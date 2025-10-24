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
    
    api_key: str
    base_url: str
    embedding_model: str
    llm_model: str
    serpapi_api_key: str
    
    vector_db_path: str
    documents_path: str
    chunk_size: int
    chunk_overlap: int
    top_k_results: int

    class Config:
        env_file = ".env"
        
settings = Settings()