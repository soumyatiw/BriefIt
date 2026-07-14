from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.article import Article
from ai_engine.state import PipelineState


def persist_node(state: PipelineState) -> dict:
    articles_to_persist = state.get("embedded_articles") or state.get("clean_articles", [])

    db: Session = SessionLocal()
    inserted = 0
    try:
        for a in articles_to_persist:
            if db.query(Article).filter(Article.url == a["url"]).first():
                continue
            db.add(Article(
                source_id=a["source_id"],
                title=a["title"],
                raw_text=a.get("raw_text"),
                clean_text=a.get("clean_text"),
                url=a["url"],
                published_at=a.get("published_at"),
                image_url=a.get("image_url"),
                faiss_id=a.get("faiss_id"),
            ))
            inserted += 1
        db.commit()
    finally:
        db.close()

    run_stats = dict(state.get("run_stats", {}))
    run_stats["persisted"] = inserted
    return {"run_stats": run_stats}
