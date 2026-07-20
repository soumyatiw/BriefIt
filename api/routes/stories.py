"""GET /stories/{id} — full detail view for the StoryPage."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.article import Article
from api.models.story import Story, story_articles as sa_table
from api.models.summary import Summary

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/{story_id}")
def get_story_detail(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    summaries = db.query(Summary).filter(Summary.story_id == story_id).all()
    summaries_by_lang = {
        s.language: {"text": s.text, "simplified_text": s.simplified_text}
        for s in summaries
    }

    # Fetch member articles ordered by published_at (newest first)
    member_articles = (
        db.query(Article)
        .join(sa_table, sa_table.c.article_id == Article.id)
        .filter(sa_table.c.story_id == story_id)
        .order_by(Article.published_at.desc())
        .all()
    )
    sources = [
        {
            "name":   a.source.name if a.source else "Unknown",
            "url":    a.url,
            "title":  a.title,
            "domain": __import__("urllib.parse", fromlist=["urlparse"]).urlparse(a.url).netloc,
        }
        for a in member_articles
    ]
    pub_dates = [a.published_at for a in member_articles if a.published_at]
    latest_pub = max(pub_dates) if pub_dates else None

    return {
        "id":              story.id,
        "title":           story.canonical_title,
        "category":        story.category,
        "sentiment":       story.sentiment,
        "perspective_note": story.perspective_note,
        "summaries":       summaries_by_lang,
        "created_at":      story.created_at.isoformat(),
        "published_at":    latest_pub.isoformat() if latest_pub else story.created_at.isoformat(),
        "sources":         sources,
    }
