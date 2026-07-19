"""
Computes chrF score (better than BLEU for morphologically rich languages
like Hindi/Tamil/Telugu) between IndicTrans2 output and reference translations.

Run with: python -m ai_engine.eval.eval_translation
"""
import json
from pathlib import Path

import sacrebleu

from ai_engine.generation.translator import translate_batch

SAMPLES_PATH = Path(__file__).parent / "translation_reference_samples.json"


def run_eval():
    if not SAMPLES_PATH.exists():
        print(f"No reference samples found at {SAMPLES_PATH}.")
        print("Create it manually with 10-15 entries — see translation_reference_samples.json.example")
        return

    with open(SAMPLES_PATH) as f:
        samples = json.load(f)

    for lang in ["hi", "ta", "te"]:
        english_texts = [s["en"] for s in samples if s.get(lang)]
        references = [[s[lang] for s in samples if s.get(lang)]]

        if not english_texts:
            print(f"[{lang}] No reference translations provided — skipping.")
            continue

        predictions = translate_batch(english_texts, lang)
        chrf_score = sacrebleu.corpus_chrf(predictions, references)

        print(f"[{lang}] chrF score: {chrf_score.score:.2f}  (n={len(english_texts)} samples)")
        for pred, ref in zip(predictions[:3], references[0][:3]):
            print(f"    Predicted : {pred}")
            print(f"    Reference : {ref}")
            print()


if __name__ == "__main__":
    run_eval()
