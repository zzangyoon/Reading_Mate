"""
전자책 벡터 검색 엔진
- Chroma 벡터 DB 기반 유사 문장 검색
- 자동 키워드 추출 (긴 문장 입력 시)
"""
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()


class VectorSearchEngine:
    def __init__(
        self, 
        db_path: str = "./99_vectorstore/e_book_db",
        collection_name: str = "the_wizard_of_oz",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        벡터 검색 엔진 초기화
        
        Args:
            db_path: Chroma DB 저장 경로
            collection_name: 컬렉션 이름
            embedding_model: OpenAI 임베딩 모델
        """
        self.embedding = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embedding,
            collection_name=collection_name
        )
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_keywords(self, text: str) -> str:
        """
        긴 문장에서 핵심 키워드 자동 추출
        
        Args:
            text: 원본 문장
            
        Returns:
            추출된 핵심 키워드
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"""다음 문장에서 검색에 유용한 핵심 키워드만 추출하세요.

문장: {text}

규칙:
- 명사, 동사, 고유명사 중심
- 5-10개 키워드
- 불필요한 조사, 부사 제외
- 공백으로 구분

키워드만 출력:"""
                }],
                temperature=0.3
            )
            
            keywords = response.choices[0].message.content.strip()
            print(f"🔍 추출된 키워드: {keywords}")
            return keywords
            
        except Exception as e:
            print(f"⚠️ 키워드 추출 실패: {e}, 원문 사용")
            return text
    
    def search_relevant_content(
        self, 
        query: str, 
        top_k: int = 5,
        auto_extract_keywords: bool = True
    ) -> List[Dict]:
        """
        유사 문장 검색
        
        Args:
            query: 검색할 키워드/문장
            top_k: 반환할 문장 개수
            auto_extract_keywords: 긴 문장 시 자동 키워드 추출
            
        Returns:
            관련 문장 리스트 (score 포함)
        """
        # 긴 문장인 경우 키워드 추출
        search_query = query
        if auto_extract_keywords and len(query) > 50:
            search_query = self.extract_keywords(query)
        
        # 유사도 검색
        results = self.vectorstore.similarity_search_with_score(
            query=search_query,
            k=top_k
        )
        
        # 결과 포맷팅 (거리 → 유사도 변환)
        formatted_results = []
        for doc, distance in results:
            similarity_score = 1 / (1 + distance)
            
            formatted_results.append({
                "text": doc.page_content,
                "score": similarity_score,
                "metadata": doc.metadata
            })
        
        return formatted_results
    
    def count_documents(self) -> int:
        """저장된 문서 개수 반환"""
        return self.vectorstore._collection.count()