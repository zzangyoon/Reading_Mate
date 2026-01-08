"""
캐릭터 분석 및 대화 관리
"""
from openai import AsyncOpenAI
from typing import List, Optional
from pydantic import BaseModel
import os
import json
from backend.app.prompts.character_prompts import (
    CHARACTER_ANALYSIS_PROMPT,
    CHARACTER_CHAT_PROMPT
)


class Character(BaseModel):
    """캐릭터 정보 모델"""
    name: str
    traits: str
    role: str
    notable_behavior: Optional[str] = None


class CharacterManager:
    """캐릭터 분석 및 대화 엔진"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def analyze_characters(
        self,
        chunks: List[str],
        book_title: str,
        current_page: int
    ) -> List[Character]:
        """LLM을 사용하여 등장 캐릭터 분석"""
        
        # 전체 텍스트 결합 (너무 길면 앞부분만)
        full_text = "\n\n".join(chunks)
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "..."

        # 프롬프트 생성 (LangChain 템플릿 사용)
        messages = CHARACTER_ANALYSIS_PROMPT.format_messages(
            book_title=book_title,
            current_page=current_page,
            full_text=full_text
        )
        
        # LangChain 메시지를 OpenAI 형식으로 변환
        role_mapping = {"human": "user", "ai": "assistant", "system": "system"}
        openai_messages = [
            {"role": role_mapping.get(msg.type, msg.type), "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=2000
        )

        response_text = response.choices[0].message.content

        try:
            characters_data = json.loads(response_text)
            characters = [Character(**char) for char in characters_data]
            return characters
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답: {response_text}")
            raise ValueError("캐릭터 분석 결과 파싱 실패")

    async def chat_as_character(
        self,
        character_name: str,
        user_message: str,
        recent_chunks: List[str],
        history: List[dict] = None
    ) -> str:
        """캐릭터로서 대화 생성"""
        
        context = "\n\n".join(recent_chunks)

        # 프롬프트 생성 (LangChain 템플릿 사용)
        messages = CHARACTER_CHAT_PROMPT.format_messages(
            character_name=character_name,
            context=context,
            user_message=user_message
        )
        
        # LangChain 메시지를 OpenAI 형식으로 변환
        role_mapping = {"human": "user", "ai": "assistant", "system": "system"}
        openai_messages = [
            {"role": role_mapping.get(msg.type, msg.type), "content": msg.content}
            for msg in messages
        ]

        # 히스토리 삽입 (system 메시지 뒤, 현재 user 메시지 앞)
        if history:
            # system 메시지 분리
            system_msg = openai_messages[0]         # system
            current_user_msg = openai_messages[1]   # 현재 user 메시지

            # 히스토리 + 현재 메시지 조합
            openai_messages = [system_msg] + history + [current_user_msg]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.8,
            max_tokens=1000
        )

        return response.choices[0].message.content


_character_manager = None

def get_character_manager():
    """CharacterManager 싱글톤 인스턴스 반환"""
    global _character_manager
    if _character_manager is None:
        _character_manager = CharacterManager()
    return _character_manager
