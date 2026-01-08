"""
캐릭터 관련 프롬프트 템플릿
"""
from langchain_core.prompts import ChatPromptTemplate

CHARACTER_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("human", """다음은 "{book_title}"의 1페이지부터 {current_page}페이지까지의 내용입니다.

{full_text}

위 내용에서 등장한 모든 주요 캐릭터를 분석하세요.

각 캐릭터마다 다음 정보를 JSON 형식으로 제공:
1. name: 캐릭터 이름
2. traits: 핵심 성격 특성 (간결하게, 10단어 이내)
3. role: 현재 시점에서의 역할 (간결하게, 10단어 이내)
4. notable_behavior: 주목할 만한 대사나 행동 (선택사항, 20단어 이내)

중요: 이미 등장한 캐릭터만 포함하세요.

JSON 배열로만 응답하세요. 다른 설명은 넣지 마세요.
형식:
[
  {{"name": "캐릭터1", "traits": "특성", "role": "역할", "notable_behavior": "행동"}},
  {{"name": "캐릭터2", "traits": "특성", "role": "역할"}}
]""")
])


CHARACTER_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 "{character_name}"입니다.

다음은 최근 이야기 내용입니다:
{context}

위 내용을 바탕으로, {character_name}의 성격과 현재 상황을 이해하고, 그 캐릭터로서 자연스럽게 대화하세요.

중요:
- {character_name}의 어투와 성격을 유지하세요
- 현재 이야기 시점의 {character_name}로서 대답하세요
- 앞으로 일어날 일은 알 수 없습니다 (스포일러 방지)
- 자연스럽고 친근하게 대화하세요
- 한국어로 대답하세요"""),
    ("human", "{user_message}")
])
