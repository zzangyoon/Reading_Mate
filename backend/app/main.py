# uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8003
"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from backend.app.core.system import ReadingAssistantSystem
from backend.app.models.request import RAGRequest

app = FastAPI(
    title="Reading Assistant API",
    description="독서 도우미 RAG 시스템 API",
    version="1.0.0"
)

@app.get("/connection_check")
async def connection_check():
    return {"status" : "200", "answer" : "ok"}

@app.post("/ask")
async def ask(req: RAGRequest):
    print("ask START !!!")
    assistant = ReadingAssistantSystem()
    answer = assistant.ask(req.selected_passage, req.user_question, req.k)
    print("answer end !!!")
    print(answer)
    return {"status" : "ok", "answer" : answer}

@app.get("/test")
async def test():
    assistant = ReadingAssistantSystem()
    answer = assistant.ask("그 집을 사이클론의 한가운데로 끌어올렸다", "여기서 사이클론이 의미하는게 뭐야?")
    print(answer)
    return {"status" : "ok", "answer" : answer}
