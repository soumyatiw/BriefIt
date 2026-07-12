import json

from ai_engine.ingestion.cleaner import clean
from ai_engine.ingestion.rss_scraper import parse_feed


def test_clean_handles_edge_cases():
    assert clean(None) == ""
    assert clean("") == ""
    assert clean("   ") == ""
    assert clean("<p>Hello <b>world</b></p>") == "Hello world"
    assert clean("Some text. Read more.") == "Some text."
    result = clean("Multi\n\n  spaced\t\ttext")
    assert "  " not in result


def test_rss_scraper_returns_articles():
    with open("ai_engine/ingestion/sources.json") as f:
        sources = json.load(f)
    rss_sources = [s for s in sources if s["type"] == "rss"][:3]
    assert rss_sources, "no RSS sources found in sources.json"

    total_articles = 0
    for source in rss_sources:
        articles = parse_feed(source["url"])
        total_articles += len(articles)
        for a in articles:
            assert a["title"]
            assert a["url"]
            assert a["clean_text"]

    assert total_articles > 0, "none of the sampled RSS sources returned any articles"
