from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ai_engine.ingestion.cleaner import MIN_ARTICLE_LENGTH, clean

REQUEST_TIMEOUT = 10
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BriefItBot/1.0)"}


def fetch_and_parse(url: str, selector_config: dict) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"[html_scraper] failed to fetch {url}: {e}")
        return []

    articles = []
    try:
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select(selector_config["article_selector"])
        for card in cards:
            try:
                title_el = card.select_one(selector_config["title_selector"])
                link_el = card.select_one(selector_config["link_selector"])
                summary_el = card.select_one(selector_config.get("summary_selector", ""))

                title = title_el.get_text(strip=True) if title_el else ""
                link = link_el.get("href", "") if link_el else ""
                if not title or not link:
                    continue

                if link.startswith("/"):
                    link = urljoin(url, link)

                raw_summary = summary_el.get_text(strip=True) if summary_el else ""
                clean_text = clean(raw_summary)
                if len(clean_text) < MIN_ARTICLE_LENGTH:
                    continue

                articles.append({
                    "title": title,
                    "url": link,
                    "raw_text": raw_summary,
                    "clean_text": clean_text,
                    "published_at": None,
                    "image_url": None,
                })
            except Exception as e:
                print(f"[html_scraper] skipped a malformed card on {url}: {e}")
                continue
    except Exception as e:
        print(f"[html_scraper] failed to parse {url}: {e}")
        return []

    return articles
