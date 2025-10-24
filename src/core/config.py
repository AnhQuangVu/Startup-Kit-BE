from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int
    
    APP_PORT: int = 8000
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    API_KEY: str
    BASE_URL: str
    EMBEDDING_MODEL: str
    LLM_MODEL: str
    SERPAPI_API_KEY: str

    VECTOR_DB_PATH: str
    DOCUMENTS_PATH: str
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    TOP_K_RESULTS: int

    class Config:
        env_file = ".env"
        
settings = Settings()