"""
IndicTrans2 wrapper for English -> Hindi/Tamil/Telugu translation.

Loads the model ONCE at module import (this is the slow step) and exposes
a simple translate(text, target_lang) -> str function.

Falls back to the Groq LLM for translation if IndicTrans2 fails to load or
errors at inference time — this keeps the pipeline running even if the
IndicTrans2 environment has an issue, at the cost of translation quality
for that run (logged clearly so you know when it happened).
"""
import logging
import warnings

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from ai_engine.generation.llm_client import call_llm

logger = logging.getLogger("briefit.translator")

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

LANG_CODE_MAP = {
    "hi": "hin_Deva",
    "ta": "tam_Taml",
    "te": "tel_Telu",
}
SRC_LANG = "eng_Latn"

_model = None
_tokenizer = None
_ip = None
_load_failed = False


def _load_model():
    """Lazy singleton loader — only runs once, on first real translate() call."""
    global _model, _tokenizer, _ip, _load_failed
    if _model is not None or _load_failed:
        return

    try:
        from IndicTransToolkit.processor import IndicProcessor

        logger.info(
            "Loading IndicTrans2 model (%s) on %s — this can take a while on first run...",
            MODEL_NAME,
            DEVICE,
        )
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, trust_remote_code=True).to(DEVICE)
        _model.eval()
        _ip = IndicProcessor(inference=True)
        logger.info("IndicTrans2 model loaded successfully.")

    except Exception as e:
        logger.error(
            "Failed to load IndicTrans2 model: %s. Will fall back to LLM translation.", e
        )
        _load_failed = True


def _translate_via_indictrans2(texts: list[str], target_lang: str) -> list[str] | None:
    """Batch-translates a list of English strings into one target language. Returns None on failure."""
    _load_model()
    if _load_failed:
        return None

    tgt_code = LANG_CODE_MAP[target_lang]
    try:
        batch = _ip.preprocess_batch(texts, src_lang=SRC_LANG, tgt_lang=tgt_code)
        inputs = _tokenizer(
            batch, truncation=True, padding="longest", return_tensors="pt", max_length=256
        ).to(DEVICE)

        with torch.no_grad():
            generated_tokens = _model.generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=256,
                num_beams=5,
                num_return_sequences=1,
            )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*as_target_tokenizer.*")
            with _tokenizer.as_target_tokenizer():
                decoded = _tokenizer.batch_decode(
                    generated_tokens.detach().cpu().tolist(),
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )
        translations = _ip.postprocess_batch(decoded, lang=tgt_code)
        return translations

    except Exception as e:
        logger.error("IndicTrans2 inference failed for lang=%s: %s", target_lang, e)
        return None


def _translate_via_llm_fallback(texts: list[str], target_lang: str) -> list[str]:
    """Last-resort fallback using the Groq LLM directly, one call per text."""
    lang_name = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu"}[target_lang]
    results = []
    for text in texts:
        prompt = (
            f"Translate the following English news summary into natural, fluent {lang_name}. "
            f"Return ONLY the translation, nothing else.\n\nEnglish text:\n{text}"
        )
        translated = call_llm(prompt, task="summarize", temperature=0.2, max_tokens=300)
        results.append(translated if translated else text)
    return results


def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """
    Public entrypoint. Translates a batch of English texts into target_lang ('hi'/'ta'/'te').
    Batching all stories per language — not one call per sentence — is the key perf decision.
    """
    if target_lang not in LANG_CODE_MAP:
        raise ValueError(
            f"Unsupported target_lang '{target_lang}'. Must be one of {list(LANG_CODE_MAP)}"
        )
    if not texts:
        return []

    result = _translate_via_indictrans2(texts, target_lang)
    if result is not None:
        return result

    logger.warning(
        "Using LLM fallback translation for lang=%s (IndicTrans2 unavailable)", target_lang
    )
    return _translate_via_llm_fallback(texts, target_lang)


def translate(text: str, target_lang: str) -> str:
    """Convenience single-string wrapper around translate_batch."""
    return translate_batch([text], target_lang)[0]
