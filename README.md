# Reading Mate

LangGraph 기반 Multi-Agent RAG 시스템으로 구현한 AI 독서 도우미

## 프로젝트 소개

독서 중 발생하는 궁금증을 즉시 해결하고, 책 속 캐릭터와 대화하며 몰입감을 높이는 AI 어시스턴트입니다.

### 해결하고자 한 문제

| 문제 | 해결 방법 |
|------|----------|
| 독서 중단 (검색하느라 흐름 끊김) | 책 맥락 기반 즉시 답변 |
| 스포일러 위험 | 현재 페이지까지만 참조 |
| 낮은 몰입감 | 캐릭터 페르소나 대화 |

## 시스템 아키텍처

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                  (Vanilla JS + HTML/CSS)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
├──────────────────┬──────────────────┬───────────────────────┤
│   Q&A Agent      │  Character Agent │  Image Agent          │
│   (LangGraph)    │  (Persona Chat)  │  (ComfyUI)            │
└──────────────────┴──────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL + pgvector │ OpenAI │ Tavily │ LangSmith        │
└─────────────────────────────────────────────────────────────┘
```

## 주요 기능

### 1. Q&A Agent
- **Hybrid Search**: 선택 구절 + 질문 병렬 검색
- **Cross-Encoder Rerank**: 2-Stage Retrieval로 검색 품질 향상
- **Self-Evaluation**: 품질 점수 < 0.6 시 자동 재시도

### 2. Character Agent
- 책 속 캐릭터 자동 분석 및 추출
- 캐릭터 페르소나 대화 (스포일러 방지)
- 대화 히스토리 DB 저장

### 3. Image Agent
- ComfyUI + FLUX 모델 기반 삽화 생성
- 책 맥락 기반 프롬프트 자동 생성

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | FastAPI |
| Workflow | LangGraph |
| Vector DB | PostgreSQL + pgvector |
| Embedding | text-embedding-3-small |
| Rerank | bge-reranker-v2-m3 |
| LLM | GPT-4o / GPT-4o-mini |
| Web Search | Tavily API |
| Monitoring | LangSmith |

## 프로젝트 구조

```text
Reading_Mate/
├── backend/                 # 백엔드 API (상세: backend/README.md)
├── frontend/                # 프론트엔드 (상세: frontend/README.md)
├── ComfyUI/                 # 이미지 생성 (서브모듈)
└── config.yaml
```

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/zzangyoon/Reading_Mate.git
cd Reading_Mate
git submodule update --init --recursive
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```text
# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password

# API Keys
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=reading-mate
```

### 3. 실행

```bash
# Backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8003

# Frontend
cd frontend
python -m http.server 8080
```

### 4. 접속

- Frontend: http://localhost:8080
- API Docs: http://localhost:8003/docs

## 상세 문서

- [Backend README](backend/README.md) - API 엔드포인트, 환경 변수 상세
- [Frontend README](frontend/README.md) - 실행 방법, ComfyUI 설정
