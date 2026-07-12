from datetime import datetime

import feedparser

from ai_engine.ingestion.cleaner import MIN_ARTICLE_LENGTH, clean


def parse_feed(source_url: str) -> list[dict]:
    try:
        feed = feedparser.parse(source_url)
    except Exception as e:
        print(f"[rss_scraper] failed to fetch {source_url}: {e}")
        return []

    if feed.bozo and not feed.entries:
        print(f"[rss_scraper] feed looks malformed, 0 entries: {source_url}")
        return []

    articles = []
    for entry in feed.entries:
        try:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue

            raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            clean_text = clean(raw_summary)
            if len(clean_text) < MIN_ARTICLE_LENGTH:
                continue

            published_at = None
            if getattr(entry, "published_parsed", None):
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            image_url = None
            if getattr(entry, "media_content", None):
                image_url = entry.media_content[0].get("url")

            articles.append({
                "title": title,
                "url": link,
                "raw_text": raw_summary,
                "clean_text": clean_text,
                "published_at": published_at,
                "image_url": image_url,
            })
        except Exception as e:
            print(f"[rss_scraper] skipped a malformed entry in {source_url}: {e}")
            continue

    return articles
