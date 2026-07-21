from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.article import Article
from ai_engine.understanding.embedder import embed_batch
from ai_engine.state import PipelineState


def _embedding_input(article: dict) -> str:
    snippet = (article.get("clean_text") or "")[:400]
    return f"{article['title']}. {snippet}".strip()


def embed_node(state: PipelineState) -> dict:
    clean_articles = state.get("clean_articles", [])
    run_stats = dict(state.get("run_stats", {}))

    if not clean_articles:
        run_stats["embedded"] = 0
        return {"embedded_articles": [], "run_stats": run_stats}

    texts = [_embedding_input(a) for a in clean_articles]
    vectors = embed_batch(texts)

    embedded_articles = []
    for article, vec in zip(clean_articles, vectors):
        article_with_vec = dict(article)
        article_with_vec["embedding"] = vec
        embedded_articles.append(article_with_vec)

    db: Session = SessionLocal()
    try:
        for a in embedded_articles:
            if db.query(Article).filter(Article.url == a["url"]).first():
                continue
            db.add(Article(
                source_id=a["source_id"],
                title=a["title"],
                raw_text=a.get("raw_text"),
                clean_text=a.get("clean_text"),
                url=a["url"],
                published_at=a.get("published_at"),
                image_url=a.get("image_url"),
                embedding=a["embedding"],
            ))
        db.commit()
    finally:
        db.close()

    run_stats["embedded"] = len(embedded_articles)
    return {"embedded_articles": embedded_articles, "run_stats": run_stats}
