"""
텍스트 처리 유틸리티
"""
import re

def clean_text(text: str) -> str:
    """텍스트 정리"""
    if not text:
        return ""
    
    # 여러 줄바꿈을 하나로
    text = re.sub(r'\n+', '\n', text)
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    text = text.strip()
    return text

