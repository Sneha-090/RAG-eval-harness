import unittest

from src.retrieval.rerank import RerankedRetriever


def chunk(key):
    return {"chunk_id": key, "doc_id": "sample.md", "text": f"text {key}"}


class RerankedRetrieverTests(unittest.TestCase):
    def test_cross_encoder_scores_reorder_hybrid_candidates(self):
        candidates = [chunk("a"), chunk("b"), chunk("c")]
        calls = []

        def retrieve(question, k):
            calls.append((question, k))
            return candidates

        reranker = RerankedRetriever(retrieve, lambda question, rows: [0.1, 0.9, 0.4],
                                     candidate_count=20)
        results = reranker.retrieve("question", 2)
        self.assertEqual(calls, [("question", 20)])
        self.assertEqual([row["chunk_id"] for row in results], ["b", "c"])
        self.assertEqual([row["rerank_score"] for row in results], [0.9, 0.4])

    def test_equal_scores_preserve_candidate_order(self):
        candidates = [chunk("a"), chunk("b")]
        reranker = RerankedRetriever(lambda *args: candidates,
                                     lambda *args: [0.5, 0.5])
        self.assertEqual([row["chunk_id"] for row in reranker.retrieve("q", 2)],
                         ["a", "b"])

    def test_empty_candidates_do_not_call_model(self):
        def forbidden(*args):
            self.fail("The score model should not be called")
        reranker = RerankedRetriever(lambda *args: [], forbidden)
        self.assertEqual(reranker.retrieve("q", 5), [])

    def test_invalid_scores_are_rejected(self):
        candidates = [chunk("a"), chunk("b")]
        for scores in ([0.1], [0.1, float("nan")], [0.1, float("inf")]):
            reranker = RerankedRetriever(lambda *args: candidates,
                                         lambda *args, value=scores: value)
            with self.assertRaises(ValueError):
                reranker.retrieve("q", 1)

    def test_invalid_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            RerankedRetriever(lambda *args: [], candidate_count=0)
        with self.assertRaises(ValueError):
            RerankedRetriever(lambda *args: []).retrieve("q", 0)


if __name__ == "__main__":
    unittest.main()
