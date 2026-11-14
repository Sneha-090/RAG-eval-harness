import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from src.evaluation.human_review import parse_partial_labels, parse_partial_mixed_labels
from src.evaluation.run import digest


class ReviewAppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet_path = self.root / 'packet.json'
        self.labels_path = self.root / 'labels.csv'
        items = []
        for index in range(10):
            identifier = f'q{index:02}'
            items.append({'row': {'id': identifier, 'question': f'Question {index}',
                                  'reference_answer': 'Reference answer', 'answerable': True,
                                  'split': 'dev', 'category': 'direct'},
                          'observation': {'id': identifier, 'status': 'ok', 'answer': 'Generated answer',
                                          'chunks': [{'chunk_id': 'doc.md::0', 'text': 'Supporting context'}]}})
        payload = {'capture_signature': 'capture', 'items': items}
        self.packet_path.write_text(json.dumps({'version': 1, **payload,
                                                'signature': digest(payload)}), encoding='utf-8')
        with self.labels_path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['id', 'correctness', 'faithfulness', 'notes'])
            writer.writerows((item['row']['id'], '', '', '') for item in items)

    def test_review_saves_one_blind_label_and_moves_forward(self):
        app = Path(__file__).parents[1] / 'streamlit_app.py'
        environment = {'RAG_REVIEW_PACKET': str(self.packet_path),
                       'RAG_REVIEW_LABELS': str(self.labels_path)}
        with patch.dict(os.environ, environment):
            view = AppTest.from_file(app, default_timeout=10).run()
            self.assertFalse(view.exception)
            self.assertEqual(view.title[0].value, 'Blind RAG answer review')
            view.segmented_control(key='correctness_q00').set_value(1.0)
            view.segmented_control(key='faithfulness_q00').set_value(1)
            view.text_area(key='notes_q00').set_value('Checked against the displayed context.')
            view.form_submit_button[0].click().run()
            self.assertFalse(view.exception)
            self.assertEqual(view.session_state.get('review_item'), 'q01')

        labels = parse_partial_labels(self.labels_path.read_text(encoding='utf-8'),
                                      {f'q{index:02}' for index in range(10)})
        self.assertEqual(labels['q00'], {'correctness': 1.0, 'faithfulness': 1,
                                         'notes': 'Checked against the displayed context.'})
        self.assertIsNone(labels['q01']['correctness'])

    def test_unanswerable_review_saves_only_abstention(self):
        packet = json.loads(self.packet_path.read_text(encoding='utf-8'))
        packet['version'] = 2
        packet['items'][0]['row']['answerable'] = False
        packet['items'][0]['row']['category'] = 'unanswerable'
        payload = {'capture_signature': packet['capture_signature'], 'items': packet['items']}
        packet['signature'] = digest(payload)
        self.packet_path.write_text(json.dumps(packet), encoding='utf-8')
        with self.labels_path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['id', 'correctness', 'faithfulness', 'abstention', 'notes'])
            writer.writerows((item['row']['id'], '', '', '', '') for item in packet['items'])

        app = Path(__file__).parents[1] / 'streamlit_app.py'
        environment = {'RAG_REVIEW_PACKET': str(self.packet_path),
                       'RAG_REVIEW_LABELS': str(self.labels_path)}
        with patch.dict(os.environ, environment):
            view = AppTest.from_file(app, default_timeout=10).run()
            self.assertFalse(view.exception)
            view.segmented_control(key='abstention_q00').set_value(1)
            view.text_area(key='notes_q00').set_value('Correctly refused missing information.')
            view.form_submit_button[0].click().run()
            self.assertFalse(view.exception)
            self.assertEqual(view.session_state.get('review_item'), 'q01')

        answerability = {item['row']['id']: item['row']['answerable'] for item in packet['items']}
        labels = parse_partial_mixed_labels(self.labels_path.read_text(encoding='utf-8'), answerability)
        self.assertEqual(labels['q00'], {'correctness': None, 'faithfulness': None,
                                         'abstention': 1,
                                         'notes': 'Correctly refused missing information.'})


if __name__ == '__main__':
    unittest.main()
