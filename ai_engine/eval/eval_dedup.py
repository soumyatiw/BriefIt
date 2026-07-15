import json
import itertools
from ai_engine.understanding.dedup_cluster import cluster_vectors, DBSCAN_EPS
from ai_engine.understanding.embedder import embed_batch

LABELED_SAMPLES_PATH = "ai_engine/eval/labeled_samples.json"


def load_labeled_samples(path: str = LABELED_SAMPLES_PATH) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def pairwise_precision_recall(true_labels: list[int], pred_labels: list[int]) -> tuple[float, float]:
    n = len(true_labels)
    tp = fp = fn = 0
    for i, j in itertools.combinations(range(n), 2):
        same_true = true_labels[i] == true_labels[j]
        same_pred = pred_labels[i] == pred_labels[j]
        if same_true and same_pred:
            tp += 1
        elif same_pred and not same_true:
            fp += 1
        elif same_true and not same_pred:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return precision, recall


def evaluate(eps: float = DBSCAN_EPS) -> tuple[float, float, float]:
    samples = load_labeled_samples()
    texts = [f"{s['title']}. {s.get('snippet', '')}" for s in samples]
    true_labels = [s["true_cluster"] for s in samples]

    vectors = embed_batch(texts)
    pred_labels = list(cluster_vectors(vectors, eps=eps, min_samples=1))

    precision, recall = pairwise_precision_recall(true_labels, pred_labels)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    print(f"eps={eps:.3f}  precision={precision:.3f}  recall={recall:.3f}  f1={f1:.3f}")
    return precision, recall, f1


def sweep_eps(eps_values: list[float] | None = None):
    eps_values = eps_values or [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    results = [(eps, *evaluate(eps=eps)) for eps in eps_values]
    best = max(results, key=lambda r: r[3])
    print(f"\nBest eps by F1: {best[0]:.3f}  (precision={best[1]:.3f}, recall={best[2]:.3f}, f1={best[3]:.3f})")
    return results


if __name__ == "__main__":
    sweep_eps()
