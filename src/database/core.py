import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./startupkit.db"

def init_engine(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    eng = create_engine(url, connect_args=connect_args)
    if not url.startswith("sqlite"):
        try:
            with eng.connect() as conn:
                pass
        except Exception as e:
            logger.warning("Could not connect to database (%s). Falling back to local SQLite.", e)
            eng = create_engine("sqlite:///./startupkit.db", connect_args={"check_same_thread": False})
    return eng

engine = init_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
