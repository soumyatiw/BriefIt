# api/database.py
#
# SQLAlchemy engine, session factory, declarative base, and FastAPI dependency.
# Import `engine`, `Base`, `SessionLocal`, and `get_db` from here — nowhere else.
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from api.config import settings

# Ensure the data/ directory exists before SQLite tries to create the file.
os.makedirs("data", exist_ok=True)

# SQLite requires check_same_thread=False when used with FastAPI's threaded
# request handling (multiple threads may share the same connection).
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
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
