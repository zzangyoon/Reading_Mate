"""
AI 프롬프트 생성기
- 캐릭터 외형 자동 추출
- 한영 키워드 번역
- 가중치 적용 프롬프트 구조화
"""
from typing import Dict, List
from openai import OpenAI
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()


class PromptGenerator:
    def __init__(self):
        """OpenAI API 클라이언트 초기화"""
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.translation_model = "gpt-4o"
    
    def _is_sentence_input(self, user_input: str) -> bool:
        """입력이 문장인지 키워드 나열인지 판단"""
        # 쉼표가 있으면 키워드
        if ',' in user_input:
            return False
        
        # 한국어 문법 요소가 있으면 문장
        korean_grammar = r'[은는이가을를에와과](?:\s|$)|[다고하](?:\s|$)'
        if re.search(korean_grammar, user_input):
            return True
        
        # 3단어 이하면 키워드
        if len(user_input.split()) <= 3:
            return False
        
        return True
    
    def _search_keyword_translation(
        self, 
        keyword: str, 
        context: List[Dict],
        book_context: str = ""
    ) -> Dict:
        """
        단일 키워드의 정확한 영문 표기 검색
        
        Args:
            keyword: 한글 키워드
            context: 책 내용 컨텍스트
            book_context: 책 제목/힌트
            
        Returns:
            번역 결과 딕셔너리
        """
        context_text = "\n".join([c['text'] for c in context[:5]])
        
        prompt = f"""당신은 문학 작품의 고유명사를 정확하게 영문으로 번역하는 전문가입니다.

<키워드>
{keyword}
</키워드>

<책_내용_참고>
{context_text}
</책_내용_참고>

<책_정보>
{book_context if book_context else "정보 없음"}
</책_정보>

**작업:**
1. 이 키워드가 캐릭터명/장소명/물건명인지 파악
2. <책_내용_참고>에 영문 표기가 있으면 그것을 사용
3. 없으면 정확한 영문 번역 제공
4. 유명 작품의 경우 공식 영문명 사용

**중요:**
- 캐릭터 이름은 절대 임의 번역 금지 (예: 도로시 → Dorothy, NOT Dorosi)
- 유명 작품의 경우 원작 영문명 사용 필수

JSON 형식:
{{
    "korean": "도로시",
    "english": "Dorothy Gale",
    "type": "character",
    "confidence": 0.95,
    "reasoning": "오즈의 마법사 주인공, 공식 영문명 Dorothy Gale"
}}

type 값: "character" (인물), "place" (장소), "object" (물건), "general" (일반명사)
confidence: 0.0~1.0 (확신도)
"""

        try:
            response = self.client.chat.completions.create(
                model=self.translation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["source"] = "gpt"
            return result
            
        except Exception as e:
            return {
                "korean": keyword,
                "english": keyword,
                "type": "general",
                "confidence": 0.3,
                "source": "fallback",
                "error": str(e)
            }
    
    def _search_and_translate_keywords(
        self, 
        keywords: str, 
        context: List[Dict],
        book_context: str = ""
    ) -> Dict[str, Dict]:
        """쉼표로 구분된 키워드들을 모두 검색하여 영문 번역"""
        keyword_list = [k.strip() for k in keywords.split(',')]
        translations = {}
        
        for keyword in keyword_list:
            if not keyword:
                continue
                
            translation_result = self._search_keyword_translation(
                keyword, 
                context, 
                book_context
            )
            
            translations[keyword] = {
                "english": translation_result["english"],
                "type": translation_result["type"],
                "confidence": translation_result["confidence"],
                "source": translation_result["source"]
            }
        
        return translations
    
    def _extract_scene_from_keywords(
        self, 
        keywords: str, 
        context: List[Dict]
    ) -> str:
        """키워드를 포함하는 책 내용 문장을 추출"""
        keyword_list = [k.strip() for k in keywords.split(',')]
        
        best_match = None
        max_match_count = 0
        
        for ctx in context[:5]:
            text = ctx['text']
            match_count = sum(1 for kw in keyword_list if kw in text)
            
            if match_count > max_match_count:
                max_match_count = match_count
                best_match = text
        
        if best_match and max_match_count >= 2:
            return best_match
        else:
            return keywords
    
    def _detect_main_characters(self, user_input: str, context: List[Dict]) -> List[str]:
        """사용자 입력과 context에서 주요 캐릭터 감지"""
        context_text = "\n".join([c['text'] for c in context[:3]])
        
        prompt = f"""다음 텍스트에서 등장하는 캐릭터 이름을 모두 찾아주세요.

<사용자_입력>
{user_input}
</사용자_입력>

<책_내용>
{context_text}
</책_내용>

**규칙:**
- 사람/동물/생명체 이름만 추출 (장소명 제외)
- 고유명사만 (일반명사 제외)
- 한국어 이름 그대로 반환

JSON 형식:
{{
    "characters": ["캐릭터1", "캐릭터2"]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("characters", [])
        except:
            return []
    
    def _extract_character_appearance(
        self, 
        character_name: str, 
        context: List[Dict]
    ) -> Dict:
        """context에서 특정 캐릭터의 외형 묘사만 추출"""
        context_text = "\n".join([c['text'] for c in context[:5]])
        
        prompt = f"""다음 텍스트에서 '{character_name}'의 외형 묘사만 추출하세요.

<텍스트>
{context_text}
</텍스트>

**추출 대상:**
- 나이/연령대 (매우 중요!)
- 성별 (매우 중요!)
- 머리 스타일 및 색상
- 옷차림 (색상, 스타일, 특징)
- 키/체형
- 얼굴 특징
- 특별한 외형적 특징 (모자, 안경, 액세서리 등)

**제외 대상:**
- 성격, 행동, 감정
- 대사나 말투
- 다른 캐릭터와의 관계

**중요:**
- 텍스트에 명시된 정보만 사용
- 추측하지 말 것
- 영어로 간결하게 나열 (쉼표로 구분)

JSON 형식:
{{
    "appearance": "young girl, braided brown hair with blue ribbons, bright blue gingham dress, ruby slippers",
    "age_group": "child" 또는 "teen" 또는 "adult" 또는 "elderly",
    "gender": "male" 또는 "female" 또는 "unknown",
    "confidence": 0.8
}}

만약 외형 정보가 없으면:
{{
    "appearance": "",
    "age_group": "unknown",
    "gender": "unknown",
    "confidence": 0.0
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "appearance": result.get("appearance", ""),
                "age_group": result.get("age_group", "unknown"),
                "gender": result.get("gender", "unknown"),
                "confidence": result.get("confidence", 0.0)
            }
        except:
            return {
                "appearance": "",
                "age_group": "unknown",
                "gender": "unknown",
                "confidence": 0.0
            }
    
    def _identify_interfering_subjects(
        self,
        main_character: str,
        context: List[Dict]
    ) -> List[str]:
        """
        단독 이미지 생성 시 배제해야 할 주체 식별
        (다른 캐릭터, 적대자, 부정적 배경)
        """
        context_text = "\n".join([c['text'] for c in context[:5]])
        
        prompt = f"""다음 텍스트에서 '{main_character}'의 단독 이미지 생성 시 배제해야 할 요소를 식별하세요.

<텍스트>
{context_text}
</텍스트>

**식별 대상:**
1. '{main_character}'의 주요 적대자나 위협 요소
2. '{main_character}'의 단독 이미지를 만들 때 등장하면 안 되는 다른 캐릭터 (동료 포함)
3. 부정적이거나 무서운 분위기를 만드는 존재

JSON 형식:
{{
    "interfering_subjects": [
        {{"korean": "날개 달린 원숭이", "english": "flying monkeys"}},
        {{"korean": "사악한 마녀", "english": "wicked witch"}}
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            subjects = result.get("interfering_subjects", [])
            return [s["english"] for s in subjects]
        except:
            return []
    
    def generate_comfyui_prompt(
        self, 
        context: List[Dict],
        user_input: str,
        style_preference: str = "Children's book illustration style, Bright and cheerful colors, Warm and gentle lighting, Soft and rounded edges, Friendly atmosphere, Kawaii, adorable, highly detailed illustration",
        book_context: str = ""
    ) -> Dict:
        """
        ComfyUI용 구조화된 프롬프트 생성
        
        Args:
            context: 벡터 검색 결과
            user_input: 사용자 입력
            style_preference: 스타일 선호도
            book_context: 책 컨텍스트
            
        Returns:
            프롬프트 딕셔너리 (positive, style_params, _debug)
        """
        # 입력 타입 판단
        is_sentence = self._is_sentence_input(user_input)
        
        # 키워드 영문 번역 (키워드 모드일 때만)
        keyword_translations = {}
        if not is_sentence:
            keyword_translations = self._search_and_translate_keywords(
                user_input, 
                context,
                book_context
            )
        
        # 키워드 입력인 경우 책 내용에서 문장 추출
        if not is_sentence:
            scene_description = self._extract_scene_from_keywords(user_input, context)
            input_type = "키워드"
        else:
            scene_description = user_input
            input_type = "문장"
        
        # 캐릭터 감지
        characters = self._detect_main_characters(user_input, context)
        
        # 각 캐릭터의 외형 정보 추출
        character_appearances = {}
        for char in characters:
            appearance_data = self._extract_character_appearance(char, context)
            if appearance_data["confidence"] > 0.5:
                character_appearances[char] = appearance_data
        
        # 주요 캐릭터 결정
        main_character = characters[0] if characters else None
        
        # 방해 요소 식별 (단독 이미지인 경우)
        interfering_subjects = []
        is_solo_request = len(characters) == 1 or "혼자" in user_input.lower() or "단독" in user_input.lower()
        
        if is_solo_request and main_character:
            interfering_subjects = self._identify_interfering_subjects(main_character, context)
            
            # 다른 캐릭터도 방해 요소에 추가
            main_char_eng = ""
            for k, v in keyword_translations.items():
                if k == main_character:
                    main_char_eng = v['english']
                    break
            
            for k, v in keyword_translations.items():
                if v['type'] == 'character' and v['english'] != main_char_eng:
                    if v['english'] not in interfering_subjects:
                        interfering_subjects.append(v['english'])
        
        # 컨텍스트 정리
        context_text = "\n".join([
            f"[장면 {i+1}] {c['text']} (점수: {c['score']:.2f})"
            for i, c in enumerate(context[:3])
        ])
        
        # 캐릭터 외형 정보 텍스트
        character_info_text = ""
        if character_appearances:
            character_info_text = "\n\n<캐릭터_외형_정보>\n"
            for char, appearance_data in character_appearances.items():
                character_info_text += f"{char}:\n"
                character_info_text += f"  - 외형: {appearance_data['appearance']}\n"
                character_info_text += f"  - 나이: {appearance_data['age_group']}\n"
                character_info_text += f"  - 성별: {appearance_data['gender']}\n"
            character_info_text += "</캐릭터_외형_정보>"
        
        # 키워드 번역 정보
        translation_info_text = ""
        if keyword_translations:
            translation_info_text = "\n\n<키워드_영문_번역>\n"
            for korean, trans_data in keyword_translations.items():
                translation_info_text += f"{korean} → {trans_data['english']} (타입: {trans_data['type']}, 확신도: {trans_data['confidence']:.2f})\n"
            translation_info_text += "\n**중요: 위 영문 번역을 반드시 사용하고, 캐릭터 고유명사에 가중치를 부여하세요.**\n"
            translation_info_text += "</키워드_영문_번역>"
        
        # Positive 약화 키워드
        weakening_text = ""
        if interfering_subjects:
            weakening_text = " (" + ", ".join([f"({s}:-1.0)" for s in set(interfering_subjects)]) + ")"
        
        # 프롬프트 생성
        prompt_template = f"""당신은 전자책 독서 경험을 향상시키도록 돕는 이미지 생성 삽화 전문가입니다.

<책_내용_참고>
{context_text}
</책_내용_참고>
{character_info_text}
{translation_info_text}

<사용자_입력>
{scene_description}
</사용자_입력>

<스타일>
{style_preference}
</스타일>

**절대적 규칙:**

1. **캐릭터 고유명사 및 외형 가중치 극대화:**
   - **가장 높은 가중치 (2.0~1.7)를 고유명사 및 연령/성별에 부여**
   - **고유명사 전략:** '(((The canonical character [Name]:2.0)))' 형태로 모델 편향을 강력하게 제어
   - **나이별 프롬프트:**
     * elderly: "(((elderly:1.8))), (((old man/woman:1.7))), ((aged:1.6))"
     * adult: "(((adult:1.7))), (((mature:1.6))), grown-up"
     * teen: "(((teenager:1.8))), (((adolescent:1.7)))"
     * child: "(((child:1.9))), (((young:1.8))), kid"

2. **Positive 약화 전략 (Negative 대체):**
   - 단독 이미지 시 다른 캐릭터/위협 요소를 {weakening_text} 형태로 프롬프트 맨 끝에 배치

3. **장면 및 스타일 충실 변환:**
   - <사용자_입력>과 <스타일>을 충실하게 반영하여 영문 프롬프트 작성

4. **구도 명시:**
   - "medium shot", "upper body shot", "cowboy shot" 중 하나 반드시 명시

5. **단독 이미지 처리:**
   - 단독 이미지 요청 시 "single character focus, solo character" 추가

6. **품질 키워드 필수:**
   - "masterpiece, best quality, highly detailed, professional illustration, bright and cheerful, daylight, vibrant colors, children's book style"

**프롬프트 구조:**
1. 나이/성별 극대화 키워드 (가중치 2.0~1.7)
2. 역할 명시
3. (((The canonical character [고유명사]:2.0)))
4. 상세 외형 묘사 (핵심 속성에 가중치 1.4~1.6)
5. 장면 행동 및 배경
6. 단독 이미지 키워드 (해당시)
7. 구도
8. 품질 키워드
9. Positive 약화 키워드 ((요소:-1.0) 형태, 맨 끝)

**예시:**
"(((child:1.9))), (((young girl:1.8))), (((female:1.7))), (((The canonical character Dorothy Gale:2.0))), ((cheerful girl:1.6)), ((braided brown hair with blue ribbons:1.5)), ((bright blue gingham dress:1.4)), ruby slippers, walking happily in a bright green field, full body shot, masterpiece, best quality (scarecrow:-1.0), (tin man:-1.0)"

다음 JSON 형식으로 반환:
{{
    "positive": "영어 프롬프트",
    "style_params": {{
        "cfg_scale": 1.0,
        "steps": 20,
        "sampler": "euler"
    }}
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.translation_model,
                messages=[{"role": "user", "content": prompt_template}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
        except Exception as e:
            result = {
                "positive": "error generating prompt",
                "style_params": {
                    "cfg_scale": 1.0,
                    "steps": 20,
                    "sampler": "euler"
                },
                "_error": str(e)
            }
        
        # Flux 최적 기본값 설정
        result.setdefault("style_params", {})
        result["style_params"].setdefault("cfg_scale", 1.0)
        result["style_params"].setdefault("steps", 20)
        result["style_params"].setdefault("sampler", "euler")
        
        # 디버깅 정보
        result["_debug"] = {
            "input_type": input_type,
            "original_input": user_input,
            "scene_used": scene_description,
            "detected_characters": characters,
            "character_appearances": character_appearances,
            "main_character": main_character,
            "interfering_subjects": interfering_subjects,
            "is_solo_request": is_solo_request,
            "keyword_translations": keyword_translations if keyword_translations else None
        }
        
        return result
    