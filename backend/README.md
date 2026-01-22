# Reading Assistant Backend

독서 도우미 RAG 시스템 백엔드 API

## 1. 핵심 기술

### LangGraph 워크플로우

```text
Planner → RAG Engine ←→ Evaluator (재시도)
        → Web Search
               ↓
            Merger → 최종 답변
```

### Rerank (2-Stage Retrieval)

1. Embedding 검색: k*3개 후보 추출
2. Cross-Encoder Rerank: 상위 k개 선별

### Self-Evaluation

- Relevance, Completeness, Accuracy 평가
- 점수 < 0.6 시 최대 2회 재시도

## 2. 프로젝트 구조

```text
backend/
├── app/
│   ├── main.py                 # FastAPI 앱
│   ├── config.py               # 환경 설정
│   ├── api/                    # API 엔드포인트
│   │   ├── endpoints/
│   │   │   ├── rag.py          # Q&A API
│   │   │   ├── character.py    # 캐릭터 API
│   │   │   ├── books.py        # 책 데이터 API
│   │   │   └── progress.py     # 진행률 API
│   │   └── router.py
│   ├── core/                   # 핵심 비즈니스 로직
│   │   ├── system.py           # LangGraph 워크플로우
│   │   ├── vector_store.py     # Hybrid Search + Rerank
│   │   ├── reranker.py         # Cross-Encoder Reranker
│   │   ├── character_manager.py # 캐릭터 분석/대화
│   │   ├── database.py         # DB 연결 관리
│   │   ├── planner.py          # 질문 분석
│   │   ├── merger.py           # 결과 통합
│   │   └── engines/
│   │       ├── rag.py          # RAG 답변 생성
│   │       ├── web_search.py   # Tavily 웹 검색
│   │       └── evaluator.py    # 품질 평가
│   ├── models/                 # Pydantic 모델
│   │   ├── request.py
│   │   └── response.py
│   └── prompts/                # 프롬프트 템플릿
│       ├── rag_prompts.py
│       ├── web_prompts.py
│       ├── planner_prompts.py
│       ├── evaluator_prompts.py
│       ├── merge_prompts.py
│       └── character_prompts.py
├── requirements.txt
└── .env
```

## 3. API 엔드포인트

### Q&A

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /ask | 독서 도우미에게 질문 |

**Request:**

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
  "answer": "최종 통합 답변",
  "book_title": "오즈의 마법사",
  "book_author": "L. 프랭크 바움",
  "rag_score": 0.85
}
```

### Character

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /character/list | 캐릭터 목록 조회 |
| POST | /character/chat | 캐릭터 대화 |
| GET | /character/history | 대화 히스토리 조회 |
| DELETE | /character/history | 대화 히스토리 삭제 |

### Book

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /book/{book_id}/chunks | 총 청크 개수 조회 |
| GET | /book/{book_id}/chunk/{chunk_id} | 특정 청크 조회 |

### Image

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /generate | 삽화 생성 |
| GET | /images/{filename} | 생성된 이미지 조회 |

## 4. 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DB_NAME | 데이터베이스 이름 | - |
| DB_USER | 데이터베이스 사용자 | - |
| DB_PASS | 데이터베이스 비밀번호 | - |
| DB_HOST | 데이터베이스 호스트 | localhost |
| DB_PORT | 데이터베이스 포트 | 5432 |
| OPENAI_API_KEY | OpenAI API 키 | - |
| TAVILY_API_KEY | Tavily API 키 | - |
| COLLECTION_NAME | Vector Store 컬렉션명 | BOOK_CHUNKS |
| RAG_SCORE_THRESHOLD | RAG 재시도 기준 점수 | 0.6 |
| MAX_RETRIES | 최대 재시도 횟수 | 2 |
| LANGCHAIN_TRACING_V2 | LangSmith 트레이싱 | false |
| LANGCHAIN_API_KEY | LangSmith API 키 | - |
| LANGCHAIN_PROJECT | LangSmith 프로젝트명 | - |

## 5. 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```
```bash
pip install sentence-transformers
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

### 3. 실행

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8003
```

### 4. API 문서

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

