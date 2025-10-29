"""
API 라우터 통합
"""
from fastapi import APIRouter
from backend.app.api.endpoints import rag

api_router = APIRouter()

api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])