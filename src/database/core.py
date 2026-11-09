import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "startupkit.db").replace("\\", "/")
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

RAW_DB_URL = os.getenv("DATABASE_URL")
if RAW_DB_URL and RAW_DB_URL.strip():
    DATABASE_URL = RAW_DB_URL.strip()
else:
    DATABASE_URL = DEFAULT_SQLITE_URL

def init_engine(url: str):
    if not url or not str(url).strip():
        url = DEFAULT_SQLITE_URL
    
    try:
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        eng = create_engine(url, connect_args=connect_args)
        if not url.startswith("sqlite"):
            with eng.connect() as conn:
                pass
        return eng
    except Exception as e:
        logger.warning("Could not initialize configured database (%s). Falling back to local SQLite.", e)
        return create_engine(DEFAULT_SQLITE_URL, connect_args={"check_same_thread": False})

engine = init_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
