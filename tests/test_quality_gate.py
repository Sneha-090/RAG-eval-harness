import copy
import unittest

from src.evaluation.gate import check_gate


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.policy = {
            "version": 1,
            "expected": {
                "config": "B", "mode": "retrieval", "split": "dev", "k": 5,
                "requested": 40, "answerable_count": 36, "dataset_sha256": "data",
                "metrics_sha256": "metrics", "scorer_sha256": "scorer",
                "embedding_model": "embed", "chunking": {"strategy": "semantic"},
            },
            "baseline": {
                "hit_at_k": 1.0, "mrr_at_k": 0.95, "source_recall_at_k": 1.0,
                "evidence_coverage_at_k": 0.84, "evidence_complete_at_k": 29 / 36,
                "complete_evidence_count": 29,
            },
            "allowed_regression": {
                "hit_at_k": 0.0, "mrr_at_k": 0.01, "source_recall_at_k": 0.0,
                "evidence_coverage_at_k": 0.005, "evidence_complete_at_k": 0.0,
                "complete_evidence_count": 0,
            },
        }
        self.manifest = {
            "signature": "run",
            "contract": {
                "config": "B", "mode": "retrieval", "k": 5,
                "dataset_sha256": "data", "embedding_model": "embed",
                "chunking": {"strategy": "semantic"},
            },
        }
        self.report = {
            "run_signature": "run", "metrics_sha256": "metrics", "scorer_sha256": "scorer",
            "splits": ["dev"], "requested": 40, "answerable_requested": 36,
            "answerable_missing_retrieval": 0, "retrieval_complete": True,
            "overall": {
                "count": 36, "hit_at_k": 1.0, "mrr_at_k": 0.95,
                "source_recall_at_k": 1.0, "evidence_coverage_at_k": 0.84,
                "evidence_complete_at_k": 29 / 36,
            },
            "questions": [
                {"scores": {"evidence_complete_at_k": int(index < 29)}}
                for index in range(36)
            ],
        }

    def test_matching_report_passes(self):
        self.assertEqual(check_gate(self.policy, self.manifest, self.report), [])

    def test_one_complete_evidence_loss_fails(self):
        report = copy.deepcopy(self.report)
        report["questions"][0]["scores"]["evidence_complete_at_k"] = 0
        report["overall"]["evidence_complete_at_k"] = 28 / 36
        failures = check_gate(self.policy, self.manifest, report)
        self.assertTrue(any("complete evidence count regressed" in item for item in failures))
        self.assertTrue(any("evidence_complete_at_k regressed" in item for item in failures))

    def test_metric_tolerance_is_enforced(self):
        passing = copy.deepcopy(self.report)
        passing["overall"]["mrr_at_k"] = 0.94
        self.assertEqual(check_gate(self.policy, self.manifest, passing), [])
        passing["overall"]["mrr_at_k"] = 0.939
        self.assertTrue(any("mrr_at_k regressed" in item
                            for item in check_gate(self.policy, self.manifest, passing)))

    def test_wrong_provenance_and_incomplete_run_fail(self):
        manifest = copy.deepcopy(self.manifest)
        report = copy.deepcopy(self.report)
        manifest["contract"]["config"] = "A"
        report["retrieval_complete"] = False
        report["answerable_missing_retrieval"] = 1
        failures = check_gate(self.policy, manifest, report)
        self.assertTrue(any("contract config" in item for item in failures))
        self.assertIn("retrieval run is incomplete", failures)
        self.assertIn("answerable retrievals are missing", failures)

    def test_non_finite_metric_fails(self):
        report = copy.deepcopy(self.report)
        report["overall"]["mrr_at_k"] = float("nan")
        self.assertTrue(any("finite number" in item
                            for item in check_gate(self.policy, self.manifest, report)))


if __name__ == "__main__":
    unittest.main()
