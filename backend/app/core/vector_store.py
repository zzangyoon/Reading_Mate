from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from backend.app.core.database import DatabaseManager
from backend.app.config import settings

class VectorStoreManager:
    """PGVector 연결 및 검색 관리"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        collection_name: str = None
    ):
        self.db_manager = db_manager
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        self.vector_store = self._get_vector_store()
    
    def _get_vector_store(self):
        """PGVector 연결"""
        return PGVector.from_existing_index(
            embedding=self.embeddings,
            collection_name=self.collection_name,
            connection_string=self.db_manager.connection_string
        )
    
    def hybrid_search(
        self,
        selected_passage: str,
        user_question: str,
        k: int = 5
    ) -> dict:
        """하이브리드 검색 (구절 + 질문)"""
        selected_passage = selected_passage.strip()
        user_question = user_question.strip()
        
        if not selected_passage and not user_question:
            raise ValueError("검색할 구절 또는 질문이 필요합니다.")
        
        # 구절로 검색
        passage_docs = []
        if selected_passage:
            passage_docs = self.vector_store.similarity_search(selected_passage, k=k)
        
        # 질문으로 검색
        question_docs = []
        if user_question:
            question_docs = self.vector_store.similarity_search(user_question, k=k)
        
        # 중복 제거
        seen_contents = set()
        unique_docs = []
        
        for doc in passage_docs + question_docs:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                unique_docs.append(doc)
        
        selected_docs = unique_docs[:k]
        
        if not selected_docs:
            return {
                "text": "관련 내용을 찾을 수 없습니다.",
                "book_title": "Unknown",
                "book_author": "Unknown"
            }
        
        # 책 메타데이터 조회
        book_id = selected_docs[0].metadata["book_id"]
        metadatas = self.db_manager.get_book_metadata(book_id)
        
        # 포맷팅
        formatted = []
        for i, doc in enumerate(selected_docs, 1):
            chapter = doc.metadata.get('chapter_name', 'Unknown')
            formatted.append(f"[구절 {i} - {chapter}]\n{doc.page_content}")
        
        return {
            "text": "\n\n".join(formatted),
            "book_title": metadatas["book_title"],
            "book_author": metadatas["book_author"]
        }