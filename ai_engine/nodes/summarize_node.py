import logging
import time

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.story import Story, story_articles
from api.models.article import Article
from api.models.summary import Summary
from ai_engine.generation.summarizer import summarize, simplify, MAX_SNIPPET_CHARS
from ai_engine.state import PipelineState

logger = logging.getLogger("briefit.summarize_node")

REQUEST_INTERVAL = 2.1
MAX_CONSECUTIVE_FAILURES = 3
BATCH_SIZE = 50


def summarize_node(state: PipelineState) -> dict:
    db: Session = SessionLocal()
    run_stats = dict(state.get("run_stats", {}))
    summarized = 0
    failed = 0
    consecutive_failures = 0

    try:
        stories_with_en_summary = {
            row[0]
            for row in db.query(Summary.story_id).filter(Summary.language == "en").all()
        }
        pending = [s for s in db.query(Story).all() if s.id not in stories_with_en_summary]
        pending = pending[:BATCH_SIZE]

        logger.info(
            "summarize_node: %d stories already summarized, %d pending",
            len(stories_with_en_summary),
            len(pending),
        )

        for story in pending:
            member_ids = [
                row[0]
                for row in db.query(story_articles.c.article_id)
                .filter(story_articles.c.story_id == story.id)
                .all()
            ]
            members = db.query(Article).filter(Article.id.in_(member_ids)).all()
            snippets = [
                f"{a.title}. {(a.clean_text or '')[:MAX_SNIPPET_CHARS]}" for a in members
            ]
            if not snippets:
                logger.warning("story_id=%d has no article snippets, skipping", story.id)
                continue

            summary_text = summarize(snippets)
            time.sleep(REQUEST_INTERVAL)

            if summary_text is None:
                failed += 1
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    logger.warning(
                        "summarize_node: %d consecutive failures — daily LLM quota likely "
                        "exhausted. Stopping early. Remaining stories will be retried next run.",
                        consecutive_failures,
                    )
                    break
                continue

            consecutive_failures = 0
            simplified_text = simplify(summary_text)
            time.sleep(REQUEST_INTERVAL)

            db.add(
                Summary(
                    story_id=story.id,
                    language="en",
                    text=summary_text,
                    simplified_text=simplified_text,
                )
            )
            summarized += 1
            db.commit()

    finally:
        db.close()

    logger.info(
        "summarize_node complete: summarized=%d failed=%d", summarized, failed
    )
    run_stats["summarized"] = summarized
    run_stats["summarize_failed"] = failed
    return {"run_stats": run_stats}
