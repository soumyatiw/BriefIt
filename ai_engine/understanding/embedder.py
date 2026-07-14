import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_batch(texts: list[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, convert_to_numpy=True, batch_size=32, show_progress_bar=False)


def embed_one(text: str) -> np.ndarray:
    return embed_batch([text])[0]
