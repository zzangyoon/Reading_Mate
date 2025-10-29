from sqlalchemy import create_engine, text
from backend.app.config import settings

class DatabaseManager:
    """데이터베이스 연결 및 조회 관리"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
    
    @staticmethod
    def _get_connection_string() -> str:
        """환경 변수 기반 DB 연결 문자열 생성"""
        return (
            f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    
    def get_book_metadata(self, book_id: int) -> dict:
        """책 메타데이터 조회"""
        engine = create_engine(self.connection_string)

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT title_ko, author FROM BOOKS WHERE book_id = :book_id"),
                {"book_id": book_id}
            ).fetchone()

            if not result:
                raise ValueError(f"book_id {book_id}에 해당하는 책이 없습니다.")
            
            return {
                "book_title": result[0],
                "book_author": result[1]
            }
