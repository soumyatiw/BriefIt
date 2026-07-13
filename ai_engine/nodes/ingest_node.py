from datetime import datetime

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.source import Source
from ai_engine.ingestion.rss_scraper import parse_feed
from ai_engine.ingestion.html_scraper import fetch_and_parse
from ai_engine.state import PipelineState

# Keep this in sync with any "type": "static" entries in sources.json.
# One entry per static source, keyed by the source's `name` column.
STATIC_SELECTORS: dict[str, dict] = {
    # "Example Static Source": {
    #     "article_selector": "div.story-card",
    #     "title_selector": "h3",
    #     "link_selector": "a",
    #     "summary_selector": "p.summary",
    # },
}


def ingest_node(state: PipelineState) -> dict:
    db: Session = SessionLocal()
    raw_articles: list[dict] = []
    errors: list[str] = []
    try:
        sources = db.query(Source).all()
        for source in sources:
            try:
                if source.type == "rss":
                    articles = parse_feed(source.url)
                elif source.type == "static":
                    config = STATIC_SELECTORS.get(source.name)
                    if not config:
                        print(f"[ingest_node] no selector config for '{source.name}', skipping")
                        continue
                    articles = fetch_and_parse(source.url, config)
                else:
                    continue

                for a in articles:
                    a["source_id"] = source.id
                raw_articles.extend(articles)
                source.health_status = "ok"
            except Exception as e:
                errors.append(f"{source.name}: {e}")
                source.health_status = "error"
            finally:
                source.last_scraped_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()

    return {
        "raw_articles": raw_articles,
        "run_stats": {"ingested": len(raw_articles), "errors": errors},
    }
