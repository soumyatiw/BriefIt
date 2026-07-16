import logging
from pathlib import Path

from ai_engine.generation.llm_client import call_llm

logger = logging.getLogger("briefit.summarizer")

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SUMMARIZE_SYSTEM_PROMPT = (PROMPT_DIR / "summarize_prompt.txt").read_text()
SIMPLIFY_SYSTEM_PROMPT = (PROMPT_DIR / "simplify_prompt.txt").read_text()

MAX_SNIPPET_CHARS = 600
MIN_SUMMARY_WORDS = 40
MAX_SUMMARY_WORDS = 120


def _build_summarize_prompt(article_snippets: list[str]) -> str:
    joined = "\n\n".join(f"Article {i+1}: {text}" for i, text in enumerate(article_snippets))
    return f"{SUMMARIZE_SYSTEM_PROMPT}\nArticles:\n{joined}\n\nGood summary:"


def summarize(article_snippets: list[str]) -> str | None:
    """Returns None on empty input, empty LLM response, or a failed LLM call.
    Word count outside the 60-80 target is a WARNING, not a failure — the
    summary is still returned and stored."""
    if not article_snippets:
        return None

    prompt = _build_summarize_prompt(article_snippets)
    raw = call_llm(prompt, task="summarize", temperature=0.2, max_tokens=300)
    if raw is None:
        logger.warning("[summarizer] LLM call returned None, skipping")
        return None

    text = raw.strip().strip('"')
    if not text:
        logger.warning("[summarizer] got an empty summary back, skipping")
        return None

    word_count = len(text.split())
    if word_count < MIN_SUMMARY_WORDS or word_count > MAX_SUMMARY_WORDS:
        logger.warning(
            "[summarizer] summary word count (%d) outside soft range %d-%d "
            "(target 60-80) — keeping it anyway.",
            word_count,
            MIN_SUMMARY_WORDS,
            MAX_SUMMARY_WORDS,
        )
    return text


def simplify(summary_text: str) -> str | None:
    """Returns None on empty input or a failed LLM call. Caller should still
    store the original summary even if this returns None — a missing
    simplified_text is not a reason to discard the summary itself."""
    if not summary_text:
        return None

    prompt = (
        f"{SIMPLIFY_SYSTEM_PROMPT}\n\nOriginal summary:\n\n{summary_text}\n\nSimplified version:"
    )
    raw = call_llm(prompt, task="summarize", temperature=0.2, max_tokens=300)
    if raw is None:
        logger.warning("[summarizer] simplify LLM call returned None, skipping")
        return None

    text = raw.strip().strip('"')
    if not text:
        logger.warning("[summarizer] got an empty simplified summary back, skipping")
        return None
    return text
