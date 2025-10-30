# streamlit run frontend/app.py
"""
Reading Mate - Streamlit 메인 애플리케이션
"""
import streamlit as st
from pathlib import Path
from services.api_client import APIClient
from components.sidebar import render_sidebar
from components.book_viewer import render_book_viewer
from components.qa_interface import render_qa_interface
from config import config

# 페이지 설정
st.set_page_config(
    page_title="Reading Mate",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 완전히 새로 작성
st.markdown("""
<style>
    /* 전체 앱 배경 - 밝은 베이지/크림색 */
    .stApp {
        background-color: #FAF9F6 !important;
    }
    
    /* 메인 컨텐츠 영역 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
        background-color: #FAF9F6;
    }
    
    /* 모든 텍스트 색상 명시적으로 지정 */
    .stApp, .stApp * {
        color: #2C3E50 !important;
    }
    
    /* 제목 */
    h1, h2, h3, h4, h5, h6 {
        color: #2E5266 !important;
        font-weight: 600 !important;
    }
    
    /* 탭 컨테이너 */
    .stTabs {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 탭 리스트 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #F5F5F5;
        padding: 8px;
        border-radius: 10px;
    }
    
    /* 개별 탭 */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 12px 24px;
        background-color: white;
        border-radius: 8px;
        color: #2C3E50 !important;
        font-weight: 500;
        border: 2px solid transparent;
    }
    
    /* 선택된 탭 */
    .stTabs [aria-selected="true"] {
        background-color: #2E5266 !important;
        color: white !important;
        border-color: #2E5266;
    }
    
    /* 탭 내용 */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px 0;
    }
    
    /* 버튼 */
    .stButton button {
        background-color: #2E5266;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #1e3d4d;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 82, 102, 0.3);
    }
    
    /* Primary 버튼 */
    .stButton button[kind="primary"] {
        background-color: #2E5266 !important;
    }
    
    /* 입력 필드 */
    .stTextArea textarea, 
    .stTextInput input {
        background-color: white !important;
        color: #2C3E50 !important;
        border: 2px solid #E0E0E0 !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    .stTextArea textarea:focus, 
    .stTextInput input:focus {
        border-color: #2E5266 !important;
        box-shadow: 0 0 0 2px rgba(46, 82, 102, 0.1);
    }
    
    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #E0E0E0;
    }
    
    section[data-testid="stSidebar"] * {
        color: #2C3E50 !important;
    }
    
    /* 파일 업로더 */
    .stFileUploader {
        background-color: #F8F9FA;
        border: 2px dashed #2E5266;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* 슬라이더 */
    .stSlider [data-baseweb="slider"] {
        background-color: #2E5266;
    }
    
    /* 경고/정보 박스 */
    .stAlert {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid;
    }
    
    /* Success 메시지 */
    .stSuccess {
        background-color: #D4EDDA !important;
        color: #155724 !important;
        border-color: #28A745 !important;
    }
    
    /* Info 메시지 */
    .stInfo {
        background-color: #D1ECF1 !important;
        color: #0C5460 !important;
        border-color: #17A2B8 !important;
    }
    
    /* Warning 메시지 */
    .stWarning {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        border-color: #FFC107 !important;
    }
    
    /* Error 메시지 */
    .stError {
        background-color: #F8D7DA !important;
        color: #721C24 !important;
        border-color: #DC3545 !important;
    }
    
    /* 컬럼 */
    [data-testid="column"] {
        background-color: transparent;
    }
    
    /* 마크다운 텍스트 */
    .stMarkdown {
        color: #2C3E50 !important;
    }
    
    /* 코드 블록 */
    code {
        background-color: #F5F5F5 !important;
        color: #E83E8C !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'k_value' not in st.session_state:
    st.session_state['k_value'] = 5

if 'backend_checked' not in st.session_state:
    api_client = APIClient()
    st.session_state['backend_status'] = api_client.connection_check()
    st.session_state['backend_checked'] = True  # 체크 완료 표시


# API 클라이언트 초기화
api_client = APIClient()

def main():
    # 사이드바
    pdf_path = render_sidebar()
    
    # 헤더
    st.markdown("""
        <div style="text-align: center; padding: 30px 0; background: white; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h1 style="color: #2E5266 !important; font-size: 3.5em; margin-bottom: 10px; font-weight: 700;">
                📚 Reading Mate
            </h1>
            <p style="color: #6E8898 !important; font-size: 1.3em; margin: 0;">
                AI-Powered Reading Assistant
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 백엔드 연결 확인
    if not st.session_state.get('backend_status', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.warning("⚠️ 백엔드 서버와 연결할 수 없습니다.")
            st.code(f"Backend URL: {config.BACKEND_URL}", language="text")
            
            # 재연결 버튼만 체크 실행
            if st.button("🔄 다시 연결", use_container_width=True):
                st.session_state['backend_status'] = api_client.connection_check()
                st.rerun()
        return
    # if not api_client.connection_check():
    #     st.warning("⚠️ 백엔드 서버와 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    #     st.code(f"Backend URL: {config.BACKEND_URL}", language="text")
    #     return
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs([
        "📖 Reading Assistant",
        "📊 My Library",
        "⚙️ Settings"
    ])
    
    with tab1:
        if pdf_path and pdf_path.exists():
            # 두 개의 컬럼으로 분할
            col_pdf, col_qa = st.columns([1.2, 1], gap="large")
            
            with col_pdf:
                render_book_viewer(pdf_path)
            
            with col_qa:
                render_qa_interface(api_client)
        
        else:
            # PDF 없을 때 안내
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 80px 40px;
                    background: white;
                    border-radius: 20px;
                    margin: 50px auto;
                    max-width: 700px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                ">
                    <h2 style="color: #2E5266 !important; font-size: 2.5em; margin-bottom: 20px;">
                        📚 Welcome to Reading Mate!
                    </h2>
                    <p style="color: #6E8898 !important; font-size: 1.2em; line-height: 1.6; margin: 30px 0;">
                        시작하려면 왼쪽 사이드바에서<br/>PDF 파일을 업로드하세요.
                    </p>
                    <div style="margin-top: 40px; color: #2C3E50 !important;">
                        <div style="margin: 15px 0; font-size: 1.1em;">
                            <span style="color: #2E5266 !important;">✨</span> AI 기반 독서 도우미
                        </div>
                        <div style="margin: 15px 0; font-size: 1.1em;">
                            <span style="color: #2E5266 !important;">🔍</span> 스마트 질의응답
                        </div>
                        <div style="margin: 15px 0; font-size: 1.1em;">
                            <span style="color: #2E5266 !important;">📖</span> 전자책 뷰어
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📚 나의 라이브러리")
        st.info("🚧 준비 중입니다. 곧 사용하실 수 있습니다!")
    
    with tab3:
        st.markdown("### ⚙️ 설정")
        st.info("🚧 준비 중입니다. 곧 사용하실 수 있습니다!")

if __name__ == "__main__":
    main()