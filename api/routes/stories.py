"""GET /stories/{id} — full detail view for the StoryPage."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.story import Story
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

    return {
        "id": story.id,
        "title": story.canonical_title,
        "category": story.category,
        "sentiment": story.sentiment,
        "perspective_note": story.perspective_note,
        "summaries": summaries_by_lang,
        "created_at": story.created_at.isoformat(),
    }
