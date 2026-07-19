"""
scripts/reset_db.py
Wipes all content data (articles, stories, summaries, interactions)
while preserving sources and users.
Run once before a fresh pipeline start.
"""
import sys
import os

# Make sure we can import the project packages
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import api.models  # noqa: F401 — registers all models
from api.database import Base, engine
from sqlalchemy import text


TABLES_TO_CLEAR = [
    "summaries",
    "story_articles",
    "stories",
    "articles",
    "interactions",
]


def main():
    print("=== BriefIt DB Reset ===")
    confirm = input(
        "This will DELETE all articles, stories, summaries, and interactions "
        "(sources and users are kept). Type YES to continue: "
    )
    if confirm.strip() != "YES":
        print("Aborted.")
        return

    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in TABLES_TO_CLEAR:
            conn.execute(text(f"DELETE FROM {table}"))
            print(f"  cleared: {table}")
        conn.execute(text("PRAGMA foreign_keys = ON"))

        # Re-create FTS5 virtual table (safe to DROP + recreate since content is gone)
        conn.execute(text("DROP TABLE IF EXISTS stories_fts"))
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS stories_fts
            USING fts5(canonical_title, content='stories', content_rowid='id')
        """))
        print("  re-created: stories_fts")

        conn.commit()

    print("\nDone. DB is clean — restart uvicorn to trigger a fresh pipeline run.")


if __name__ == "__main__":
    main()
