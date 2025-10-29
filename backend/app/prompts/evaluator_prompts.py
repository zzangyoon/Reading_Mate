"""
RAG Evaluator 프롬프트 템플릿
"""
from langchain_core.prompts import ChatPromptTemplate

EVALUATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", 
    """
        당신은 RAG 시스템의 품질 평가자입니다.

        다음 기준으로 답변을 평가하세요:
        1. Relevance (관련성): 질문과 답변이 얼마나 관련있는가? (0-10)
        2. Completeness (완전성): 답변이 질문을 충분히 다루는가? (0-10)
        3. Accuracy (정확성): 제공된 컨텍스트와 일치하는가? (0-10)

        JSON 형식으로 답변하세요:
        {{
            "relevance": 8,
            "completeness": 7,
            "accuracy": 9,
            "total_score": 8.0,
            "reasoning": "..."
        }}
    """),
    ("human", 
    """
        질문: {question}

        컨텍스트:
        {context}

        답변:
        {answer}
    """)
])