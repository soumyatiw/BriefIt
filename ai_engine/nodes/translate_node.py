"""
LangGraph node wrapper for translation.

Reads English summaries from the summaries table, translates them into
Hindi, Tamil, and Telugu using IndicTrans2, and writes new Summary rows per
language. Stories that already have all three language rows are skipped, so
re-running is safe and free.

Design note: this node reads from the DB rather than from LangGraph state
because summarize_node writes directly to the DB (not to state). All nodes
in this pipeline follow the same DB-centric pattern for exactly this reason.
"""
import logging

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.summary import Summary
from ai_engine.generation.translator import translate_batch
from ai_engine.state import PipelineState

logger = logging.getLogger("briefit.translate_node")

TARGET_LANGS = ["hi", "ta", "te"]


def translate_node(state: PipelineState) -> dict:
    db: Session = SessionLocal()
    run_stats = dict(state.get("run_stats", {}))
    translated = 0
    skipped = 0
    failed_stories = 0

    try:
        en_summaries = db.query(Summary).filter(Summary.language == "en").all()

        if not en_summaries:
            logger.info("translate_node: no English summaries found, nothing to translate")
            run_stats["translated"] = 0
            run_stats["translate_skipped"] = 0
            return {"run_stats": run_stats}

        existing_translations = {
            (row.story_id, row.language)
            for row in db.query(Summary.story_id, Summary.language)
            .filter(Summary.language.in_(TARGET_LANGS))
            .all()
        }

        pending = [
            s for s in en_summaries
            if all((s.story_id, lang) not in existing_translations for lang in TARGET_LANGS)
        ]

        logger.info(
            "translate_node: %d English summaries found, %d already fully translated, %d pending",
            len(en_summaries),
            len(en_summaries) - len(pending),
            len(pending),
        )

        if not pending:
            run_stats["translated"] = 0
            run_stats["translate_skipped"] = len(en_summaries)
            return {"run_stats": run_stats}

        summaries_text = [s.text for s in pending]
        simplified_text = [s.simplified_text or "" for s in pending]

        for lang in TARGET_LANGS:
            logger.info("Translating %d summaries into '%s'...", len(pending), lang)

            translated_summaries = translate_batch(summaries_text, lang)
            translated_simplified = translate_batch(
                [t for t in simplified_text if t], lang
            )

            simplified_iter = iter(translated_simplified)

            for i, en_summary in enumerate(pending):
                lang_key = (en_summary.story_id, lang)
                if lang_key in existing_translations:
                    continue

                translated_main = translated_summaries[i] if i < len(translated_summaries) else None
                if not translated_main:
                    logger.warning(
                        "story_id=%d lang=%s: got empty translation, skipping this lang row",
                        en_summary.story_id,
                        lang,
                    )
                    failed_stories += 1
                    continue

                translated_simple = next(simplified_iter, None) if simplified_text[i] else None

                db.add(
                    Summary(
                        story_id=en_summary.story_id,
                        language=lang,
                        text=translated_main,
                        simplified_text=translated_simple,
                    )
                )

            db.commit()
            translated += len(pending)
            logger.info("Committed '%s' translations.", lang)

        skipped = len(en_summaries) - len(pending)

    finally:
        db.close()

    logger.info(
        "translate_node complete: translated=%d skipped=%d failed=%d",
        translated,
        skipped,
        failed_stories,
    )
    run_stats["translated"] = translated
    run_stats["translate_skipped"] = skipped
    run_stats["translate_failed"] = failed_stories
    return {"run_stats": run_stats}
