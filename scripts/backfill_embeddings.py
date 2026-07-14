from api.database import SessionLocal
from api.models.article import Article
from ai_engine.understanding.embedder import embed_batch
from ai_engine.understanding.vector_store import VectorStore


def main():
    db = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.faiss_id.is_(None)).all()
        if not articles:
            print("No un-embedded articles found — nothing to backfill.")
            return

        texts = [
            f"{a.title}. {(a.clean_text or '')[:400]}".strip()
            for a in articles
        ]
        vectors = embed_batch(texts)

        store = VectorStore()
        faiss_ids = store.add(vectors)
        store.save()

        for article, faiss_id in zip(articles, faiss_ids):
            article.faiss_id = faiss_id
        db.commit()
        print(f"Backfilled embeddings for {len(articles)} articles.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
