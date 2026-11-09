import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

load_dotenv()
RAW_DB_URL = os.getenv("DATABASE_URL")
DATABASE_URL = RAW_DB_URL if (RAW_DB_URL and RAW_DB_URL.strip()) else "sqlite:///./startupkit.db"

def init_engine(url: str):
    if not url or not str(url).strip():
        url = "sqlite:///./startupkit.db"
    
    try:
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        eng = create_engine(url, connect_args=connect_args)
        if not url.startswith("sqlite"):
            with eng.connect() as conn:
                pass
        return eng
    except Exception as e:
        logger.warning("Could not initialize configured database (%s). Falling back to local SQLite.", e)
        return create_engine("sqlite:///./startupkit.db", connect_args={"check_same_thread": False})

engine = init_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
