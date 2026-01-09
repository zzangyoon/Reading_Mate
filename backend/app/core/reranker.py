"""
Cross-Encoder 기반 Reranker
"""
from sentence_transformers import CrossEncoder
from typing import List
from langchain.schema import Document


class Reranker:
    """검색 결과 재정렬을 위한 Cross-Encoder Reranker"""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model = CrossEncoder(model_name, max_length=512)
    
    def rerank(
        self, 
        query: str, 
        documents: List[Document], 
        top_k: int = 5
    ) -> List[Document]:
        """문서들을 query와의 관련성으로 재정렬"""
        if not documents:
            return []
        
        # (query, document) 쌍 생성
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Cross-Encoder로 점수 계산
        scores = self.model.predict(pairs)
        
        # 점수순 정렬
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in doc_score_pairs[:top_k]]


# 싱글톤 패턴
_reranker = None

def get_reranker() -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker
