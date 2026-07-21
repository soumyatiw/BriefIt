# api/database.py
#
# SQLAlchemy engine, session factory, declarative base, and FastAPI dependency.
# Import `engine`, `Base`, `SessionLocal`, and `get_db` from here — nowhere else.
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from api.config import settings

# SQLite needs a local data/ directory; PostgreSQL doesn't, but this is harmless.
os.makedirs("data", exist_ok=True)

# check_same_thread is a SQLite-only argument — don't pass it to PostgreSQL.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    # Tuned for PostgreSQL on Render's free-tier (pool_pre_ping detects stale connections).
    pool_pre_ping=True,
)

# Session factory — all DB sessions are created from this.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0-style declarative base.
    Every ORM model (Day 2 onward) must inherit from this class.
    """
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request completes (even on errors).

    Usage in a route:
        def some_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
