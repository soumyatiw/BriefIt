"""
GET /feed?lang=en&category=technology
Returns stories that have at least one English summary (i.e. have been processed
by the pipeline). Filters out unsummarized stories so the feed never shows blanks.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.story import Story, story_articles as sa_table
from api.models.summary import Summary
from api.security import get_current_user_id_optional

router = APIRouter(prefix="/feed", tags=["feed"])

VALID_LANGS = {"en", "hi", "ta", "te"}


@router.get("")
def get_feed(
    lang: str = Query("en"),
    category: str | None = Query(None),
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id_optional),  # feed works logged-out too
):
    if lang not in VALID_LANGS:
        lang = "en"

    # Only surface stories that have at least one English summary — i.e. the pipeline
    # has finished processing them.  Stories ingested but not yet summarized are hidden.
    summarized_ids_subq = (
        db.query(Summary.story_id)
        .filter(Summary.language == "en")
        .subquery()
    )

    query = (
        db.query(Story)
        .filter(Story.id.in_(select(summarized_ids_subq)))
        .order_by(Story.created_at.desc())
    )
    if category:
        query = query.filter(Story.category == category)

    stories = query.offset(offset).limit(limit).all()

    results = []
    for story in stories:
        # Try the requested language first, fall back to English
        summary = (
            db.query(Summary)
            .filter(Summary.story_id == story.id, Summary.language == lang)
            .first()
        ) or (
            db.query(Summary)
            .filter(Summary.story_id == story.id, Summary.language == "en")
            .first()
        )

        source_count_row = db.execute(
            select(func.count()).where(sa_table.c.story_id == story.id)
        ).scalar()
        source_count = source_count_row or 0

        results.append({
            "id": story.id,
            "title": story.canonical_title,
            "category": story.category,
            "sentiment": story.sentiment,
            "summary": summary.text if summary else "",
            "language": summary.language if summary else lang,
            "source_count": source_count,
            "created_at": story.created_at.isoformat(),
        })

    return {"stories": results, "count": len(results), "offset": offset}
