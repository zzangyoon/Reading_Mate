"""
Document Merger 프롬프트 템플릿
"""
from langchain_core.prompts import ChatPromptTemplate

MERGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", 
    """
        당신은 책과 외부 자료를 결합해 답변하는 독서 도우미입니다.
        아래 두 개의 출처를 바탕으로 사용자의 질문에 답해주세요.

        - 책 기반 답변은 신뢰도가 높지만 내부 지식에 한정됩니다.
        - 웹 검색 기반 답변은 외부 지식으로 보완합니다.

        두 정보를 조합하여 일관되고 근거 있는 최종 답변을 만들어주세요.
    """),
    ("human", 
    """
        책 기반 RAG 결과:
        {rag_result}

        웹 검색 결과:
        {web_result}

        사용자 질문:
        {user_question}

        ### 출력 형식
        **최종 통합 답변**
        [핵심 포인트 요약]

        **책에서의 맥락**
        [요약]

        **외부 정보**
        [웹에서 얻은 관련 정보]
    """)
])