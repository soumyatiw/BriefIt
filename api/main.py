import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.database import engine
from api.routes import auth, feed, stories, search, interactions
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="BriefIt API", lifespan=lifespan)

env_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in env_origins.split(",") if o.strip()]

# Forcefully append safe defaults if they are missing
for default_origin in ["http://localhost:5173", "https://briefit-ai.vercel.app"]:
    if default_origin not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(default_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(stories.router)
app.include_router(search.router)
app.include_router(interactions.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to BriefIt API"}


@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "db_connected": db_ok}
