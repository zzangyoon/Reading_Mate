from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from backend.app.core.database import DatabaseManager
from backend.app.core.vector_store import VectorStoreManager
from backend.app.core.planner import Planner
from backend.app.core.merger import DocumentMerger
from backend.app.core.engines import evaluator, rag, web_search
from backend.app.config import settings

def debug_reducer(old, new):
    """State update 동기화 error 해결용 reducer"""
    
    if new is not None:
        # 문자열인 경우
        if isinstance(new, str):
            if new != "" and new != "Unknown":
                return new
        # 숫자인 경우
        elif isinstance(new, (int, float)):
            return new
        # dict인 경우
        elif isinstance(new, dict):
            if new:  # 빈 dict가 아니면
                return new
        # 기타
        else:
            return new
    
    # new가 없으면 old 유지
    return old if old is not None else new

class GraphState(TypedDict):
    """LangGraph State"""
    # selected_passage: str
    selected_passage: Annotated[str, debug_reducer]
    user_question: Annotated[str, debug_reducer]
    k: Annotated[int, debug_reducer]
    book_title: Annotated[str, debug_reducer]
    book_author: Annotated[str, debug_reducer]  
    plan: Annotated[dict, debug_reducer]
    rag_result: Annotated[str, debug_reducer]
    rag_score: float
    rag_context: Annotated[str, debug_reducer]
    web_result: Annotated[str, debug_reducer]
    final_answer: Annotated[str, debug_reducer]
    retry_count: Annotated[int, debug_reducer]


