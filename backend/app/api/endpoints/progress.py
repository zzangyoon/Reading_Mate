from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.core.database import DatabaseManager
from sqlalchemy import text
from datetime import datetime

router = APIRouter(tags=["progress"])

class ProgressSaveRequest(BaseModel):
    user_id: str
    book_id: int
    position: int

class ProgressResponse(BaseModel):
    user_id: str
    book_id: int
    position: int
    updated_at: str = None

@router.get("/get", response_model=ProgressResponse)
async def get_progress(user_id: str, book_id: int):
    """사용자의 책 읽기 진도 조회"""
    try:
        db_manager = DatabaseManager()

        async with db_manager.async_engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT user_id, book_id, position, updated_at
                    FROM user_progress
                    WHERE user_id = :user_id AND book_id = :book_id
                """),
                {"user_id": user_id, "book_id": book_id}
            )
            row = result.fetchone()

            if not row:
                # 진도가 없으면 1페이지부터 시작
                return ProgressResponse(
                    user_id=user_id,
                    book_id=book_id,
                    position=1
                )

            return ProgressResponse(
                user_id=row[0],
                book_id=row[1],
                position=row[2],
                updated_at=row[3].isoformat() if row[3] else None
            )

    except Exception as e:
        print(f"진도 조회 오류: {e}")
        # 에러 발생 시에도 1페이지 반환
        return ProgressResponse(
            user_id=user_id,
            book_id=book_id,
            position=1
        )

@router.post("/save")
async def save_progress(request: ProgressSaveRequest):
    """사용자의 책 읽기 진도 저장"""
    try:
        db_manager = DatabaseManager()

        async with db_manager.async_engine.begin() as conn:
            # UPSERT: 존재하면 업데이트, 없으면 삽입
            await conn.execute(
                text("""
                    INSERT INTO user_progress (user_id, book_id, position, updated_at)
                    VALUES (:user_id, :book_id, :position, :updated_at)
                    ON CONFLICT (user_id, book_id)
                    DO UPDATE SET
                        position = EXCLUDED.position,
                        updated_at = EXCLUDED.updated_at
                """),
                {
                    "user_id": request.user_id,
                    "book_id": request.book_id,
                    "position": request.position,
                    "updated_at": datetime.utcnow()
                }
            )

        return {"status": "ok", "message": "진도 저장 완료"}

    except Exception as e:
        print(f"진도 저장 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
