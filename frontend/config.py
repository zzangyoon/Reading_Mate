"""
프론트엔드 설정
"""
import os
from dataclasses import dataclass

@dataclass
class FrontendConfig:
    """프론트엔드 설정"""
    # BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    BACKEND_URL: str = "http://localhost:8003"
    
    # 테마 색상
    PRIMARY_COLOR: str = "#2E5266"      # 짙은 청록색
    SECONDARY_COLOR: str = "#6E8898"    # 연한 회색빛 청록
    ACCENT_COLOR: str = "#9FB1BC"       # 아센트 색상
    BACKGROUND_COLOR: str = "#F5F5F5"   # 배경색
    TEXT_COLOR: str = "#2C3E50"         # 텍스트 색상
    
    # PDF 설정
    PDF_DISPLAY_HEIGHT: int = 700
    
    @property
    def api_base_url(self) -> str:
        return f"{self.BACKEND_URL}/"

config = FrontendConfig()