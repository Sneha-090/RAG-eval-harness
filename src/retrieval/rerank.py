"""Cross-encoder reranking for Configuration D."""
import math

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L6-v2"
RERANKER_MODEL_REVISION = "233902d25c440f23af6f7d6e94d2946bac0bee0a"
RERANK_CANDIDATES = 20
RERANK_BATCH_SIZE = 16

_model = None


def get_reranker():
    """Load the local cross-encoder once and reuse it."""
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder(RERANKER_MODEL_NAME, revision=RERANKER_MODEL_REVISION)
    return _model


def predict_scores(question, chunks):
    pairs = [(question, chunk["text"]) for chunk in chunks]
    return get_reranker().predict(
        pairs,
        batch_size=RERANK_BATCH_SIZE,
        show_progress_bar=False,
    )


class RerankedRetriever:
    def __init__(self, candidate_retrieve, score_fn=predict_scores,
                 candidate_count=RERANK_CANDIDATES):
        if candidate_count <= 0:
            raise ValueError("candidate_count must be positive")
        self.candidate_retrieve = candidate_retrieve
        self.score_fn = score_fn
        self.candidate_count = candidate_count

    def retrieve(self, question, k):
        if k <= 0:
            raise ValueError("k must be positive")
        count = max(k, self.candidate_count)
        candidates = self.candidate_retrieve(question, count)
        if not candidates:
            return []
        raw_scores = self.score_fn(question, candidates)
        scores = [float(score) for score in raw_scores]
        if len(scores) != len(candidates):
            raise ValueError("Reranker returned the wrong number of scores")
        if any(not math.isfinite(score) for score in scores):
            raise ValueError("Reranker returned a non-finite score")
        ranked = sorted(enumerate(zip(candidates, scores)),
                        key=lambda item: (-item[1][1], item[0]))
        return [{**chunk, "rerank_score": score}
                for _, (chunk, score) in ranked[:k]]
