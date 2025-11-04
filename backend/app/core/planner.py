import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.prompts.planner_prompts import PLANNER_PROMPT
from backend.app.config import settings

class Planner:
    """질문 분석 및 실행 계획 수립"""
    
    def __init__(self, model: str = None, temperature: float = 0):
        model = model or "gpt-4o-mini"
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.chain = PLANNER_PROMPT | self.llm | StrOutputParser()
    
    async def analyze(self, selected_passage: str, user_question: str) -> dict:
        """질문 분석"""
        plan_str = await self.chain.ainvoke({
            "selected_passage": selected_passage,
            "user_question": user_question
        })
        
        try:
            plan = json.loads(plan_str)
        except:
            # 파싱 실패시 기본값
            plan = {
                "need_rag": True,
                "need_web": True,
                "question_type": "contextual",
                "complexity": "medium",
                "reasoning": "Default plan"
            }
        
        return plan