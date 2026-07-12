from datetime import UTC, datetime

from sqlalchemy import exc

from api.database import SessionLocal
from api.models.article import Article
from api.models.source import Source
from ai_engine.ingestion.rss_scraper import parse_feed
from ai_engine.ingestion.html_scraper import fetch_and_parse

STATIC_SELECTOR_CONFIGS: dict[str, dict] = {}


def run():
    db = SessionLocal()
    try:
        sources = db.query(Source).all()
        total_inserted = 0
        total_skipped = 0
        total_errors = 0

        for source in sources:
            print(f"\n--- Scraping: {source.name} ({source.url})")

            if source.type == "rss":
                raw_articles = parse_feed(source.url)
            elif source.type == "static":
                config = STATIC_SELECTOR_CONFIGS.get(source.name)
                if not config:
                    print(f"  [SKIP] No selector config for static source '{source.name}'")
                    total_errors += 1
                    source.health_status = "error"
                    continue
                raw_articles = fetch_and_parse(source.url, config)
            else:
                print(f"  [SKIP] Unknown source type '{source.type}'")
                total_errors += 1
                source.health_status = "error"
                continue

            if not raw_articles and source.health_status != "ok":
                source.health_status = "error"
                source.last_scraped_at = datetime.now(UTC)
                total_errors += 1
                print(f"  => 0 articles returned, marked as error")
                continue

            inserted = 0
            skipped = 0
            for art in raw_articles:
                existing = db.query(Article).filter(Article.url == art["url"]).first()
                if existing:
                    skipped += 1
                    continue

                row = Article(
                    source_id=source.id,
                    title=art["title"],
                    url=art["url"],
                    raw_text=art["raw_text"],
                    clean_text=art["clean_text"],
                    published_at=art.get("published_at"),
                    image_url=art.get("image_url"),
                )
                db.add(row)
                try:
                    db.flush()
                    inserted += 1
                except exc.IntegrityError:
                    db.rollback()
                    skipped += 1

            source.health_status = "ok"
            source.last_scraped_at = datetime.now(UTC)
            total_inserted += inserted
            total_skipped += skipped
            print(f"  => {inserted} inserted, {skipped} duplicates skipped")

        db.commit()
        print(f"\n{'='*50}")
        print(f"SUMMARY: {len(sources)} sources scraped")
        print(f"  New articles inserted : {total_inserted}")
        print(f"  Duplicates skipped    : {total_skipped}")
        print(f"  Sources with errors   : {total_errors}")

    finally:
        db.close()


if __name__ == "__main__":
    run()
