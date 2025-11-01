from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from backend.app.config import settings
from typing import Dict, Optional

class DatabaseManager:
    """데이터베이스 연결 및 조회 관리"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
        self.async_connection_string = self._get_async_connection_string()
        self._async_engine: Optional[AsyncEngine] = None

    def _get_connection_string(self) -> str:
        """환경 변수 기반 DB 연결 문자열 생성"""
        return (
            f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    
    def _get_async_connection_string(self) -> str:
        """비동기 DB 연결 문자열 생성 (asyncpg 사용)"""
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    
    @property
    def async_engine(self) -> AsyncEngine:
        """비동기 엔진 (싱글톤)"""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.async_connection_string,
                echo=True,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
        return self._async_engine
    
    async def get_book_metadata(self, book_id: int) -> dict:
        """책 메타데이터 조회"""
        print("get_book_metadata !!!")

        async with self.async_engine.connect() as conn:
            print("db - 연결 성공, 쿼리 실행")
            result = await conn.execute(
                text("SELECT title_ko, author FROM BOOKS WHERE book_id = :book_id"),
                {"book_id": book_id}
            )
            print("db 3")

            row = result.fetchone()

            print("db row ::: ", row)

            if not row:
                raise ValueError(f"book_id {book_id}에 해당하는 책이 없습니다.")
            
            return {
                "book_title": row[0],
                "book_author": row[1]
            }
        
    async def close(self):
        """비동기 엔진 종료 (앱 종료 시 호출)"""
        if self._async_engine:
            await self._async_engine.dispose()
