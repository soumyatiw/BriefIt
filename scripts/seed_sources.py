import json
from pathlib import Path

from api.database import SessionLocal
from api.models.source import Source

SOURCES_FILE = Path(__file__).parent.parent / "ai_engine" / "ingestion" / "sources.json"


def seed():
    sources = json.loads(SOURCES_FILE.read_text())
    db = SessionLocal()
    inserted = updated = 0

    try:
        for entry in sources:
            existing = db.query(Source).filter(Source.url == entry["url"]).first()
            if existing:
                existing.name = entry["name"]
                existing.type = entry["type"]
                existing.category = entry["category"]
                existing.language = entry["language"]
                updated += 1
            else:
                db.add(Source(**entry))
                inserted += 1
        db.commit()
    finally:
        db.close()

    print(f"Sources seeded — inserted: {inserted}, updated: {updated}")


if __name__ == "__main__":
    seed()
