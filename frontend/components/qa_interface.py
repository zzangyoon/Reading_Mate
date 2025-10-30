"""
질의응답 인터페이스
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api_client import APIClient
from utils.text_handler import clean_text

def render_qa_interface(api_client: APIClient):
    """질의응답 인터페이스 렌더링"""
    
    # 컨테이너로 감싸기
    st.markdown("""
        <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)
    
    st.markdown("### 💬 질문하기")
    
    # Quick Tips
    with st.expander("🎯 사용 팁", expanded=False):
        st.markdown("""
        <div style="color: #2C3E50 !important;">
        <ul style="color: #2C3E50 !important;">
            <li style="color: #2C3E50 !important;">구절 없이 질문만 입력 가능</li>
            <li style="color: #2C3E50 !important;">질문 없이 구절만 입력 가능</li>
            <li style="color: #2C3E50 !important;">둘 다 입력하면 더 정확한 답변</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 구절 입력 (세션 상태와 동기화)
    selected_passage = st.text_area(
        "📝 선택한 구절",
        height=120,
        placeholder="왼쪽 PDF에서 '텍스트 추출' 버튼을 누르거나, 직접 구절을 입력하세요...",
        key="selected_passage",
        value=st.session_state.get('selected_passage', '')
    )
    
    # 질문 입력
    user_question = st.text_input(
        "❓ 질문",
        placeholder="이 구절에 대해 궁금한 점을 질문하세요...",
        key="user_question"
    )
    
    # 버튼
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    with col_btn2:
        visualize_button = st.button("🎨 삽화로 보기", use_container_width=True)
    
    with col_btn3:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state['selected_passage'] = ""
        st.session_state['user_question'] = ""
        if 'extracted_text' in st.session_state:
            del st.session_state['extracted_text']
        st.rerun()
    
    if visualize_button:
        if not selected_passage:
            st.warning("⚠️ 삽화로 만들 구절을 먼저 입력해주세요.")
        else:
            st.info("🚧 삽화 생성 기능은 준비 중입니다. 곧 사용하실 수 있습니다!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 답변 표시 영역
    if ask_button:
        if not selected_passage and not user_question:
            st.warning("⚠️ 구절 또는 질문을 입력해주세요.")
            return
        
        # 로딩 표시
        with st.spinner("🤔 AI가 답변을 생성하고 있습니다..."):
            k_value = st.session_state.get('k_value', 5)
            
            result = api_client.ask_question(
                selected_passage=clean_text(selected_passage) if selected_passage else "",
                user_question=clean_text(user_question) if user_question else "",
                k=k_value
            )
        
        # 결과 표시
        if result['success']:
            data = result['data']
            
            st.markdown(f"""
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #E0E0E0;">
                <h3 style="margin-top:0;">✨ AI 답변</h3>
                <div style="
                    background-color: #F8F9FA;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #2E5266;
                    color: #2C3E50 !important;
                    line-height: 1.8;
                ">
                    {data['answer']}
                </div>
            """, unsafe_allow_html=True)

            # 평가 점수
            if data.get('rag_score'):
                score = data['rag_score']
                st.progress(score, text=f"신뢰도: {score*100:.0f}%")
            
            # 피드백 버튼
            st.markdown("<br>", unsafe_allow_html=True)
            col_fb1, col_fb2 = st.columns([1, 1])
            with col_fb1:
                if st.button("👍 도움됨", key="helpful", use_container_width=True):
                    st.success("피드백 감사합니다!")
            with col_fb2:
                if st.button("👎 별로", key="not_helpful", use_container_width=True):
                    st.info("피드백 감사합니다. 더 나은 답변을 제공하도록 노력하겠습니다.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            st.error(f"오류가 발생했습니다: {result['error']}")