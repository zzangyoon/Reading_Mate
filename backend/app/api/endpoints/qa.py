from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from backend.app.core.system import get_assistant_system

router = APIRouter(tags=["qa"])


class QARequest(BaseModel):
    """Q&A 요청 모델"""
    question: str
    selected_text: Optional[str] = None
    book_id: Union[str, int] = "the_wizard_of_oz"  # str과 int 둘 다 허용
    user_id: str = "default_user"


class QAResponse(BaseModel):
    """Q&A 응답 모델"""
    answer: str
    contexts: Optional[List[str]] = None
    sources: Optional[List[Dict]] = None


@router.post("/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    책 내용에 대한 질문에 답변
    
    - selected_text가 있으면 해당 텍스트를 context로 포함
    - RAG 시스템을 통해 관련 내용 검색 후 답변 생성
    """
    try:
        # 기존 ReadingAssistantSystem 활용
        assistant_system = get_assistant_system()
        
        # selected_text가 있으면 passage로 사용, 없으면 빈 문자열
        passage = request.selected_text if request.selected_text else ""
        
        answer = await assistant_system.ask(passage, request.question)
        
        return QAResponse(
            answer=answer,
            contexts=None,
            sources=None
        )
        
    except Exception as e:
        print(f"Q&A 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
