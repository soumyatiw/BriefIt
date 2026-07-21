import numpy as np
# pyrefly: ignore [missing-import]
from fastembed import TextEmbedding

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=_MODEL_NAME)
    return _model


def embed_batch(texts: list[str]) -> np.ndarray:
    model = get_model()
    embeddings = list(model.embed(texts, batch_size=32))
    return np.array(embeddings)


def embed_one(text: str) -> np.ndarray:
    return embed_batch([text])[0]
