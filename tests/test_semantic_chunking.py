import unittest

import numpy as np

from src.chunking.semantic import semantic_chunk_documents, semantic_chunk_text
from src.ingestion.loader import Document


def topic_embeddings(texts):
    vectors = []
    for text in texts:
        vectors.append([1.0, 0.0] if "alpha" in text else [0.0, 1.0])
    return np.array(vectors)


class SemanticChunkingTests(unittest.TestCase):
    def test_large_meaning_change_creates_exact_source_chunks(self):
        text = "alpha topic.\n\nalpha detail.\n\nunrelated topic.\n\nunrelated detail."
        chunks = semantic_chunk_text(text, topic_embeddings, min_chars=1,
                                     max_chars=200, breakpoint_percentile=75)
        self.assertEqual([piece for _, piece in chunks], [
            "alpha topic.\n\nalpha detail.",
            "unrelated topic.\n\nunrelated detail.",
        ])
        for start, piece in chunks:
            self.assertEqual(text[start:start + len(piece)], piece)

    def test_hard_maximum_splits_even_without_semantic_change(self):
        text = " ".join(["alpha"] * 30)
        chunks = semantic_chunk_text(text, topic_embeddings, min_chars=20,
                                     max_chars=45, unit_max_chars=45)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(piece) <= 45 for _, piece in chunks))

    def test_tiny_trailing_remainder_is_merged_when_it_fits(self):
        text = "alpha content with enough length.\n\nx"
        chunks = semantic_chunk_text(text, topic_embeddings, min_chars=20,
                                     max_chars=100)
        self.assertEqual(chunks, [(0, text)])

    def test_document_ids_are_deterministic_and_semantic_specific(self):
        docs = [Document("sample.md", "alpha one.\n\nunrelated two.")]
        chunks = semantic_chunk_documents(docs, topic_embeddings, min_chars=1,
                                          max_chars=100)
        self.assertEqual([chunk.chunk_id for chunk in chunks],
                         ["sample.md::s0", "sample.md::s1"])
        self.assertTrue(all(chunk.text in docs[0].text for chunk in chunks))

    def test_invalid_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            semantic_chunk_text("text", topic_embeddings, min_chars=0)
        with self.assertRaises(ValueError):
            semantic_chunk_text("text", topic_embeddings, min_chars=10, max_chars=5)
        with self.assertRaises(ValueError):
            semantic_chunk_text("text", topic_embeddings, breakpoint_percentile=101)


if __name__ == "__main__":
    unittest.main()
