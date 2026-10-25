import copy
import unittest

from src.evaluation.validate import validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(id="q001", category="direct", split="dev", question="Why?",
                        answerable=True, reference_answer="A fact.", gold_sources=["a.md"],
                        evidence=[dict(source="a.md", quote="A fact.")])
        self.docs = {"a.md": "A fact. Another fact."}

    def test_valid_record(self):
        self.assertEqual(validate([self.row], self.docs), [])

    def test_missing_evidence_is_rejected(self):
        self.row["evidence"][0]["quote"] = "Invented fact."
        self.assertTrue(any("not found" in e for e in validate([self.row], self.docs)))

    def test_duplicate_question_is_rejected(self):
        second = copy.deepcopy(self.row)
        second["id"] = "q002"
        second["question"] = " WHY? "
        self.assertTrue(any("duplicate question" in e for e in validate([self.row, second], self.docs)))

    def test_source_without_evidence_is_rejected(self):
        self.row["gold_sources"].append("b.md")
        self.docs["b.md"] = "Other fact."
        self.assertTrue(any("each gold source" in e for e in validate([self.row], self.docs)))

    def test_unanswerable_cannot_have_evidence(self):
        self.row.update(category="unanswerable", answerable=False)
        self.assertTrue(any("must have empty" in e for e in validate([self.row], self.docs)))

    def test_bad_types_return_errors(self):
        self.row.update(category=[], answerable="true", gold_sources=None)
        self.assertGreaterEqual(len(validate([self.row], self.docs)), 3)


if __name__ == "__main__":
    unittest.main()
