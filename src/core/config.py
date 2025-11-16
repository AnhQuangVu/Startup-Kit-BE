from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_DATABASE: Optional[str] = "startupkit"
    MYSQL_USER: Optional[str] = "root"
    MYSQL_PASSWORD: Optional[str] = ""
    MYSQL_PORT: Optional[int] = 3306
    
    APP_PORT: int = 8003
    DATABASE_URL: Optional[str] = "sqlite:///./startupkit.db"
    SECRET_KEY: str = "startupkit_super_secret_jwt_key_2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    API_KEY: Optional[str] = ""
    BASE_URL: Optional[str] = "https://api.openai.com/v1"
    EMBEDDING_MODEL: Optional[str] = "text-embedding-3-small"
    LLM_MODEL: Optional[str] = "gpt-4o-mini"
    SERPAPI_API_KEY: Optional[str] = ""

    VECTOR_DB_PATH: Optional[str] = "data/vector_db"
    DOCUMENTS_PATH: Optional[str] = "data/documents"
    CHUNK_SIZE: Optional[int] = 2000
    CHUNK_OVERLAP: Optional[int] = 200
    TOP_K_RESULTS: Optional[int] = 10

    class Config:
        env_file = ".env"
        extra = "ignore"
        
settings = Settings()
