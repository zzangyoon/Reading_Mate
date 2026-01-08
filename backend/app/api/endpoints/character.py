from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.app.core.database import DatabaseManager
from backend.app.core.character_manager import get_character_manager, Character
from sqlalchemy import text
from datetime import datetime

router = APIRouter(tags=["CHARACTER"])


class CharacterListResponse(BaseModel):
    """캐릭터 목록 응답"""
    characters: List[Character]
    book_title: str
    current_page: int


class ChatRequest(BaseModel):
    """캐릭터 대화 요청"""
    user_id: str = "default_user"
    book_id: int
    character_name: str
    user_message: str
    current_page: int


class ChatResponse(BaseModel):
    """캐릭터 대화 응답"""
    response: str
    character_name: str


async def get_chunks_up_to_page(book_id: int, current_page: int) -> tuple[List[str], str]:
    """현재 페이지까지의 청크들을 조회"""
    db_manager = DatabaseManager()

    async with db_manager.async_engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT document, cmetadata
                FROM langchain_pg_embedding
                WHERE (cmetadata->>'book_id')::int = :book_id
                AND (cmetadata->>'chunk_index')::int < :chunk_index
                ORDER BY (cmetadata->>'chunk_index')::int ASC
            """),
            {"book_id": book_id, "chunk_index": current_page}
        )
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")

        chunks = [row[0] for row in rows]
        book_title = rows[0][1].get("book_title", "Unknown")

        return chunks, book_title


async def get_recent_chunks(book_id: int, current_page: int, k: int = 5) -> List[str]:
    """최근 k개의 청크 조회"""
    db_manager = DatabaseManager()

    async with db_manager.async_engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT document
                FROM langchain_pg_embedding
                WHERE (cmetadata->>'book_id')::int = :book_id
                AND (cmetadata->>'chunk_index')::int < :chunk_index
                ORDER BY (cmetadata->>'chunk_index')::int DESC
                LIMIT :k
            """),
            {"book_id": book_id, "chunk_index": current_page, "k": k}
        )
        rows = result.fetchall()

        chunks = [row[0] for row in reversed(rows)]
        return chunks


@router.get("/available", response_model=CharacterListResponse)
async def get_available_characters(book_id: int, current_page: int):
    """현재 읽은 진도에 따라 사용 가능한 캐릭터 목록 반환"""
    try:
        chunks, book_title = await get_chunks_up_to_page(book_id, current_page)
        
        character_manager = get_character_manager()
        characters = await character_manager.analyze_characters(chunks, book_title, current_page)

        return CharacterListResponse(
            characters=characters,
            book_title=book_title,
            current_page=current_page
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"캐릭터 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_chat_history(user_id: str, book_id: int, character_name: str):
    """캐릭터 대화 기록 조회"""
    try:
        db_manager = DatabaseManager()
        
        async with db_manager.async_engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT role, content, created_at
                    FROM character_chat_history
                    WHERE user_id = :user_id 
                    AND book_id = :book_id 
                    AND character_name = :character_name
                    ORDER BY created_at ASC
                """),
                {"user_id": user_id, "book_id": book_id, "character_name": character_name}
            )
            rows = result.fetchall()
            
            history = [
                {"role": row[0], "content": row[1], "created_at": row[2].isoformat()}
                for row in rows
            ]
            
            return {"history": history}
            
    except Exception as e:
        print(f"히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history")
async def clear_chat_history(user_id: str, book_id: int, character_name: str):
    """캐릭터 대화 기록 삭제"""
    try:
        db_manager = DatabaseManager()
        
        async with db_manager.async_engine.begin() as conn:
            await conn.execute(
                text("""
                    DELETE FROM character_chat_history
                    WHERE user_id = :user_id 
                    AND book_id = :book_id 
                    AND character_name = :character_name
                """),
                {"user_id": user_id, "book_id": book_id, "character_name": character_name}
            )
            
        return {"status": "ok", "message": "대화 기록 삭제 완료"}
        
    except Exception as e:
        print(f"히스토리 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_with_character(request: ChatRequest):
    """캐릭터와 대화"""
    try:
        db_manager = DatabaseManager()

        # 1. 이전 대화 기록 조회
        async with db_manager.async_engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT role, content
                    FROM character_chat_history
                    WHERE user_id = :user_id 
                    AND book_id = :book_id 
                    AND character_name = :character_name
                    ORDER BY created_at ASC
                    LIMIT 20
                """),
                {"user_id": request.user_id, "book_id": request.book_id, "character_name": request.character_name}
            )
            rows = result.fetchall()
            history = [{"role": row[0], "content": row[1]} for row in rows]

        # 2. 최근 청크 조회
        recent_chunks = await get_recent_chunks(request.book_id, request.current_page, k=5)

        if not recent_chunks:
            raise HTTPException(status_code=404, detail="책 내용을 찾을 수 없습니다.")

        # 3. LLM 호출 (히스토리 포함)
        character_manager = get_character_manager()
        response_text = await character_manager.chat_as_character(
            request.character_name,
            request.user_message,
            recent_chunks,
            history = history
        )

        # 4. 대화 기록 저장 (사용자 + 어시스턴트)
        async with db_manager.async_engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO character_chat_history (user_id, book_id, character_name, role, content, created_at)
                    VALUES 
                        (:user_id, :book_id, :character_name, 'user', :user_msg, :now),
                        (:user_id, :book_id, :character_name, 'assistant', :assistant_msg, :now)
                """),
                {
                    "user_id": request.user_id,
                    "book_id": request.book_id,
                    "character_name": request.character_name,
                    "user_msg": request.user_message,
                    "assistant_msg": response_text,
                    "now": datetime.utcnow()
                }
            )

        return ChatResponse(
            response=response_text,
            character_name=request.character_name
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"캐릭터 대화 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))