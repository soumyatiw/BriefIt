from api.database import engine
from sqlalchemy import text

print("Dropping all tables to reset schema for pgvector...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS story_articles CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS interactions CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS articles CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS summaries CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS stories CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS sources CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    conn.commit()
print("Success! You can now run python -m scripts.init_db")
