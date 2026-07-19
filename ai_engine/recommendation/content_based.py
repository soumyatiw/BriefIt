"""
Given a user's liked/bookmarked story embeddings, FAISS-search for similar recent stories.
Falls back gracefully to an empty list on any error (cold start, missing embeddings, etc.)
so the caller can fall back to trending.
"""
from sqlalchemy.orm import Session

from api.models.interaction import Interaction
from api.models.article import Article
from ai_engine.understanding.vector_store import VectorStore  # Day 5 FAISS wrapper


def get_recommended_story_ids(
    db: Session,
    user_id: int,
    vector_store: VectorStore,
    k: int = 10,
) -> list[int]:
    """Return up to k story IDs similar to the stories the user has liked/bookmarked.

    Returns an empty list on cold start (no interactions) or if no embeddings exist yet.
    """
    liked = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id, Interaction.type.in_(["like", "bookmark"]))
        .order_by(Interaction.created_at.desc())
        .limit(5)  # use the user's 5 most recent likes as the "taste" signal
        .all()
    )
    if not liked:
        return []  # cold start — caller should fall back to trending

    story_ids = [i.story_id for i in liked]

    # Fetch articles linked to those stories
    try:
        articles = (
            db.query(Article)
            .join(Article.story_articles)
            .filter(Article.story_articles.any(story_id__in=story_ids))
            .all()
        )
    except Exception:
        articles = []

    if not articles or not any(a.embedding for a in articles):
        return []

    seed_vectors = [a.embedding for a in articles if a.embedding]
    recommended_ids: set[int] = set()
    for vec in seed_vectors:
        similar = vector_store.search(vec, k=k)
        recommended_ids.update(similar)

    return list(recommended_ids - set(story_ids))[:k]  # exclude what they already engaged with
