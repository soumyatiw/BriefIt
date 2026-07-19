from datetime import datetime

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.source import Source
from ai_engine.ingestion.rss_scraper import parse_feed
from ai_engine.ingestion.html_scraper import fetch_and_parse
from ai_engine.state import PipelineState

# Keep this in sync with any "type": "static" entries in sources.json.
STATIC_SELECTORS: dict[str, dict] = {}

# Hard cap on new articles per pipeline run.
# At 60 articles / hr, the summarizer (10 stories/run) stays comfortably within
# Groq's free-tier rate limits for llama3-8b-8192.
INGEST_BATCH_LIMIT = 60


def ingest_node(state: PipelineState) -> dict:
    db: Session = SessionLocal()
    raw_articles: list[dict] = []
    errors: list[str] = []
    try:
        sources = db.query(Source).all()
        for source in sources:
            if len(raw_articles) >= INGEST_BATCH_LIMIT:
                break
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
                # Only take as many as we still have room for
                slots_left = INGEST_BATCH_LIMIT - len(raw_articles)
                raw_articles.extend(articles[:slots_left])
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
        "run_stats": {"ingested": len(raw_articles), "ingest_errors": errors},
    }
