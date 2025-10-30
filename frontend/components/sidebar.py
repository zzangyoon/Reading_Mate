"""
사이드바 컴포넌트
"""
import streamlit as st
from pathlib import Path
from typing import Optional

def render_sidebar() -> Optional[Path]:
    """사이드바 렌더링"""
    with st.sidebar:
        st.markdown("""
            <h2 style="color: #2E5266 !important; text-align: center; margin-bottom: 30px;">
                📚 Reading Mate
            </h2>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 책 선택
        st.markdown("### 📖 책 선택")
        
        # 업로드된 PDF 파일
        uploaded_file = st.file_uploader(
            "PDF 파일 업로드",
            type=['pdf'],
            help="읽고 싶은 책의 PDF 파일을 업로드하세요"
        )
        
        if uploaded_file:
            # 임시 저장
            pdf_path = Path("temp") / uploaded_file.name
            pdf_path.parent.mkdir(exist_ok=True)
            
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.success(f"✅ {uploaded_file.name} 로드 완료")
            return pdf_path
        
        st.markdown("---")
        
        # 설정 - 주석 처리
        # st.markdown("### ⚙️ 설정")
        # k_value = st.slider(
        #     "검색 문서 개수",
        #     min_value=1,
        #     max_value=20,
        #     value=5,
        #     help="관련 구절을 몇 개나 검색할지 선택하세요"
        # )
        
        # st.session_state['k_value'] = k_value
        
        # 기본값 설정
        if 'k_value' not in st.session_state:
            st.session_state['k_value'] = 5
        
        # st.markdown("---")
        
        # 도움말
        with st.expander("❓ 사용 방법"):
            st.markdown("""
            <div style="color: #2C3E50 !important;">
            <ol style="color: #2C3E50 !important; line-height: 1.8;">
                <li style="color: #2C3E50 !important;"><strong>PDF 업로드</strong>: 읽고 싶은 책을 업로드하세요</li>
                <li style="color: #2C3E50 !important;"><strong>텍스트 추출</strong>: 궁금한 구절을 드래그로 선택해서 복사/붙여넣기 하세요</li>
                <li style="color: #2C3E50 !important;"><strong>질문 입력</strong>: 질문을 입력하고 Ask 버튼을 누르세요</li>
                <li style="color: #2C3E50 !important;"><strong>답변 확인</strong>: AI가 책 내용과 외부 지식을 결합하여 답변합니다</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
        
        return None