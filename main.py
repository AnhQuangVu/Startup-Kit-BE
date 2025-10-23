from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.projects.router import router as projects_router
from src.database.core import engine, Base

import time
import logging
from sqlalchemy.exc import DatabaseError


def life_span(app: FastAPI):
    print("Starting up...")
    # Thử tạo bảng với retry/backoff để tránh lỗi khi có concurrent DDL trên MySQL
    max_attempts = 5
    delay = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            print("DB tables ensured")
            break
        except DatabaseError as e:
            logging.warning("DatabaseError during create_all attempt %s/%s: %s", attempt, max_attempts, e)
            if attempt == max_attempts:
                logging.error("Failed to run create_all after %s attempts — continuing without creating tables.", max_attempts)
                break
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            logging.exception("Unexpected error during create_all: %s", e)
            break
    yield
    print("Shutting down...")
    
app = FastAPI(
    title="Startup Investment Platform API",
    description="API for connecting startups and investors.",
    version="1.0.0",
    lifespan=life_span
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Startup Investment Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)