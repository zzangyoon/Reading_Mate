"""
Vector Store 테스트
"""
import sys
from pathlib import Path

# backend 디렉토리 추가
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

# 직접 import
from app.core.database import DatabaseManager
from app.core.vector_store import VectorStoreManager

def test_vector_store():
    """Vector Store 테스트"""
    print("=== Vector Store 테스트 ===\n")
    
    # 초기화
    db_manager = DatabaseManager()
    vs_manager = VectorStoreManager(db_manager)
    
    # 하이브리드 검색 테스트
    result = vs_manager.hybrid_search(
        selected_passage="사이클론 지하실",
        user_question="왜 필요했나요?",
        k=3
    )
    
    print(f"책 제목: {result['book_title']}")
    print(f"저자: {result['book_author']}")
    print(f"\n검색 결과:\n{result['text'][:300]}...")

if __name__ == "__main__":
    test_vector_store()