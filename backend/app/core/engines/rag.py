from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.vector_store import VectorStoreManager
from backend.app.prompts.rag_prompts import RAG_PROMPT
from backend.app.config import settings

class RAGEngine:
    """RAG 검색 및 답변 생성"""
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model: str = None,
        temperature: float = 0.3
    ):
        model = model or settings.LLM_MODEL
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.chain = RAG_PROMPT | self.llm | StrOutputParser()
    
    async def generate_answer(
        self,
        selected_passage: str,
        user_question: str,
        context: str,
        book_title: str,
        book_author: str
    ) -> str:
        """RAG 답변 생성"""
        return await self.chain.ainvoke({
            "context": context,
            "book_title": book_title,
            "book_author": book_author,
            "selected_passage": selected_passage,
            "user_question": user_question
        })