"""
API 응답 모델
"""
from pydantic import BaseModel
from typing import Optional

class RAGResponse(BaseModel):
    """RAG 질문 응답"""
    answer: str
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    rag_score: Optional[float] = None

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    detail: Optional[str] = None