class ReadingAssistantSystem:
    """독서 도우미 통합 시스템"""
    
    def __init__(
        self,
        collection_name: str = None,
        rag_score_threshold: float = None,
        max_retries: int = None
    ):
        # 초기화
        self.db_manager = DatabaseManager()
        self.vector_store_manager = VectorStoreManager(
            self.db_manager,
            collection_name or settings.COLLECTION_NAME
        )
        self.planner = Planner()
        self.rag_engine = rag.RAGEngine(self.vector_store_manager)
        self.rag_evaluator = evaluator.RAGEvaluator()
        self.web_search_engine = web_search.WebSearchEngine()
        self.document_merger = DocumentMerger()
        
        # 설정
        self.rag_score_threshold = rag_score_threshold or settings.RAG_SCORE_THRESHOLD
        self.max_retries = max_retries or settings.MAX_RETRIES
        
        # LangGraph 생성
        self.graph = self._create_graph()
    
    async def _planner_node(self, state: GraphState) -> GraphState:
        """Planner 노드"""
        print("\n=== PLANNER NODE ===")
        print(f"state ::: {state}")
        plan = await self.planner.analyze(
            state["selected_passage"],
            state["user_question"]
        )
        print(f"Plan: {plan}")
        state["plan"] = plan

        # 하이브리드 검색
        hybrid_result = await self.vector_store_manager.hybrid_search(
            state["selected_passage"],
            state["user_question"],
            state.get("k", 5)
        )
        
        state["book_title"] = hybrid_result["book_title"]
        state["book_author"] = hybrid_result["book_author"]
        state["rag_context"] = hybrid_result["text"]

        print(f"return state ::: {state}")
        return state
    
    async def _rag_node(self, state: GraphState) -> GraphState:
        """RAG 노드"""
        print("\n=== RAG NODE ===")
        print(f"state ::: {state}")
        
        if not state.get("plan", {}).get("need_rag", True):
            print("RAG 스킵 (Planner 판단)")
            state["rag_result"] = "RAG 검색 불필요"
            state["rag_score"] = 1.0
            state["book_title"] = "Unknown"
            state["book_author"] = "Unknown"
            return state
        
        # # 하이브리드 검색
        # hybrid_result = self.vector_store_manager.hybrid_search(
        #     state["selected_passage"],
        #     state["user_question"],
        #     state.get("k", 5)
        # )
        
        # state["book_title"] = hybrid_result["book_title"]
        # state["book_author"] = hybrid_result["book_author"]
        # state["rag_context"] = hybrid_result["text"]

        print(f"책 정보: {state['book_title']} - {state['book_author']}")
        
        # RAG 답변 생성
        result = await self.rag_engine.generate_answer(
            state["selected_passage"],
            state["user_question"],
            state["rag_context"],
            state["book_title"],
            state["book_author"]
        )
        
        state["rag_result"] = result
        print(f"RAG 결과 생성 완료 (길이: {len(result)})")
        print(f"return state ::: {state}")
        
        return state
    
    async def _web_search_node(self, state: GraphState) -> GraphState:
        """Web Search 노드"""
        print("\n=== WEB SEARCH NODE ===")
        print(f"state ::: {state}")
        
        if not state.get("plan", {}).get("need_web", True):
            print("Web Search 스킵 (Planner 판단)")
            state["web_result"] = "웹 검색 불필요"
            return state
        
        book_title = state.get("book_title", "Unknown")
        book_author = state.get("book_author", "Unknown")

        print(f"사용할 책 정보: {book_title} - {book_author}")
        
        result = await self.web_search_engine.search(
            state["selected_passage"],
            state["user_question"],
            # state.get("book_title", "Unknown"),
            # state.get("book_author", "Unknown")
            book_title,
            book_author
        )
        
        state["web_result"] = result
        print(f"Web Search 결과 생성 완료 (길이: {len(result)})")
        
        return state
    
    async def _evaluate_node(self, state: GraphState) -> GraphState:
        """RAG 평가 노드"""
        print("\n=== RAG EVALUATION NODE ===")
        print(f"state ::: {state}")
        
        score = await self.rag_evaluator.evaluate(
            state["user_question"],
            state.get("rag_context", ""),
            state.get("rag_result", "")
        )
        
        state["rag_score"] = score
        print(f"RAG 평가 점수: {score:.2f}")
        
        return state
    
    async def _merge_node(self, state: GraphState) -> GraphState:
        """문서 통합 노드"""
        print("\n=== DOC GRADER NODE (MERGE) ===")
        print(f"state ::: {state}")
        
        final_answer = await self.document_merger.merge(
            state.get("rag_result", ""),
            state.get("web_result", ""),
            state["user_question"]
        )
        
        state["final_answer"] = final_answer
        print("최종 답변 생성 완료")
        
        return state
    
    def _after_rag(self, state: GraphState) -> Literal["evaluate", "merge"]:
        """RAG 실행 후 다음 노드 결정"""
        if not state.get("plan", {}).get("need_rag", True):
            print("RAG 스킵 -> 평가 생략, 바로 merge로 이동")
            return "merge"
        return "evaluate"

    def _rag_retry(self, state: GraphState) -> Literal["rag", "merge"]:
        """RAG 재시도 여부 결정"""
        score = state.get("rag_score", 1.0)
        retry_count = state.get("retry_count", 0)
        
        if score < self.rag_score_threshold and retry_count < self.max_retries:
            print(f"\n RAG 점수 낮음 ({score:.2f}), 재시도 {retry_count + 1}회")
            state["retry_count"] = retry_count + 1
            return "rag"
        else:
            return "merge"
    
    def _create_graph(self):
        """LangGraph 워크플로우 생성"""
        workflow = StateGraph(GraphState)
        
        # 노드 추가
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("evaluate", self._evaluate_node)
        workflow.add_node("merge", self._merge_node)
        
        # 엣지 설정
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "rag")
        workflow.add_edge("planner", "web_search")
        # workflow.add_edge("rag", "evaluate")
        workflow.add_conditional_edges(
            "rag",
            self._after_rag,
            {
                "evaluate": "evaluate",
                "merge": "merge"
            }
        )
        workflow.add_conditional_edges(
            "evaluate",
            self._rag_retry,
            {
                "rag": "rag",
                "merge": "merge"
            }
        )
        workflow.add_edge("web_search", "merge")
        workflow.add_edge("merge", END)

        graph = workflow.compile()
        print(graph)
        
        return workflow.compile()
    
    async def ask(
        self,
        selected_passage: str,
        user_question: str,
        k: int = 5
    ) -> str:
        """독서 도우미에게 질문하기"""
        initial_state = {
            "selected_passage": selected_passage,
            "user_question": user_question,
            "k": k,
            "retry_count": 0,
            "book_title": None,
            "book_author": None,
            "final_answer": None
        }

        print(f"selected_passage::: {selected_passage}, user_question ::: {user_question}")
        
        result = await self.graph.ainvoke(initial_state)
        return result["final_answer"]
    
_assistant_system = None

def get_assistant_system():
    global _assistant_system
    if _assistant_system is None:
        _assistant_system = ReadingAssistantSystem()
    return _assistant_system