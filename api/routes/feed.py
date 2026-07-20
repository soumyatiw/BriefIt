"""
GET /feed?lang=en&category=technology&offset=0&limit=20
Returns stories that have at least one English summary (pipeline-processed only).
Supports pagination via offset for the "Load more" button.

GET /feed/total — returns the total count of summarized stories for pagination math.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.article import Article
from api.models.story import Story, story_articles as sa_table
from api.models.summary import Summary
from api.security import get_current_user_id_optional

router = APIRouter(prefix="/feed", tags=["feed"])

VALID_LANGS = {"en", "hi", "ta", "te"}
PAGE_SIZE   = 20


@router.get("/total")
def get_feed_total(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Returns the total count of summarized stories — used by the frontend to decide
    whether to show the Load More button."""
    summarized_ids_subq = (
        db.query(Summary.story_id).filter(Summary.language == "en").subquery()
    )
    q = db.query(func.count(Story.id)).filter(Story.id.in_(select(summarized_ids_subq)))
    if category:
        q = q.filter(Story.category == category)
    total = q.scalar() or 0
    return {"total": total}


@router.get("")
def get_feed(
    lang: str = Query("en"),
    category: str | None = Query(None),
    limit: int = Query(PAGE_SIZE, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id_optional),
):
    if lang not in VALID_LANGS:
        lang = "en"

    # Only show stories that have at least one English summary row.
    # Stories ingested but not yet summarized are invisible until the pipeline finishes them.
    summarized_ids_subq = (
        db.query(Summary.story_id)
        .filter(Summary.language == "en")
        .subquery()
    )

    # Sort by the most recent article published_at within each story,
    # so truly fresh stories always float to the top of the feed.
    latest_article_date = (
        db.query(sa_table.c.story_id, func.max(Article.published_at).label("latest"))
        .join(Article, Article.id == sa_table.c.article_id)
        .group_by(sa_table.c.story_id)
        .subquery()
    )
    query = (
        db.query(Story)
        .outerjoin(latest_article_date, latest_article_date.c.story_id == Story.id)
        .filter(Story.id.in_(select(summarized_ids_subq)))
        .order_by(latest_article_date.c.latest.desc().nullslast(), Story.created_at.desc())
    )
    if category:
        query = query.filter(Story.category == category)

    total = query.count()
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

        # Fetch member articles with their source names for the sources chip
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
            "language":     summary.language if summary else lang,
            "source_count": len(sources_list),
            "created_at":   story.created_at.isoformat(),
            "published_at": latest_pub.isoformat() if latest_pub else story.created_at.isoformat(),
            "sources":      sources_list,
        })

    has_more = (offset + len(results)) < total
    return {
        "stories":  results,
        "count":    len(results),
        "offset":   offset,
        "total":    total,
        "has_more": has_more,
    }
