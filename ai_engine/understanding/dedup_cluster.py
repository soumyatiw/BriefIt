import numpy as np
from sklearn.cluster import DBSCAN

DBSCAN_EPS = 0.34          # tuned 2026-07-15: last eps with precision=1.000 before false positives appear; F1=0.771 on 64 hard-negative-inclusive articles (re-tuned after adding hard negatives for same-topic different-event pairs)
MATCH_THRESHOLD = 0.80     # cosine similarity required to attach to an existing story; raised to match stricter eps


def cluster_vectors(vectors: np.ndarray, eps: float = DBSCAN_EPS, min_samples: int = 1) -> np.ndarray:
    if len(vectors) == 0:
        return np.array([], dtype=int)
    if len(vectors) == 1:
        return np.array([0], dtype=int)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
    return dbscan.fit_predict(vectors)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
