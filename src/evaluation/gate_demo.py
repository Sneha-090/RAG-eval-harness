"""Prove that the quality gate rejects a deliberately degraded report."""
import argparse
import copy
from pathlib import Path

from src.evaluation.gate import check_gate, load_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("quality-gate.json"))
    args = parser.parse_args()
    policy, manifest, report = load_inputs(args.run, args.policy)
    degraded = copy.deepcopy(report)
    for row in degraded["questions"]:
        scores = row.get("scores")
        if scores and scores["evidence_complete_at_k"] == 1:
            scores["evidence_complete_at_k"] = 0
            break
    degraded["overall"]["evidence_complete_at_k"] = (
        policy["baseline"]["complete_evidence_count"] - 1
    ) / policy["expected"]["answerable_count"]
    failures = check_gate(policy, manifest, degraded)
    if not any("complete evidence" in failure for failure in failures):
        raise SystemExit("FAIL: degraded report was not rejected")
    print("PASS: deliberate one-question degradation was rejected")


if __name__ == "__main__":
    main()
