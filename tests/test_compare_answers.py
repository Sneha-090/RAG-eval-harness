import math
import unittest

from src.evaluation.compare_answers import build_comparison


class CompareAnswersTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {'id': 'q1', 'category': 'direct', 'answerable': True},
            {'id': 'q2', 'category': 'unanswerable', 'answerable': False},
        ]
        files = {'data/raw/doc.md': 'corpus'}
        base_contract = {'mode': 'answers', 'config': 'A', 'k': 5, 'files': files,
                         'generator': {'provider': 'test', 'model': 'generator'},
                         'prompt_sha256': 'answer-prompt', 'embedding_model': 'embedding'}
        candidate_contract = {**base_contract, 'config': 'B'}
        self.baseline_capture = {'signature': 'capture-a', 'dataset': self.rows,
                                 'contract': base_contract}
        self.candidate_capture = {'signature': 'capture-b', 'dataset': self.rows,
                                  'contract': candidate_contract}
        self.baseline_observations = [
            {'id': 'q1', 'status': 'ok', 'answer': 'A1', 'chunks': [{'text': 'a'}],
             'retrieval_s': 1.0, 'generation_s': 2.0},
            {'id': 'q2', 'status': 'ok', 'answer': 'A2', 'chunks': [{'text': 'b'}],
             'retrieval_s': 2.0, 'generation_s': 4.0},
        ]
        self.candidate_observations = [
            {'id': 'q1', 'status': 'ok', 'answer': 'B1', 'chunks': [{'text': 'c'}],
             'retrieval_s': 1.5, 'generation_s': 1.0},
            {'id': 'q2', 'status': 'ok', 'answer': 'B2', 'chunks': [{'text': 'd'}],
             'retrieval_s': 2.5, 'generation_s': 2.0},
        ]
        judge_contract_a = {'capture_signature': 'capture-a',
                            'judge': {'provider': 'test', 'model': 'judge'},
                            'prompt_sha256': 'judge-prompt'}
        judge_contract_b = {**judge_contract_a, 'capture_signature': 'capture-b'}
        self.baseline_judge = {'contract': judge_contract_a, 'signature': 'judge-a'}
        self.candidate_judge = {'contract': judge_contract_b, 'signature': 'judge-b'}
        self.baseline_verdicts = [
            {'id': 'q1', 'verdict': {'correctness': .5, 'faithfulness': 0,
                                     'abstention': None, 'reason': 'Partial'}},
            {'id': 'q2', 'verdict': {'correctness': None, 'faithfulness': None,
                                     'abstention': 1, 'reason': 'Refused'}},
        ]
        self.candidate_verdicts = [
            {'id': 'q1', 'verdict': {'correctness': 1, 'faithfulness': 1,
                                     'abstention': None, 'reason': 'Better'}},
            {'id': 'q2', 'verdict': {'correctness': None, 'faithfulness': None,
                                     'abstention': 0, 'reason': 'Invented'}},
        ]

    def build(self):
        return build_comparison(
            self.baseline_capture, self.baseline_observations, self.baseline_judge,
            self.baseline_verdicts, self.candidate_capture, self.candidate_observations,
            self.candidate_judge, self.candidate_verdicts)

    def test_paired_scores_and_latency(self):
        report = self.build()
        self.assertEqual(report['paired_deltas']['correctness']['improved'], 1)
        self.assertEqual(report['paired_deltas']['faithfulness']['mean_delta'], 1)
        self.assertEqual(report['paired_deltas']['abstention']['regressed'], 1)
        self.assertEqual(report['latency']['candidate']['answer_successful_stages']['mean_s'], 3.5)
        self.assertEqual(report['questions'][0]['answers'], {'baseline': 'A1', 'candidate': 'B1'})
        self.assertEqual(report['questions'][0]['retrieved_context']['candidate'], [{'text': 'c'}])
        self.assertFalse(report['winner_claim_allowed'])

    def test_confounded_inputs_are_rejected(self):
        candidate_contract = self.candidate_capture['contract']
        baseline_contract = self.baseline_capture['contract']
        if not isinstance(candidate_contract, dict) or not isinstance(baseline_contract, dict):
            self.fail('Invalid test fixture')
        candidate_contract['generator'] = {'provider': 'other', 'model': 'x'}
        with self.assertRaisesRegex(ValueError, 'same_generator'):
            self.build()
        candidate_contract['generator'] = baseline_contract['generator']
        self.candidate_capture['dataset'] = [dict(self.rows[0], id='different'), self.rows[1]]
        with self.assertRaisesRegex(ValueError, 'identical question'):
            self.build()

    def test_invalid_latency_and_agreement_are_rejected(self):
        self.candidate_observations[0]['generation_s'] = math.nan
        with self.assertRaisesRegex(ValueError, 'Invalid latency'):
            self.build()
        self.candidate_observations[0]['generation_s'] = 1.0
        agreement = {'agreement_measured': True, 'judge_signature': 'wrong'}
        with self.assertRaisesRegex(ValueError, 'Human agreement'):
            build_comparison(
                self.baseline_capture, self.baseline_observations, self.baseline_judge,
                self.baseline_verdicts, self.candidate_capture, self.candidate_observations,
                self.candidate_judge, self.candidate_verdicts, agreement)


if __name__ == '__main__':
    unittest.main()
