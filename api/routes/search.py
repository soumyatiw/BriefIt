"""
GET /search?q=... — SQLite FTS5 full-text search over story titles + English summaries.
Falls back to a plain LIKE query if the FTS5 virtual table hasn't been created yet,
so search never hard-fails just because a migration step was missed.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.database import get_db
from api.models.story import Story

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search_stories(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    try:
        rows = db.execute(
            text("""
                SELECT s.id, s.canonical_title, s.category, s.sentiment
                FROM stories_fts f
                JOIN stories s ON s.id = f.rowid
                WHERE stories_fts MATCH :q
                LIMIT 20
            """),
            {"q": q},
        ).fetchall()
        if rows:
            return {"results": [dict(r._mapping) for r in rows], "engine": "fts5"}
    except Exception:
        pass  # FTS5 table missing or query syntax issue — fall through to LIKE search

    like_results = (
        db.query(Story)
        .filter(Story.canonical_title.ilike(f"%{q}%"))
        .limit(20)
        .all()
    )
    return {
        "results": [
            {"id": s.id, "canonical_title": s.canonical_title, "category": s.category, "sentiment": s.sentiment}
            for s in like_results
        ],
        "engine": "like_fallback",
    }
