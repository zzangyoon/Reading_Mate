"""
API 라우터 통합
"""
from fastapi import APIRouter
from backend.app.api.endpoints import rag, qa, books, progress, character

api_router = APIRouter()

api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(qa.router, prefix="/qa", tags=["QA"])
api_router.include_router(books.router, prefix="/books", tags=["BOOKS"])
api_router.include_router(progress.router, prefix="/progress", tags=["PROGRESS"])
api_router.include_router(character.router, prefix="/character", tags=["CHARACTER"])