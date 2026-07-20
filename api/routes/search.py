"""
GET /search?q=... — SQLite FTS5 full-text search over story titles + English summaries.
Falls back to a plain LIKE query if the FTS5 virtual table hasn't been created yet,
so search never hard-fails just because a migration step was missed.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, select

from api.database import get_db
from api.models.story import Story, story_articles as sa_table
from api.models.summary import Summary
from api.models.article import Article

router = APIRouter(prefix="/search", tags=["search"])


def _enrich_stories(stories: list[Story], lang: str, db: Session) -> list[dict]:
    """Attach summary, published_at, and sources to each story — same shape as /feed."""
    results = []
    for story in stories:
        summary = (
            db.query(Summary)
            .filter(Summary.story_id == story.id, Summary.language == lang)
            .first()
        ) or (
            db.query(Summary)
            .filter(Summary.story_id == story.id, Summary.language == "en")
            .first()
        )

        member_articles = (
            db.query(Article)
            .join(sa_table, sa_table.c.article_id == Article.id)
            .filter(sa_table.c.story_id == story.id)
            .order_by(Article.published_at.desc())
            .all()
        )
        sources_list = [
            {"name": a.source.name, "url": a.url, "title": a.title}
            for a in member_articles
            if a.source
        ]
        pub_dates = [a.published_at for a in member_articles if a.published_at]
        latest_pub = max(pub_dates) if pub_dates else None

        results.append({
            "id":           story.id,
            "title":        story.canonical_title,
            "category":     story.category,
            "sentiment":    story.sentiment,
            "summary":      summary.text if summary else "",
            "language":     summary.language if summary else "en",
            "source_count": len(sources_list),
            "created_at":   story.created_at.isoformat(),
            "published_at": latest_pub.isoformat() if latest_pub else story.created_at.isoformat(),
            "sources":      sources_list,
        })
    return results


@router.get("")
def search_stories(
    q: str = Query(..., min_length=1),
    lang: str = Query("en"),
    db: Session = Depends(get_db),
):
    stories: list[Story] = []

    # Try FTS5 first
    try:
        rows = db.execute(
            text("""
                SELECT s.id
                FROM stories_fts f
                JOIN stories s ON s.id = f.rowid
                WHERE stories_fts MATCH :q
                ORDER BY rank
                LIMIT 20
            """),
            {"q": q},
        ).fetchall()
        if rows:
            ids = [r[0] for r in rows]
            # Preserve FTS rank order
            id_order = {sid: i for i, sid in enumerate(ids)}
            fetched = db.query(Story).filter(Story.id.in_(ids)).all()
            stories = sorted(fetched, key=lambda s: id_order.get(s.id, 999))
    except Exception:
        pass  # FTS5 table missing or syntax issue — fall through

    if not stories:
        stories = (
            db.query(Story)
            .filter(Story.canonical_title.ilike(f"%{q}%"))
            .limit(20)
            .all()
        )

    return {
        "results": _enrich_stories(stories, lang, db),
        "engine":  "fts5" if stories else "like_fallback",
    }
