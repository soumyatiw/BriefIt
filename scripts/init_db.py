import api.models  # noqa: F401 — registers all models on Base.metadata
from api.database import Base, engine
from sqlalchemy import text


def main() -> None:
    Base.metadata.create_all(bind=engine)
    tables = list(Base.metadata.tables.keys())
    print(f"Tables created: {', '.join(sorted(tables))}")

    # Create FTS5 virtual table for full-text search over story titles.
    # Uses SQLite's built-in FTS5 module — content table keeps data in sync.
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS stories_fts
            USING fts5(canonical_title, content='stories', content_rowid='id')
        """))
        conn.commit()
    print("FTS5 virtual table 'stories_fts' ensured.")


if __name__ == "__main__":
    main()
