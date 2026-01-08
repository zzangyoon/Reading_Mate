from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.app.core.database import DatabaseManager
from sqlalchemy import text

router = APIRouter(tags=["books"])

class BookInfo(BaseModel):
    """책 정보 모델"""
    book_id: int
    title_ko: str
    author: str
    is_novel: bool
    genre: Optional[str] = None

@router.get("/list", response_model=List[BookInfo])
async def get_books_list():
    """
    서버에 저장된 책 목록 조회
    """
    try:
        db_manager = DatabaseManager()
        
        async with db_manager.async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT book_id, title_ko, author, is_novel, genre FROM BOOKS")
            )
            rows = result.fetchall()
            
            books = []
            for row in rows:
                books.append(BookInfo(
                    book_id=row[0],
                    title_ko=row[1],
                    author=row[2],
                    is_novel=row[3],
                    genre=row[4]
                ))
            
            return books
            
    except Exception as e:
        print(f"책 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
