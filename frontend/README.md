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

## [ComfyUI 서브모듈 설치 방법]
프로젝트 루트에서 comfyUI 서브모듈을 초기화하고 최신 상태로 업데이트하려면 아래 명령어를 실행하세요

```
git clone <repo-url>
git submodule update --init --recursive
```

## [모델 파일 설치 안내]
본 프로젝트에서는 모델 파일을 제공하지 않습니다.  
아래 경로에 필요한 모델 파일을 직접 다운로드하여 위치시켜 주세요:

📁 다운로드한 파일들은 아래 경로에 각각 위치시켜 주세요:

```
ComfyUI/
├── models/
│ ├── diffusion_models/
│ │ └── flux1-krea-dev_fp8_scaled.safetensors
│ ├── text_encoders/
│ │ ├── clip_l.safetensors
│ │ └── t5xxl_fp16.safetensors
│ ├── vae/
│ │ └── ae.safetensors
│ └── loras/
│ └── pp-storybook_rank2_bf16.safetensors
```
> 💡 모델 파일은 Hugging Face, Civitai 등 공식 배포처에서 직접 다운로드해 주세요.

## 주요 기능
- 📖 PDF 뷰어
- 💬 AI 질의응답
- 📚 삽화 생성