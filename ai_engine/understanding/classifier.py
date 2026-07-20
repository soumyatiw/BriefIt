"""
Lightweight rule-based category classifier.
Uses keyword matching on article titles/text — no LLM call needed, instant and free.
Falls back to 'general' if no keywords match.

Categories: politics, technology, finance, sports, entertainment, general
"""

import re

RULES: list[tuple[str, list[str]]] = [
    ("politics", [
        "parliament", "minister", "pm ", "prime minister", "bjp", "congress", "election",
        "lok sabha", "rajya sabha", "government", "policy", "protest", "party", "mla",
        "mp ", "governor", "president", "diplomat", "treaty", "cjp", "waqf", "rahul",
        "modi", "yogi", "kejriwal", "bill passed", "opposition", "ruling party",
        "chief minister", "cm ", "constitution", "supreme court", "high court", "judiciary",
        "political", "vote", "ballot", "democracy", "coup", "sanction",
    ]),
    ("technology", [
        "ai ", "artificial intelligence", "machine learning", "tech", "software",
        "startup", "app ", "iphone", "android", "google", "microsoft", "apple ",
        "meta ", "openai", "chatgpt", "cybersecurity", "hack", "data breach",
        "semiconductor", "chip", "5g", "internet", "cloud", "robotics", "drone",
        "elon musk", "tesla", "spacex", "satellite", "launch vehicle",
    ]),
    ("finance", [
        "stock", "market", "sensex", "nifty", "rupee", "rbi", "sebi", "ipo",
        "economy", "gdp", "inflation", "interest rate", "budget", "tax", "revenue",
        "profit", "loss", "earnings", "quarterly", "fiscal", "investment", "fund",
        "startup funding", "unicorn", "vc ", "venture capital", "nse", "bse",
        "cryptocurrency", "bitcoin", "banking", "loan", "credit", "insurance",
        "trade deficit", "export", "import", "forex",
    ]),
    ("sports", [
        "cricket", "ipl", "bcci", "test match", "odi", "t20", "icc",
        "football", "fifa", "premier league", "la liga", "champions league",
        "tennis", "wimbledon", "us open", "french open", "australian open",
        "olympics", "cwg", "asian games", "hockey", "badminton", "chess",
        "wrestling", "boxing", "athlete", "medal", "gold medal", "world cup",
        "rohit sharma", "virat", "dhoni", "neymar", "messi", "ronaldo",
        "formula 1", "f1 ", "motorsport", "kabaddi", "pro kabaddi",
    ]),
    ("entertainment", [
        "bollywood", "hollywood", "movie", "film", "actor", "actress",
        "celebrity", "box office", "ott", "netflix", "amazon prime", "disney",
        "music album", "song ", "concert", "award", "oscar", "filmfare",
        "web series", "trailer", "release date", "fashion", "lifestyle",
        "viral", "meme", "instagram", "youtube channel",
    ]),
]


def classify_category(title: str, text: str = "") -> str:
    """
    Returns one of: politics | technology | finance | sports | entertainment | general.
    Scores each category by keyword hits across title (weight 3×) + text (weight 1×).
    """
    combined_title = title.lower()
    combined_text = (text or "").lower()

    scores: dict[str, int] = {}
    for category, keywords in RULES:
        score = 0
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw.strip()), combined_title):
                score += 3
            if re.search(r'\b' + re.escape(kw.strip()), combined_text):
                score += 1
        scores[category] = score

    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"
