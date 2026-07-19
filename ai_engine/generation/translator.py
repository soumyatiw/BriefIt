"""
Translation: English → Hindi / Tamil / Telugu

Uses GoogleTranslator (deep-translator) — instant, free, no API key, no quota.
Falls back to Groq LLM only if the network is unavailable.
"""
import logging

from ai_engine.generation.llm_client import call_llm

logger = logging.getLogger("briefit.translator")

GOOGLE_LANG_MAP = {
    "hi": "hi",   # Hindi
    "ta": "ta",   # Tamil
    "te": "te",   # Telugu
}


def _translate_via_google(texts: list[str], target_lang: str) -> list[str] | None:
    """Primary: Google Translate via deep-translator. Returns None if unavailable."""
    try:
        from deep_translator import GoogleTranslator  # type: ignore[import]
        tgt = GOOGLE_LANG_MAP[target_lang]
        results = [GoogleTranslator(source="en", target=tgt).translate(t) or t for t in texts]
        logger.info("Google translated %d texts → %s", len(texts), target_lang)
        return results
    except Exception as exc:
        logger.warning("GoogleTranslator failed (%s) for lang=%s — LLM fallback", exc, target_lang)
        return None


def _translate_via_llm(texts: list[str], target_lang: str) -> list[str]:
    """Last-resort Groq LLM fallback (uses token quota — only when offline)."""
    lang_name = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu"}[target_lang]
    results = []
    for text in texts:
        prompt = (
            f"Translate the following English news summary into natural, fluent {lang_name}. "
            f"Return ONLY the translation, nothing else.\n\nEnglish text:\n{text}"
        )
        out = call_llm(prompt, task="summarize", temperature=0.2, max_tokens=300)
        results.append(out if out else text)
    return results


def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """Translate a list of English strings to target_lang ('hi' / 'ta' / 'te').
    Tries Google Translate first, then Groq LLM as last resort.
    """
    if target_lang not in GOOGLE_LANG_MAP:
        raise ValueError(f"Unsupported target_lang '{target_lang}'. Use: {list(GOOGLE_LANG_MAP)}")
    if not texts:
        return []

    result = _translate_via_google(texts, target_lang)
    if result is not None:
        return result

    logger.warning("Network unavailable — using LLM fallback for lang=%s", target_lang)
    return _translate_via_llm(texts, target_lang)


def translate(text: str, target_lang: str) -> str:
    """Single-string convenience wrapper."""
    return translate_batch([text], target_lang)[0]
