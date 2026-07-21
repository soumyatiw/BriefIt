from typing import TypedDict


class PipelineState(TypedDict, total=False):
    raw_articles: list[dict]       # straight from scrapers
    clean_articles: list[dict]     # after dedup-by-URL
    embedded_articles: list[dict]  # + embedding vector per article 
    stories: list[dict]            # clustered groups of article ids
    sentiment_tagged: list[dict]   # stories + sentiment/perspective note
    summarized: list[dict]         # stories + English summary + simplified
    translated: list[dict]         # stories + hi/ta/te summaries
    run_stats: dict                # counts, timings, errors
