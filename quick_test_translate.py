"""
Quick isolation test for Day 9 translation.
Tests IndicTrans2 directly, the LLM fallback path, and all three target languages.
Run with: python quick_test_translate.py
"""
import logging
logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")

from ai_engine.generation.translator import translate, translate_batch

TEXT = "The government announced a new economic policy today aimed at controlling inflation."

print("=" * 60)
print("Testing single translate() for each language...")
print("=" * 60)
for lang in ["hi", "ta", "te"]:
    result = translate(TEXT, lang)
    print(f"[{lang}] {result}")

print()
print("=" * 60)
print("Testing batch translate_batch() — all three in one go per language...")
print("=" * 60)
samples = [
    "A magnitude 5.8 earthquake struck the coastal region early Thursday morning.",
    "TCS has opened an industrial AI solutions lab in Bengaluru in partnership with NVIDIA.",
]
for lang in ["hi", "ta", "te"]:
    results = translate_batch(samples, lang)
    print(f"\n[{lang}]")
    for orig, trans in zip(samples, results):
        print(f"  EN: {orig}")
        print(f"  -> {trans}")

print()
print("=" * 60)
print("Testing LLM fallback path (simulating IndicTrans2 load failure)...")
print("=" * 60)
from ai_engine.generation import translator as _t
_t._load_failed = True
result = translate("Test sentence for fallback.", "hi")
print(f"[hi fallback] {result}")
_t._load_failed = False
