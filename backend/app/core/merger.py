from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.prompts.merge_prompts import MERGE_PROMPT
from backend.app.config import settings

class DocumentMerger:
    """RAG + Web Search 결과 통합"""
    
    def __init__(self, model: str = None, temperature: float = 0.3):
        model = model or settings.LLM_MODEL
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.chain = MERGE_PROMPT | self.llm | StrOutputParser()
    
    def merge(self, rag_result: str, web_result: str, user_question: str) -> str:
        """결과 통합"""
        return self.chain.invoke({
            "rag_result": rag_result,
            "web_result": web_result,
            "user_question": user_question
        })