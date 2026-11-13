import math
import unittest

from src.evaluation.answer_report import build_report, latency_summary
from src.evaluation.run import digest


class AnswerReportTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {'id': 'q1', 'category': 'direct', 'answerable': True},
            {'id': 'q2', 'category': 'unanswerable', 'answerable': False},
        ]
        self.observations = [
            {'id': 'q1', 'status': 'ok', 'answer': 'Answer', 'chunks': [],
             'retrieval_s': 1.0, 'generation_s': 2.0, 'resumed': True},
            {'id': 'q2', 'status': 'ok', 'answer': 'Cannot answer', 'chunks': [],
             'retrieval_s': 2.0, 'generation_s': 4.0, 'resumed': False},
        ]
        self.capture = {'signature': 'capture', 'dataset': self.rows,
                        'contract': {'mode': 'answers', 'config': 'A',
                                     'generator': {'provider': 'test', 'model': 'generator'}}}
        self.verdicts = [
            {'id': 'q1', 'status': 'ok', 'judge_s': 3.0,
             'verdict': {'correctness': .5, 'faithfulness': 0,
                         'abstention': None, 'reason': 'Partial'}},
            {'id': 'q2', 'status': 'ok', 'judge_s': 6.0,
             'verdict': {'correctness': None, 'faithfulness': None,
                         'abstention': 1, 'reason': 'Refused'}},
        ]
        contract = {'capture_signature': 'capture',
                    'judge': {'provider': 'test', 'model': 'judge'}}
        self.judge = {'contract': contract, 'dataset': self.rows,
                      'observations': self.observations}
        self.judge['signature'] = digest({'rows': self.rows, 'observations': self.observations,
                                          'contract': contract})
        self.agreement = {'agreement_measured': True, 'judge_signature': self.judge['signature'],
                          'sample_size': 10, 'exact_agreement': {'correctness': .9, 'faithfulness': .8},
                          'disagreements': [{}, {}]}

    def test_scores_and_successful_stage_latency_are_separate(self):
        report = build_report(self.capture, self.observations, self.judge,
                              self.verdicts, self.agreement)
        self.assertEqual(report['answer_quality']['correctness']['score_sum'], .5)
        self.assertEqual(report['answer_quality']['faithfulness']['mean'], 0)
        self.assertEqual(report['answer_quality']['abstention']['mean'], 1)
        self.assertEqual(report['latency']['answer_successful_stages'],
                         {'count': 2, 'mean_s': 4.5, 'p95_s': 6.0})
        self.assertEqual(report['latency']['resumed_question_count'], 1)

    def test_nearest_rank_p95_and_invalid_latency(self):
        self.assertEqual(latency_summary(list(range(1, 21)))['p95_s'], 19)
        for value in (-1, math.nan, math.inf, True, '1'):
            with self.assertRaises(ValueError):
                latency_summary([value])

    def test_mismatched_inputs_are_rejected(self):
        self.agreement['judge_signature'] = 'wrong'
        with self.assertRaises(ValueError):
            build_report(self.capture, self.observations, self.judge,
                         self.verdicts, self.agreement)
        self.agreement['judge_signature'] = self.judge['signature']
        self.observations[0]['generation_s'] = math.nan
        with self.assertRaises(ValueError):
            build_report(self.capture, self.observations, self.judge,
                         self.verdicts, self.agreement)


if __name__ == '__main__':
    unittest.main()
