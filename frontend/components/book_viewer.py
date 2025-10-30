"""
책 뷰어 컴포넌트
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pdf_handler import load_pdf_as_base64
from config import config

def render_book_viewer(pdf_path: Path):
    """책 뷰어 렌더링"""
    
    # PDF를 base64로 인코딩
    pdf_base64 = load_pdf_as_base64(pdf_path)
    
    if not pdf_base64:
        st.error("PDF 파일을 로드할 수 없습니다.")
        return
    
    # 컨테이너
    st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)
    
    st.markdown("### 📖 책 내용")
    
    # 진행도 표시
    current_progress = st.session_state.get('reading_progress', 0)
    st.progress(current_progress / 100, text=f"📊 독서 진행도: {current_progress:.1f}%")
    
    # 기본 PDF 뷰어 (가장 안정적)
    pdf_viewer_html = f"""
    <style>
        .pdf-viewer-container {{
            border: 2px solid #E0E0E0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background: white;
            margin: 10px 0;
        }}
        .pdf-viewer-container iframe {{
            border: none;
            width: 100%;
            height: {config.PDF_DISPLAY_HEIGHT}px;
        }}
    </style>
    <div class="pdf-viewer-container">
        <iframe 
            src="data:application/pdf;base64,{pdf_base64}" 
            type="application/pdf">
        </iframe>
    </div>
    """
    
    st.markdown(pdf_viewer_html, unsafe_allow_html=True)
    
    # 사용 안내
    st.info("""
    💡 **Tip**: 
    - PDF를 스크롤하며 읽으세요
    - 궁금한 구절을 **드래그로 선택 → Ctrl+C 복사**
    - 오른쪽 '선택한 구절' 입력창에 **Ctrl+V 붙여넣기**
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)