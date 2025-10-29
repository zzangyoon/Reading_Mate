"""
RAG API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from backend.app.core.system import ReadingAssistantSystem
from backend.app.models.request import RAGRequest
from backend.app.models.response import RAGResponse, ErrorResponse

router = APIRouter()

# 시스템 초기화
assistant_system = ReadingAssistantSystem()

@router.post("/ask", response_model=RAGResponse)
async def ask_question(request: RAGRequest):
    """독서 도우미에게 질문하기"""
    try:
        answer = assistant_system.ask(
            selected_passage=request.selected_passage,
            user_question=request.user_question,
            k=request.k
        )
        
        return RAGResponse(
            answer=answer,
            book_title=None,  # 필요시 state에서 가져오기
            book_author=None,
            rag_score=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))