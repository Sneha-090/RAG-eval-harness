import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.human_review import (compare_packet, export_packet, parse_labels,
                                         parse_mixed_labels, parse_partial_labels,
                                         parse_partial_mixed_labels, save_partial_labels,
                                         save_partial_mixed_labels, select_mixed_sample,
                                         select_sample)
from src.evaluation.judge import judge_records
from src.evaluation.run import run_records


class HumanReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.capture = self.root / 'capture'
        self.packet = self.root / 'packet'
        self.judge = self.root / 'judge'
        self.rows = [dict(id=f'q{i:02}', question=f'Question {i}', reference_answer='Reference',
                          answerable=True, split='dev', category='direct' if i % 2 else 'paraphrase') for i in range(10)]
        run_records(self.rows, self.capture, {'k': 5, 'mode': 'answers'},
                    lambda q, k: [{'chunk_id': 'a::0', 'text': 'Context'}], lambda q, c: 'Answer')
        self.observations = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(self.capture.glob('record-*.json'))]

    def label_text(self):
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=['id','correctness','faithfulness','notes'])
        writer.writeheader()
        writer.writerows(dict(id=r['id'], correctness='1', faithfulness='0', notes='Synthetic unit-test labels') for r in self.rows)
        return buffer.getvalue()

    def prepare_judge(self):
        manifest = json.loads((self.capture / 'manifest.json').read_text(encoding='utf-8'))
        judge_records(self.rows, self.observations, self.judge, {'capture_signature': manifest['signature']},
                      lambda p: json.dumps(dict(correctness=1, faithfulness=1, abstention=None, reason='Synthetic test verdict')))

    def test_export_is_blind_and_labels_are_blank(self):
        count = export_packet(self.capture, self.packet)
        self.assertEqual(count, 10)
        labels = list(csv.DictReader((self.packet / 'labels.csv').read_text(encoding='utf-8').splitlines()))
        self.assertTrue(all(r['correctness'] == r['faithfulness'] == '' for r in labels))
        packet = json.loads((self.packet / 'packet.json').read_text(encoding='utf-8'))
        self.assertNotIn('verdict', json.dumps(packet))
        with self.assertRaises(FileExistsError):
            export_packet(self.capture, self.packet)

    def test_insufficient_or_test_answers_do_not_enter_sample(self):
        self.rows[0]['split'] = 'test'
        with self.assertRaises(ValueError):
            select_sample(self.rows, self.observations)
        with self.assertRaises(ValueError):
            select_sample(self.rows, self.observations, 20)

    def test_blank_unknown_duplicate_and_incomplete_labels_rejected(self):
        identifiers = {r['id'] for r in self.rows}
        export_packet(self.capture, self.packet)
        with self.assertRaises(ValueError):
            parse_labels((self.packet / 'labels.csv').read_text(encoding='utf-8'), identifiers)
        text = self.label_text()
        self.assertEqual(len(parse_labels(text, identifiers)), 10)
        for bad in [text.replace('q00', 'unknown'), text.replace('q01', 'q00'),
                    '\n'.join(text.splitlines()[:-1]), text.replace(',1,0,', ',0.7,0,')]:
            with self.assertRaises(ValueError):
                parse_labels(bad, identifiers)

    def test_partial_labels_round_trip_without_losing_notes(self):
        export_packet(self.capture, self.packet)
        path = self.packet / 'labels.csv'
        identifiers = [row['id'] for row in self.rows]
        labels = parse_partial_labels(path.read_text(encoding='utf-8'), set(identifiers))
        labels['q00'] = {'correctness': .5, 'faithfulness': 0, 'notes': 'Needs a closer look, later.'}
        save_partial_labels(path, identifiers, labels)
        restored = parse_partial_labels(path.read_text(encoding='utf-8'), set(identifiers))
        self.assertEqual(restored['q00'], labels['q00'])
        self.assertIsNone(restored['q01']['correctness'])
        with self.assertRaises(ValueError):
            parse_labels(path.read_text(encoding='utf-8'), set(identifiers))

    def test_exact_agreement_and_disagreements_separate(self):
        export_packet(self.capture, self.packet)
        self.prepare_judge()
        labels = self.root / 'human.csv'
        labels.write_text(self.label_text(), encoding='utf-8')
        report = compare_packet(self.packet / 'packet.json', labels, self.judge)
        self.assertEqual(report['exact_agreement'], {'correctness': 1, 'faithfulness': 0})
        self.assertEqual(len(report['disagreements']), 10)

    def test_changed_packet_is_rejected(self):
        export_packet(self.capture, self.packet)
        path = self.packet / 'packet.json'
        packet = json.loads(path.read_text(encoding='utf-8'))
        packet['items'][0]['observation']['answer'] = 'Changed'
        path.write_text(json.dumps(packet), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'signature mismatch'):
            compare_packet(path, self.packet / 'labels.csv', self.judge)

    def test_mismatched_judge_capture_is_rejected(self):
        export_packet(self.capture, self.packet)
        self.prepare_judge()
        path = self.judge / 'manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        manifest['contract']['capture_signature'] = 'wrong'
        path.write_text(json.dumps(manifest), encoding='utf-8')
        labels = self.root / 'human.csv'
        labels.write_text(self.label_text(), encoding='utf-8')
        with self.assertRaises(ValueError):
            compare_packet(self.packet / 'packet.json', labels, self.judge)

    def test_mixed_packet_labels_and_three_metric_agreement(self):
        mixed_capture = self.root / 'mixed-capture'
        mixed_packet = self.root / 'mixed-packet'
        mixed_judge = self.root / 'mixed-judge'
        rows = [dict(id=f'm{i:02}', question=f'Question {i}', reference_answer='Reference',
                     answerable=i < 8, split='dev',
                     category=('unanswerable' if i >= 8 else ['direct', 'multi_part',
                               'paraphrase', 'similar_page'][i % 4])) for i in range(10)]
        run_records(rows, mixed_capture, {'k': 5, 'mode': 'answers'},
                    lambda q, k: [{'chunk_id': 'a::0', 'text': 'Context'}],
                    lambda q, c: 'Cannot answer' if q in {'Question 8', 'Question 9'} else 'Answer')
        observations = [json.loads(path.read_text(encoding='utf-8'))
                        for path in sorted(mixed_capture.glob('record-*.json'))]
        selected = select_mixed_sample(rows, observations, 10)
        self.assertEqual(sum(not item['row']['answerable'] for item in selected), 2)
        self.assertEqual(export_packet(mixed_capture, mixed_packet, 10, mixed=True), 10)
        packet = json.loads((mixed_packet / 'packet.json').read_text(encoding='utf-8'))
        self.assertEqual(packet['version'], 2)
        answerability = {row['id']: row['answerable'] for row in rows}
        labels = parse_partial_mixed_labels(
            (mixed_packet / 'labels.csv').read_text(encoding='utf-8'), answerability)
        for identifier, answerable in answerability.items():
            labels[identifier] = ({'correctness': 1.0, 'faithfulness': 1,
                                   'abstention': None, 'notes': ''} if answerable else
                                  {'correctness': None, 'faithfulness': None,
                                   'abstention': 1, 'notes': ''})
        save_partial_mixed_labels(mixed_packet / 'labels.csv',
                                  [item['row']['id'] for item in packet['items']],
                                  labels, answerability)
        self.assertEqual(len(parse_mixed_labels(
            (mixed_packet / 'labels.csv').read_text(encoding='utf-8'), answerability)), 10)

        manifest = json.loads((mixed_capture / 'manifest.json').read_text(encoding='utf-8'))
        judge_records(rows, observations, mixed_judge,
                      {'capture_signature': manifest['signature']},
                      lambda prompt: json.dumps(
                          dict(correctness=1, faithfulness=1, abstention=None,
                               reason='Supported') if '"answerable": true' in prompt else
                          dict(correctness=None, faithfulness=None, abstention=1,
                               reason='Correct refusal')))
        agreement = compare_packet(mixed_packet / 'packet.json',
                                   mixed_packet / 'labels.csv', mixed_judge)
        self.assertEqual(agreement['metric_sample_size'],
                         {'correctness': 8, 'faithfulness': 8, 'abstention': 2})
        self.assertEqual(agreement['exact_agreement'],
                         {'correctness': 1, 'faithfulness': 1, 'abstention': 1})


if __name__ == '__main__':
    unittest.main()
