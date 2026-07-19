"""POST /interactions — like/bookmark, requires auth."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.security import get_current_user_id
from api.models.interaction import Interaction

router = APIRouter(prefix="/interactions", tags=["interactions"])


class InteractionCreate(BaseModel):
    story_id: int
    type: str  # "like" or "bookmark"


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
        db.delete(existing)  # toggle off if already liked/bookmarked
        db.commit()
        return {"status": "removed"}

    interaction = Interaction(user_id=user_id, story_id=payload.story_id, type=payload.type)
    db.add(interaction)
    db.commit()
    return {"status": "added"}
