from datetime import datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.article import Article
from api.models.story import Story, story_articles
from ai_engine.understanding.dedup_cluster import cluster_vectors, cosine_similarity, DBSCAN_EPS, MATCH_THRESHOLD
from ai_engine.understanding.vector_store import VectorStore
from ai_engine.state import PipelineState

ROLLING_WINDOW_HOURS = 48


def _get_vector(store: VectorStore, faiss_id: int) -> np.ndarray:
    return store.index.reconstruct(int(faiss_id))


def dedup_cluster_node(state: PipelineState) -> dict:
    db: Session = SessionLocal()
    run_stats = dict(state.get("run_stats", {}))
    try:
        cutoff = datetime.utcnow() - timedelta(hours=ROLLING_WINDOW_HOURS)
        store = VectorStore()

        assigned_article_ids = {
            row[0]
            for row in db.query(story_articles.c.article_id)
            .join(Article, Article.id == story_articles.c.article_id)
            .filter(Article.published_at >= cutoff)
            .all()
        }

        recent_stories = db.query(Story).filter(Story.created_at >= cutoff).all()
        story_centroids: list[tuple[Story, np.ndarray]] = []
        for story in recent_stories:
            member_ids = [
                row[0]
                for row in db.query(story_articles.c.article_id)
                .filter(story_articles.c.story_id == story.id)
                .all()
            ]
            members = db.query(Article).filter(Article.id.in_(member_ids)).all()
            vectors = [_get_vector(store, a.faiss_id) for a in members if a.faiss_id is not None]
            if vectors:
                story_centroids.append((story, np.mean(vectors, axis=0)))

        query = (
            db.query(Article)
            .filter(Article.published_at >= cutoff)
            .filter(Article.faiss_id.isnot(None))
        )
        if assigned_article_ids:
            query = query.filter(~Article.id.in_(assigned_article_ids))
        unassigned = query.all()

        attached_count = 0
        still_unassigned = []
        for article in unassigned:
            vec = _get_vector(store, article.faiss_id)
            best_story, best_sim = None, -1.0
            for story, centroid in story_centroids:
                sim = cosine_similarity(vec, centroid)
                if sim > best_sim:
                    best_story, best_sim = story, sim
            if best_story is not None and best_sim >= MATCH_THRESHOLD:
                db.execute(story_articles.insert().values(story_id=best_story.id, article_id=article.id))
                attached_count += 1
            else:
                still_unassigned.append(article)
        db.commit()

        new_stories_created = 0
        if still_unassigned:
            vectors = np.array([_get_vector(store, a.faiss_id) for a in still_unassigned])
            labels = cluster_vectors(vectors, eps=DBSCAN_EPS, min_samples=1)

            clusters: dict[int, list[Article]] = {}
            for article, label in zip(still_unassigned, labels):
                clusters.setdefault(int(label), []).append(article)

            for members in clusters.values():
                members_sorted = sorted(members, key=lambda a: a.published_at or datetime.min)
                canonical_title = members_sorted[0].title
                story = Story(canonical_title=canonical_title, category=None)
                db.add(story)
                db.flush()
                for m in members:
                    db.execute(story_articles.insert().values(story_id=story.id, article_id=m.id))
                new_stories_created += 1
            db.commit()

        run_stats["attached_to_existing_story"] = attached_count
        run_stats["new_stories_created"] = new_stories_created
    finally:
        db.close()

    return {"run_stats": run_stats}
