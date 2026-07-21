"""
Given a user's liked/bookmarked story embeddings, FAISS-search for similar recent stories.
Falls back gracefully to an empty list on any error (cold start, missing embeddings, etc.)
so the caller can fall back to trending.
"""
from sqlalchemy.orm import Session

from api.models.interaction import Interaction
from api.models.article import Article



from api.models.story import story_articles

def get_recommended_story_ids(
    db: Session,
    user_id: int,
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
    articles = (
        db.query(Article)
        .join(story_articles, Article.id == story_articles.c.article_id)
        .filter(story_articles.c.story_id.in_(story_ids))
        .filter(Article.embedding.isnot(None))
        .all()
    )

    if not articles:
        return []

    seed_vectors = [a.embedding for a in articles]
    recommended_ids: set[int] = set()

    for vec in seed_vectors:
        # Find k closest articles to this seed vector
        similar_articles = (
            db.query(Article)
            .filter(Article.embedding.isnot(None))
            .order_by(Article.embedding.cosine_distance(vec))
            .limit(k)
            .all()
        )
        
        for sim_a in similar_articles:
            # We want the story IDs associated with these similar articles
            associated_stories = db.query(story_articles.c.story_id).filter(story_articles.c.article_id == sim_a.id).all()
            for row in associated_stories:
                if row[0] not in story_ids:
                    recommended_ids.add(row[0])
                    if len(recommended_ids) >= k:
                        break
        if len(recommended_ids) >= k:
            break

    return list(recommended_ids)[:k]
