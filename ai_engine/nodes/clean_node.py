from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.article import Article
from ai_engine.state import PipelineState


def clean_node(state: PipelineState) -> dict:
    raw_articles = state.get("raw_articles", [])
    db: Session = SessionLocal()
    try:
        existing_urls = {row[0] for row in db.query(Article.url).all()}
    finally:
        db.close()

    # Deduplicate within the batch itself first, then against the DB.
    seen: set[str] = set()
    unique_raw: list[dict] = []
    for a in raw_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique_raw.append(a)

    clean_articles = [a for a in unique_raw if a["url"] not in existing_urls]

    run_stats = dict(state.get("run_stats", {}))
    run_stats["deduped_new"] = len(clean_articles)
    run_stats["deduped_skipped"] = len(unique_raw) - len(clean_articles)
    run_stats["within_batch_dupes"] = len(raw_articles) - len(unique_raw)
    return {"clean_articles": clean_articles, "run_stats": run_stats}
