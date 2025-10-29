"""
환경 설정 관리
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Tavily
    TAVILY_API_KEY: str = ""
    
    # RAG Settings
    COLLECTION_NAME: str = "BOOK_CHUNKS"
    RAG_SCORE_THRESHOLD: float = 0.6
    MAX_RETRIES: int = 2
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"
    
    class Config:
        env_file = ".env"

settings = Settings()