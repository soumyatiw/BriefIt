from typing import TypedDict


class PipelineState(TypedDict, total=False):
    raw_articles: list[dict]       # straight from scrapers (Day 4)
    clean_articles: list[dict]     # after dedup-by-URL (Day 4)
    embedded_articles: list[dict]  # + embedding vector per article (Day 5)
    stories: list[dict]            # clustered groups of article ids (Day 6)
    sentiment_tagged: list[dict]   # stories + sentiment/perspective note (Day 7)
    summarized: list[dict]         # stories + English summary + simplified (Day 8)
    translated: list[dict]         # stories + hi/ta/te summaries (Day 9)
    run_stats: dict                # counts, timings, errors — grows every day
