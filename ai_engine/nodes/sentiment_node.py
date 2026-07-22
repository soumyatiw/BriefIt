import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.article import Article
from api.models.story import Story, story_articles
from ai_engine.understanding.sentiment import analyze_sentiment
from ai_engine.understanding.classifier import classify_category
from ai_engine.state import PipelineState

logger = logging.getLogger("briefit.sentiment_node")

ROLLING_WINDOW_HOURS = 48
BATCH_SIZE = 50          # stories per pipeline run — keeps each run under ~2 minutes
REQUEST_INTERVAL = 2.1   # seconds between LLM calls — Groq free tier allows 30 RPM


def sentiment_node(state: PipelineState) -> dict:
    run_stats = dict(state.get("run_stats", {}))
    db: Session = SessionLocal()

    try:
        cutoff = datetime.utcnow() - timedelta(hours=ROLLING_WINDOW_HOURS)

        untagged_stories = (
            db.query(Story)
            .filter(Story.created_at >= cutoff)
            .filter(Story.sentiment.is_(None))
            .limit(BATCH_SIZE)
            .all()
        )

        logger.info(
            "Running sentiment analysis on %d untagged stories (batch cap %d)",
            len(untagged_stories),
            BATCH_SIZE,
        )

        tagged_count = 0
        for story in untagged_stories:
            member_ids = [
                row[0]
                for row in db.query(story_articles.c.article_id)
                .filter(story_articles.c.story_id == story.id)
                .all()
            ]
            members = db.query(Article).filter(Article.id.in_(member_ids)).all()

            story_dict = {
                "articles": [
                    {
                        "source_name": getattr(m, "source_id", "Unknown"),
                        "title": m.title,
                        "clean_text": m.clean_text,
                    }
                    for m in members
                ]
            }

            result = analyze_sentiment(story_dict)
            story.sentiment = result.sentiment
            story.perspective_note = result.perspective_note

            # Classify category from article titles + text (keyword-based, no LLM call)
            all_titles = " ".join(m.title or "" for m in members)
            all_text   = " ".join((m.clean_text or "")[:300] for m in members)
            story.category = classify_category(all_titles, all_text)

            tagged_count += 1
            db.commit()
            time.sleep(REQUEST_INTERVAL)

        logger.info("Sentiment analysis complete: tagged %d stories", tagged_count)
        run_stats["sentiment_tagged"] = tagged_count

    finally:
        db.close()

    return {"run_stats": run_stats}
