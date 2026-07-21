import os
import numpy as np
import faiss

INDEX_DIR = "data/faiss_index"
INDEX_PATH = os.path.join(INDEX_DIR, "articles.index")
EMBEDDING_DIM = 384


class VectorStore:
    def __init__(self):
        os.makedirs(INDEX_DIR, exist_ok=True)
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        else:
            self.index = faiss.IndexFlatIP(EMBEDDING_DIM)

    def add(self, vectors: np.ndarray) -> list[int]:
        vectors = np.ascontiguousarray(vectors.astype("float32"))
        faiss.normalize_L2(vectors)
        start_pos = self.index.ntotal
        self.index.add(vectors)
        return list(range(start_pos, start_pos + vectors.shape[0]))

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[tuple[int, float]]:
        query_vector = np.ascontiguousarray(query_vector.astype("float32").reshape(1, -1))
        faiss.normalize_L2(query_vector)
        scores, positions = self.index.search(query_vector, k)
        return [
            (int(pos), float(score))
            for pos, score in zip(positions[0], scores[0])
            if pos != -1
        ]

    def save(self):
        faiss.write_index(self.index, INDEX_PATH)
