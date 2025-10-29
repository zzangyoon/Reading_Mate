"""
Web Search 프롬프트 템플릿
"""
from langchain_core.prompts import ChatPromptTemplate

WEB_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", 
    """
        당신은 친절하고 깊이 있는 독서 도우미입니다.
        사용자가 제공한 구절에 대해 툴을 사용해서 답변해 주세요.
        책 본문에 명시되지 않은 내용은 "책 본문 내 명시는 없지만…"으로 표시해 주세요.
    """),
    ("human", 
    """
        현재 사용자는 다음 책을 읽고 있습니다:
        - 책 제목: {book_title}
        - 저자: {book_author}

        아래는 사용자가 선택한 구절입니다:
        "{selected_passage}"

        사용자의 질문:
        "{user_question}"
    """),
    ("placeholder", "{agent_scratchpad}")
])