"""
백엔드 API 클라이언트
"""
import requests
from typing import Dict
from config import config

from pydantic import BaseModel, Field

class RAGRequest(BaseModel):
    """RAG 질문 요청"""
    selected_passage: str = Field(..., description="사용자가 선택한 책 구절")
    user_question: str = Field(..., description="사용자의 질문")
    k: int = Field(default=5, description="검색할 문서 개수", ge=1, le=20)

class APIClient:
    """백엔드 API 클라이언트"""
    
    def __init__(self):
        self.base_url = config.api_base_url
    
    def ask_question(
        self,
        selected_passage: str,
        user_question: str,
        k: int = 5
    ) -> Dict:
        """RAG 질문 요청"""
        req_json = {
                    "selected_passage": selected_passage,
                    "user_question": user_question,
                    "k": k
                }
        print(f"selected_passage ::: {selected_passage} /// user_question ::: {user_question} /// k ::: {k}")
    
        try:
            response = requests.post(
                f"{self.base_url}ask",
                json=req_json,
                timeout=60
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
        
    def connection_check(self) -> bool:
        """백엔드 연결 확인"""
        try:
            response = requests.get(f"{config.BACKEND_URL}/connection_check", timeout=5)
            return response.status_code == 200
        except:
            return False
        
    def save_progress(
        self,
        book_id: int,
        progress: float,
        current_page: int
    ) -> Dict:
        """독서 진행도 저장"""
        try:
            response = requests.post(
                f"{self.base_url}/progress/save",
                json={
                    "book_id": book_id,
                    "progress": progress,
                    "current_page": current_page
                },
                timeout=5
            )
            response.raise_for_status()
            return {"success": True}
        except:
            return {"success": False}

    def get_progress(self, book_id: int) -> Dict:
        """독서 진행도 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/progress/get/{book_id}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except:
            return {"progress": 0, "current_page": 1}