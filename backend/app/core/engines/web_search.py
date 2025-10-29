from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_tavily import TavilySearch
from backend.app.prompts.web_prompts import WEB_SEARCH_PROMPT

class WebSearchEngine:
    """웹 검색 엔진"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.tools = [TavilySearch()]
    
    def search(
        self,
        selected_passage: str,
        user_question: str,
        book_title: str = "Unknown",
        book_author: str = "Unknown"
    ) -> str:
        """웹 검색 실행"""
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=WEB_SEARCH_PROMPT
        )
        # print(f"search ::: book_title ::: {book_title}, book_author ::: {book_author}")
        
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True
        )
        
        result = executor.invoke({
            "selected_passage": selected_passage,
            "user_question": user_question,
            "book_title": book_title,
            "book_author": book_author
        })
        
        return result.get("output", "")