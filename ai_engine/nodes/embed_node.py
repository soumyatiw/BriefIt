from ai_engine.understanding.embedder import embed_batch
from ai_engine.understanding.vector_store import VectorStore
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

    store = VectorStore()
    faiss_ids = store.add(vectors)
    store.save()

    embedded_articles = []
    for article, faiss_id in zip(clean_articles, faiss_ids):
        article_with_id = dict(article)
        article_with_id["faiss_id"] = faiss_id
        embedded_articles.append(article_with_id)

    run_stats["embedded"] = len(embedded_articles)
    return {"embedded_articles": embedded_articles, "run_stats": run_stats}
