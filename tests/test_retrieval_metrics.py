import unittest

from src.evaluation.metrics import score_retrieval, summarize
from src.evaluation.report import render_markdown


class RetrievalMetricsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {'a.md': 'alpha beta gamma', 'b.md': 'other evidence', 'x.md': 'irrelevant'}
        self.row = dict(id='q1', category='multi_part', answerable=True,
                        gold_sources=['a.md', 'b.md'],
                        evidence=[{'source': 'a.md', 'quote': 'beta gamma'},
                                  {'source': 'b.md', 'quote': 'evidence'}])

    def chunk(self, source, text, suffix='0'):
        return {'chunk_id': f'{source}::{suffix}', 'doc_id': source, 'text': text}

    def test_page_hit_is_not_complete_evidence(self):
        chunks = [self.chunk('x.md', 'irrelevant'), self.chunk('a.md', 'alpha')]
        scores = score_retrieval(self.row, chunks, self.docs, 5)
        self.assertEqual(scores['hit_at_k'], 1)
        self.assertEqual(scores['mrr_at_k'], .5)
        self.assertEqual(scores['source_recall_at_k'], .5)
        self.assertEqual(scores['evidence_coverage_at_k'], 0)

    def test_union_covers_evidence_across_chunk_boundaries(self):
        chunks = [self.chunk('a.md', 'beta'), self.chunk('a.md', 'gamma', '1'),
                  self.chunk('b.md', 'evidence')]
        scores = score_retrieval(self.row, chunks, self.docs, 3)
        self.assertEqual(scores['evidence_coverage_at_k'], 1)
        self.assertEqual(scores['evidence_complete_at_k'], 1)

    def test_partial_coverage_and_overlap_do_not_double_count(self):
        chunks = [self.chunk('a.md', 'beta'), self.chunk('a.md', 'beta', '1')]
        scores = score_retrieval(self.row, chunks, self.docs, 5)
        self.assertAlmostEqual(scores['evidence_coverage_at_k'], (4/9)/2)

    def test_k_cutoff_and_empty_success(self):
        chunks = [self.chunk('x.md', 'irrelevant'), self.chunk('a.md', 'beta gamma')]
        self.assertEqual(score_retrieval(self.row, chunks, self.docs, 1)['hit_at_k'], 0)
        self.assertTrue(all(value == 0 for value in score_retrieval(self.row, [], self.docs, 5).values()))

    def test_unknown_source_or_fabricated_text_is_rejected(self):
        for source, text in [('missing.md', 'text'), ('a.md', 'fabricated')]:
            with self.assertRaises(ValueError):
                score_retrieval(self.row, [self.chunk(source, text)], self.docs, 5)

    def test_duplicate_chunk_id_is_rejected(self):
        chunk = self.chunk('a.md', 'beta')
        with self.assertRaises(ValueError):
            score_retrieval(self.row, [chunk, chunk], self.docs, 5)

    def test_unanswerable_and_missing_are_not_silent_zeros(self):
        unanswerable = dict(id='u1', category='unanswerable', answerable=False)
        report = summarize([self.row, unanswerable], [{'id': 'u1', 'chunks': [], 'status': 'ok', 'retrieval_s': 2}], self.docs, 5)
        self.assertEqual(report['overall']['count'], 0)
        self.assertIsNone(report['overall']['hit_at_k'])
        self.assertEqual(report['answerable_missing_retrieval'], 1)
        self.assertFalse(report['retrieval_complete'])
        self.assertEqual(report['retrieval_latency']['p95_s'], 2)
        self.assertIn('n/a', render_markdown(report))

    def test_generation_failure_keeps_retrieval_score(self):
        report = summarize([self.row], [{'id': 'q1', 'chunks': [], 'status': 'error'}], self.docs, 5)
        self.assertEqual(report['overall']['count'], 1)
        self.assertEqual(report['answerable_missing_retrieval'], 0)

    def test_repeated_quote_uses_best_occurrence(self):
        row = dict(answerable=True, gold_sources=['a.md'], evidence=[{'source': 'a.md', 'quote': 'word'}])
        scores = score_retrieval(row, [self.chunk('a.md', 'word tail')], {'a.md': 'word middle word tail'}, 5)
        self.assertEqual(scores['evidence_complete_at_k'], 1)

    def test_nearest_rank_p95(self):
        rows = [dict(id=str(i), answerable=False, category='unanswerable') for i in range(20)]
        observations = [dict(id=str(i), chunks=[], status='ok', retrieval_s=i+1) for i in range(20)]
        report = summarize(rows, observations, self.docs, 5)
        self.assertEqual(report['retrieval_latency']['p95_s'], 19)
        self.assertEqual(report['retrieval_latency']['mean_s'], 10.5)


if __name__ == '__main__':
    unittest.main()
