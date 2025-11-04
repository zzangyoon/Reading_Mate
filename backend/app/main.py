# uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8003
"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from backend.app.core.system import get_assistant_system
from backend.app.models.request import RAGRequest
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from fastapi.responses import FileResponse
from backend.app.api.router import api_router
import yaml

from vector_search import VectorSearchEngine
from prompt_generator import PromptGenerator
from comfyui_client import ComfyUIClient

from contextlib import asynccontextmanager

services = {}
sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    print("앱 시작: DB 연결 준비")
    print("서비스 시작 중...")
    
    # 설정 파일 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 서비스 초기화
    services['vector_search'] = VectorSearchEngine(
        db_path=config['vector_db']['path'],
        collection_name=config['vector_db']['collection'],
        embedding_model=config['vector_db']['embedding_model']
    )
    
    services['prompt_generator'] = PromptGenerator()
    
    services['comfyui_client'] = ComfyUIClient(
        server_address=config['comfyui_server']
    )
    
    print("서비스 초기화 완료!")
    yield
    # 종료 시
    print("앱 종료: DB 연결 해제")
    assistant_system = get_assistant_system()
    await assistant_system.db_manager.close()


# ===== 요청/응답 모델 =====
class GenerationRequest(BaseModel):
    """이미지 생성 요청"""
    user_input: str
    book_id: str = "the_wizard_of_oz"
    steps: Optional[int] = 20
    cfg_scale: Optional[float] = 1.0
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    lora_strength: Optional[float] = 0.8

app = FastAPI(
    title="Reading Assistant API",
    description="독서 도우미 RAG 시스템 API",
    version="1.0.0",
    lifespan = lifespan
)

app.include_router(api_router)

@app.get("/connection_check")
async def connection_check():
    return {"status" : "200", "answer" : "ok"}

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    """
    이미지 생성 API
    
    워크플로우:
    1. 벡터 검색 → 관련 문장 추출
    2. 프롬프트 생성 → 캐릭터 외형/키워드 번역
    3. ComfyUI 이미지 생성
    """
    try:
        print(f"입력: {request.user_input}")
        
        # 1. 벡터 검색
        print("벡터 DB 검색 중...")
        context = services['vector_search'].search_relevant_content(
            query=request.user_input,
            top_k=5
        )
        print(f"!!! {len(context)}개 관련 문장 찾음")
        
        # 2. 프롬프트 생성
        print("\n프롬프트 생성 중...")
        prompt_data = services['prompt_generator'].generate_comfyui_prompt(
            context=context,
            user_input=request.user_input,
            book_context=request.book_id
        )
        
        # 워크플로우 파라미터 추가
        prompt_data['style_params'].update({
            "steps": request.steps,
            "cfg_scale": request.cfg_scale,
            "width": request.width,
            "height": request.height,
            "lora_strength": request.lora_strength,
        })
        
        print(f"프롬프트 생성 완료")
        
        # 3. 이미지 생성
        print("\nComfyUI 이미지 생성 중...")
        result = services['comfyui_client'].generate_image(
            prompt_data=prompt_data
        )
        
        print(f"이미지 생성 완료!")
        print(f"image_url : /images/{Path(result['image_path']).name}")
        
        
        return {"image_url" : f"/images/{Path(result['image_path']).name}"}
    
    except Exception as e:
        print(f"\n오류 ::: {e}")
        

@app.get("/images/{filename}")
async def get_image(filename: str):
    """생성된 이미지 파일 반환"""
    image_path = Path("generated_images") / filename
    
    if not image_path.exists():
        return {"status_code":404, "detail":"이미지 없음"}
    
    return FileResponse(image_path)

# @app.get("/test")
# async def test():
#     assistant = ReadingAssistantSystem()
#     answer = assistant.ask("그 집을 사이클론의 한가운데로 끌어올렸다", "여기서 사이클론이 의미하는게 뭐야?")
#     print(answer)
#     return {"status" : "ok", "answer" : answer}
