from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.projects.router import router as projects_router, public_router
from src.ai.router import router as ai_router
from src.database.core import engine, Base

import time
import logging
from sqlalchemy.exc import DatabaseError


def life_span(app: FastAPI):
    print("Starting up...")
    Base.metadata.create_all(bind=engine)
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
app.include_router(ai_router)
app.include_router(public_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Startup Investment Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)