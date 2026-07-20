"""
POST /interactions            — toggle like/bookmark (auth required)
GET  /interactions?type=like  — returns story IDs the user has liked/bookmarked
GET  /interactions/stories    — returns full enriched stories the user liked/bookmarked
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.models.article import Article
from api.models.interaction import Interaction
from api.models.story import Story, story_articles as sa_table
from api.models.summary import Summary
from api.security import get_current_user_id

router = APIRouter(prefix="/interactions", tags=["interactions"])


class InteractionCreate(BaseModel):
    story_id: int
    type: str  # "like" or "bookmark"


def _enrich(story: Story, db: Session, lang: str = "en") -> dict:
    summary = (
        db.query(Summary).filter(Summary.story_id == story.id, Summary.language == lang).first()
        or db.query(Summary).filter(Summary.story_id == story.id, Summary.language == "en").first()
    )
    member_articles = (
        db.query(Article)
        .join(sa_table, sa_table.c.article_id == Article.id)
        .filter(sa_table.c.story_id == story.id)
        .order_by(Article.published_at.desc())
        .all()
    )
    sources = [
        {"name": a.source.name if a.source else "Unknown", "url": a.url, "title": a.title}
        for a in member_articles
    ]
    pub_dates = [a.published_at for a in member_articles if a.published_at]
    latest_pub = max(pub_dates) if pub_dates else None
    return {
        "id":           story.id,
        "title":        story.canonical_title,
        "category":     story.category,
        "sentiment":    story.sentiment,
        "summary":      summary.text if summary else "",
        "language":     summary.language if summary else "en",
        "source_count": len(sources),
        "created_at":   story.created_at.isoformat(),
        "published_at": latest_pub.isoformat() if latest_pub else story.created_at.isoformat(),
        "sources":      sources,
    }


@router.post("")
def create_interaction(
    payload: InteractionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if payload.type not in {"like", "bookmark"}:
        raise HTTPException(status_code=400, detail="type must be 'like' or 'bookmark'")

    existing = (
        db.query(Interaction)
        .filter(
            Interaction.user_id == user_id,
            Interaction.story_id == payload.story_id,
            Interaction.type == payload.type,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "removed"}

    db.add(Interaction(user_id=user_id, story_id=payload.story_id, type=payload.type))
    db.commit()
    return {"status": "added"}


@router.get("")
def get_interaction_ids(
    type: str = Query("like"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Returns list of story IDs the user has liked or bookmarked."""
    rows = (
        db.query(Interaction.story_id)
        .filter(Interaction.user_id == user_id, Interaction.type == type)
        .all()
    )
    return {"story_ids": [r[0] for r in rows]}


@router.get("/stories")
def get_interacted_stories(
    type: str = Query("like"),
    lang: str = Query("en"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Returns full enriched stories the user has liked or bookmarked, newest first."""
    interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id, Interaction.type == type)
        .order_by(Interaction.created_at.desc())
        .all()
    )
    story_ids = [i.story_id for i in interactions]
    stories = db.query(Story).filter(Story.id.in_(story_ids)).all()
    # preserve interaction order (newest first)
    order_map = {sid: idx for idx, sid in enumerate(story_ids)}
    stories_sorted = sorted(stories, key=lambda s: order_map.get(s.id, 999))
    return {"stories": [_enrich(s, db, lang) for s in stories_sorted], "type": type}
