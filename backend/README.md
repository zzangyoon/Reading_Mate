# Reading Assistant Backend

독서 도우미 RAG 시스템 백엔드 API

## [프로젝트 구조]

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 환경 설정
│   ├── api/                 # API 엔드포인트
│   │   ├── endpoints/
│   │   │   └── rag.py
│   │   └── router.py
│   ├── core/                # 핵심 비즈니스 로직
│   │   ├── database.py
│   │   ├── merger.py
│   │   ├── planner.py
│   │   ├── system.py
│   │   ├── vector_store.py
│   │   ├── engines/
│   │   │   ├── rag.py
│   │   │   ├── web_search.py
│   │   │   └── evaluator.py
│   ├── models/              # Pydantic 모델
│   │   ├── request.py
│   │   └── response.py
│   └── prompts/             # 프롬프트 템플릿
│       ├── rag_prompts.py
│       ├── web_prompts.py
│       ├── planner_prompts.py
│       ├── evaluator_prompts.py
│       └── merge_prompts.py
├── requirements.txt
├── .env
└── README.md
```

## [설치 및 실행]

### 1. 환경 설정

```bash
# 의존성 설치
uv pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정
```

### 2. 실행

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8003
```

### 3. API 문서 확인

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## [API 엔드포인트]

### POST /ask

독서 도우미에게 질문하기

**Request Body:**
```json
{
  "selected_passage": "구절 내용",
  "user_question": "질문 내용",
  "k": 5
}
```

**Response:**
```json
{
  "answer": "최종 통합 답변...",
  "book_title": "오즈의 마법사",
  "book_author": "L. 프랭크 바움",
  "rag_score": 0.85
}
```

## [환경 변수]

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DB_NAME | 데이터베이스 이름 | - |
| DB_USER | 데이터베이스 사용자 | - |
| DB_PASS | 데이터베이스 비밀번호 | - |
| OPENAI_API_KEY | OpenAI API 키 | - |
| COLLECTION_NAME | Vector Store 컬렉션명 | BOOK_CHUNKS |
| RAG_SCORE_THRESHOLD | RAG 재시도 기준 점수 | 0.6 |
| MAX_RETRIES | 최대 재시도 횟수 | 2 |