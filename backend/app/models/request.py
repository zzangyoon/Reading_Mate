"""
API 요청 모델
"""
from pydantic import BaseModel, Field

class RAGRequest(BaseModel):
    """RAG 질문 요청"""
    selected_passage: str = Field(..., description="사용자가 선택한 책 구절")
    user_question: str = Field(..., description="사용자의 질문")
    k: int = Field(default=5, description="검색할 문서 개수", ge=1, le=20)

class BookSearchRequest(BaseModel):
    """책 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    k: int = Field(default=10, description="검색 결과 개수", ge=1, le=50)