import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.run import run_records


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / 'run'
        self.rows = [{'id': 'q001', 'question': 'Question?'}]
        self.contract = {'k': 5}
        self.chunks = [{'chunk_id': 'a::0', 'doc_id': 'a', 'text': 'Evidence', 'similarity': .8}]
        self.addCleanup(self.temp.cleanup)

    def retrieve(self, question, k):
        return self.chunks

    def test_completed_run_never_repeats_calls(self):
        run_records(self.rows, self.output, self.contract, self.retrieve)
        def forbidden(*args):
            self.fail('Completed work was repeated')
        result = run_records(self.rows, self.output, self.contract, forbidden)
        self.assertEqual(result['completed'], 1)
        record = json.loads((self.output / 'record-0000.json').read_text())
        self.assertEqual(record['chunks'], self.chunks)

    def test_changed_inputs_refuse_resume(self):
        run_records(self.rows, self.output, self.contract, self.retrieve)
        with self.assertRaisesRegex(ValueError, 'inputs changed'):
            run_records(self.rows, self.output, {'k': 3}, self.retrieve)
        self.assertFalse((self.output / '.lock').exists())

    def test_generator_failure_preserves_retrieval_and_redacts_details(self):
        def failed(*args):
            raise RuntimeError('secret-token-must-not-be-written')
        first = run_records(self.rows, self.output, self.contract, self.retrieve, failed)
        self.assertEqual(first['failed'], 1)
        self.assertNotIn('secret-token', (self.output / 'record-0000.json').read_text())
        def forbidden(*args):
            self.fail('Retrieval should have been reused')
        second = run_records(self.rows, self.output, self.contract, forbidden,
                             lambda *args: 'Answer', retry_errors=True)
        self.assertEqual(second['completed'], 1)

    def test_errors_are_not_retried_without_flag(self):
        def failed(*args):
            raise TimeoutError()
        run_records(self.rows, self.output, self.contract, failed)
        result = run_records(self.rows, self.output, self.contract, self.retrieve)
        self.assertEqual(result['failed'], 1)

    def test_interruption_resumes_from_saved_retrieval(self):
        def interrupted(*args):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            run_records(self.rows, self.output, self.contract, self.retrieve, interrupted)
        self.assertFalse((self.output / '.lock').exists())
        result = run_records(self.rows, self.output, self.contract,
                             lambda *args: self.fail('Repeated retrieval'), lambda *args: 'Answer')
        self.assertEqual(result['completed'], 1)

    def test_empty_generation_is_failure(self):
        result = run_records(self.rows, self.output, self.contract, self.retrieve, lambda *args: '')
        self.assertEqual(result['failed'], 1)

    def test_concurrent_run_is_rejected(self):
        self.output.mkdir()
        (self.output / '.lock').write_text('123')
        with self.assertRaises(FileExistsError):
            run_records(self.rows, self.output, self.contract, self.retrieve)
        self.assertTrue((self.output / '.lock').exists())


if __name__ == '__main__':
    unittest.main()
