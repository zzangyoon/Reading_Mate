import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.prompts.evaluator_prompts import EVALUATOR_PROMPT

class RAGEvaluator:
    """RAG 결과 품질 평가"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.chain = EVALUATOR_PROMPT | self.llm | StrOutputParser()
    
    async def evaluate(self, question: str, context: str, answer: str) -> float:
        """RAG 결과 평가 (0-1 스케일)"""
        eval_str = await self.chain.ainvoke({
            "question": question,
            "context": context,
            "answer": answer
        })
        
        try:
            eval_result = json.loads(eval_str)
            score = eval_result.get("total_score", 5.0) / 10.0
        except:
            score = 0.7
        
        return score