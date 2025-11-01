"""
RAG API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from backend.app.core.system import get_assistant_system
from backend.app.models.request import RAGRequest
from backend.app.models.response import RAGResponse, ErrorResponse

router = APIRouter()

# 시스템 초기화
# assistant_system = ReadingAssistantSystem()

@router.post("/ask", response_model=RAGResponse)
async def ask_question(req: RAGRequest):
    """독서 도우미에게 질문하기"""
    print("router !!! rag/ask")
    try:
        assistant_system = get_assistant_system()
        answer = await assistant_system.ask(
            selected_passage=req.selected_passage,
            user_question=req.user_question,
            k=req.k
        )
        
        return RAGResponse(
            answer=answer,
            book_title=None,  # 필요시 state에서 가져오기
            book_author=None,
            rag_score=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))