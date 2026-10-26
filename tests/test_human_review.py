import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.human_review import compare_packet, export_packet, parse_labels, select_sample
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


if __name__ == '__main__':
    unittest.main()
