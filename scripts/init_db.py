import os

import api.models  # noqa: F401 — registers all models on Base.metadata
from api.database import Base, engine
from sqlalchemy import text


def main() -> None:
    Base.metadata.create_all(bind=engine)
    tables = list(Base.metadata.tables.keys())
    print(f"Tables created: {', '.join(sorted(tables))}")

    database_url = os.getenv("DATABASE_URL", "sqlite://")

    if database_url.startswith("sqlite"):
        # SQLite: create FTS5 virtual table for full-text search.
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS stories_fts
                USING fts5(canonical_title, content='stories', content_rowid='id')
            """))
            conn.commit()
        print("SQLite FTS5 table 'stories_fts' ensured.")
    else:
        # PostgreSQL: add a tsvector column + GIN index on the stories table.
        # This powers the full-text search in api/routes/search.py.
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE stories
                ADD COLUMN IF NOT EXISTS search_vector tsvector
                    GENERATED ALWAYS AS (
                        to_tsvector('english', coalesce(canonical_title, ''))
                    ) STORED;
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS stories_search_vector_idx
                ON stories USING GIN (search_vector);
            """))
            conn.commit()
        print("PostgreSQL GIN full-text index on 'stories.search_vector' ensured.")


if __name__ == "__main__":
    main()
