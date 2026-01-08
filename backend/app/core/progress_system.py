from typing import Optional
from backend.app.core.database import DatabaseManager
from backend.app.agents.summarizer import Summarizer

class ProgressSystem:
    """독서 진행도 관리 시스템"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.summarizer = Summarizer()
    
    async def save_progress(
        self,
        user_id: int,
        book_id: int,
        position: int
    ) -> bool:
        """독서 진행도 저장"""
        return await self.db_manager.save_reading_progress(
            user_id, book_id, position
        )
    
    async def get_progress(
        self,
        user_id: int,
        book_id: int
    ) -> Optional[int]:
        """독서 진행도 조회"""
        return await self.db_manager.get_reading_progress(user_id, book_id)
    
    async def get_summary(
        self,
        user_id: int,
        book_id: int,
        start_position: int,
        end_position: int
    ) -> str:
        """읽은 구간 요약"""
        # DB에서 텍스트 추출
        text = await self.db_manager.get_text_by_range(
            book_id, start_position, end_position
        )
        
        if not text:
            return "해당 구간의 내용을 찾을 수 없습니다."
        
        # LLM으로 요약
        summary = await self.summarizer.summarize(text)
        return summary


# 싱글톤 인스턴스
_progress_system = None

def get_progress_system() -> ProgressSystem:
    """진행도 시스템 싱글톤 반환"""
    global _progress_system
    if _progress_system is None:
        _progress_system = ProgressSystem()
    return _progress_system