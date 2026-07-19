import logging
from pathlib import Path

from ai_engine.generation.llm_client import call_llm

logger = logging.getLogger("briefit.summarizer")

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SUMMARIZE_SYSTEM_PROMPT = (PROMPT_DIR / "summarize_prompt.txt").read_text()
SIMPLIFY_SYSTEM_PROMPT  = (PROMPT_DIR / "simplify_prompt.txt").read_text()

MAX_SNIPPET_CHARS = 800   # slightly larger snippet → richer context for 70-80 word target
TARGET_WORDS_MIN  = 60
TARGET_WORDS_MAX  = 90    # soft outer limit; anything in 60-90 is accepted


def _build_summarize_prompt(article_snippets: list[str]) -> str:
    joined = "\n\n".join(f"Article {i+1}: {text}" for i, text in enumerate(article_snippets))
    return f"{SUMMARIZE_SYSTEM_PROMPT}\nArticles:\n{joined}\n\nSummary (70-80 words):"


def summarize(article_snippets: list[str]) -> str | None:
    """Returns a 70-80 word English summary, or None on failure.

    The model is instructed to produce exactly 70-80 words.  If the response
    falls outside the 60-90 word soft range we log a warning but still store it
    — a too-short summary beats a missing one.
    """
    if not article_snippets:
        return None

    prompt = _build_summarize_prompt(article_snippets)
    raw = call_llm(prompt, task="summarize", temperature=0.25, max_tokens=400)
    if raw is None:
        logger.warning("[summarizer] LLM returned None — likely rate-limited")
        return None

    text = raw.strip().strip('"')
    if not text:
        logger.warning("[summarizer] got empty summary")
        return None

    word_count = len(text.split())
    if word_count < TARGET_WORDS_MIN or word_count > TARGET_WORDS_MAX:
        logger.warning(
            "[summarizer] summary word count %d outside soft range %d-%d — keeping it",
            word_count, TARGET_WORDS_MIN, TARGET_WORDS_MAX,
        )
    else:
        logger.info("[summarizer] summary OK: %d words", word_count)
    return text


def simplify(summary_text: str) -> str | None:
    """Simplify a summary to plain language (ELI15 style). Returns None on failure.
    A missing simplified_text is not a reason to skip storing the main summary.
    """
    if not summary_text:
        return None

    prompt = (
        f"{SIMPLIFY_SYSTEM_PROMPT}\n\nOriginal summary:\n\n{summary_text}\n\nSimplified version:"
    )
    raw = call_llm(prompt, task="summarize", temperature=0.2, max_tokens=300)
    if raw is None:
        logger.warning("[summarizer] simplify LLM returned None")
        return None

    text = raw.strip().strip('"')
    return text if text else None
