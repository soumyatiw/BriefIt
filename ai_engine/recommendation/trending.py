"""Simple velocity score: interaction count in the last N hours per story."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.models.interaction import Interaction


def get_trending_story_ids(db: Session, hours: int = 24, limit: int = 10) -> list[int]:
    since = datetime.utcnow() - timedelta(hours=hours)
    rows = (
        db.query(Interaction.story_id, func.count(Interaction.id).label("score"))
        .filter(Interaction.created_at >= since)
        .group_by(Interaction.story_id)
        .order_by(func.count(Interaction.id).desc())
        .limit(limit)
        .all()
    )
    return [r.story_id for r in rows]
