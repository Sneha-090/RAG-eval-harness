import unittest

from src.retrieval.hybrid import BM25, HybridRetriever, fuse


def chunk(key, text):
    return {"chunk_id": key, "doc_id": "sample.md", "text": text}


class HybridTests(unittest.TestCase):
    def test_keyword_search_retains_underscore_and_filters_misses(self):
        matching = chunk("m", "Use response_model to set the output type.")
        index = BM25([matching, chunk("u", "Use response model documentation.")])
        self.assertEqual(index.search("What does RESPONSE_MODEL do?", 5), [matching])
        self.assertEqual(index.search("unrelated", 5), [])

    def test_agreement_ranks_first_and_results_are_unique(self):
        shared, dense, lexical = chunk("s", "shared"), chunk("d", "dense"), chunk("l", "lexical")
        results = fuse([dense, shared], [lexical, shared], 2)
        self.assertEqual([row["chunk_id"] for row in results], ["s", "d"])

    def test_hybrid_can_find_keyword_hit_outside_dense_candidates(self):
        dense, lexical = chunk("a", "general guide"), chunk("z", "response_model")
        calls = []

        def search(question, k):
            calls.append((question, k))
            return [dense]

        results = HybridRetriever([dense, lexical], search).retrieve("response_model", 2)
        self.assertEqual(calls, [("response_model", 2)])
        self.assertEqual([row["chunk_id"] for row in results], ["a", "z"])
