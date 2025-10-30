# Reading Mate Frontend

AI 기반 독서 도우미 프론트엔드

## 프로젝트 구조

```
frontend/
├── app.py                # 메인 애플리케이션
├── config.py             # 설정
├── services/
│   └── api_client.py     # API 클라이언트
├── components/
│   ├── sidebar.py        # 사이드바
│   ├── book_viewer.py    # 책 뷰어
│   └── qa_interface.py   # 질의응답 UI
├── utils/
│   ├── pdf_handler.py    # PDF 처리
│   └── text_handler.py   # 텍스트 처리
├── requirements.txt
└── .env
```

## [실행 방법]

```bash
# Streamlit 실행
streamlit run frontend/app.py
```

## 주요 기능
- 📖 PDF 뷰어
- 💬 AI 질의응답
- 📚 삽화 생성 (준비중)