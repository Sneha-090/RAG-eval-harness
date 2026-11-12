"""Fail when a fresh retrieval report regresses below the frozen policy."""
import argparse
import json
import math
from pathlib import Path

METRICS = ("hit_at_k", "mrr_at_k", "source_recall_at_k",
           "evidence_coverage_at_k", "evidence_complete_at_k")
EPSILON = 1e-12


def _number(value, label, failures, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        failures.append(f"{label} must be a finite number")
        return None
    if minimum is not None and value < minimum:
        failures.append(f"{label} must be at least {minimum}")
    if maximum is not None and value > maximum:
        failures.append(f"{label} must be at most {maximum}")
    return value


def check_gate(policy, manifest, report):
    """Return human-readable failures; an empty list means PASS."""
    failures = []
    expected = policy.get("expected", {})
    baseline = policy.get("baseline", {})
    allowed = policy.get("allowed_regression", {})
    contract = manifest.get("contract", {})

    if policy.get("version") != 1:
        failures.append("policy version must be 1")
    for key in ("config", "mode", "k", "dataset_sha256", "embedding_model", "chunking"):
        if contract.get(key) != expected.get(key):
            failures.append(f"contract {key} differs from the policy")
    if report.get("run_signature") != manifest.get("signature"):
        failures.append("report and manifest signatures differ")
    if report.get("metrics_sha256") != expected.get("metrics_sha256"):
        failures.append("metric contract hash differs from the policy")
    if report.get("scorer_sha256") != expected.get("scorer_sha256"):
        failures.append("retrieval scorer hash differs from the policy")
    if report.get("splits") != [expected.get("split")]:
        failures.append("report split differs from the policy")
    if report.get("requested") != expected.get("requested"):
        failures.append("requested question count differs from the policy")
    if report.get("answerable_requested") != expected.get("answerable_count"):
        failures.append("answerable question count differs from the policy")
    if report.get("retrieval_complete") is not True:
        failures.append("retrieval run is incomplete")
    if report.get("answerable_missing_retrieval") != 0:
        failures.append("answerable retrievals are missing")

    overall = report.get("overall", {})
    if overall.get("count") != expected.get("answerable_count"):
        failures.append("scored answerable count differs from the policy")
    for metric in METRICS:
        actual = _number(overall.get(metric), f"actual {metric}", failures, 0, 1)
        reference = _number(baseline.get(metric), f"baseline {metric}", failures, 0, 1)
        tolerance = _number(allowed.get(metric), f"allowed regression {metric}", failures, 0, 1)
        if None not in (actual, reference, tolerance):
            threshold = reference - tolerance
            if actual + EPSILON < threshold:
                failures.append(
                    f"{metric} regressed: actual {actual:.6f} < threshold {threshold:.6f}"
                )

    questions = report.get("questions")
    if not isinstance(questions, list):
        failures.append("report questions must be a list")
        complete_count = None
    else:
        complete_count = sum(
            row.get("scores", {}).get("evidence_complete_at_k") == 1
            for row in questions if isinstance(row, dict) and isinstance(row.get("scores"), dict)
        )
    baseline_count = _number(baseline.get("complete_evidence_count"),
                             "baseline complete evidence count", failures, 0)
    count_tolerance = _number(allowed.get("complete_evidence_count"),
                              "allowed complete evidence count regression", failures, 0)
    if complete_count is not None and None not in (baseline_count, count_tolerance):
        threshold = baseline_count - count_tolerance
        if complete_count < threshold:
            failures.append(
                f"complete evidence count regressed: actual {complete_count} < threshold {threshold:g}"
            )
    return failures


def load_inputs(run_dir, policy_path):
    policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads((run_dir / "evaluation.json").read_text(encoding="utf-8"))
    return policy, manifest, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("quality-gate.json"))
    args = parser.parse_args()
    try:
        policy, manifest, report = load_inputs(args.run, args.policy)
        failures = check_gate(policy, manifest, report)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Quality gate could not run: {exc}\n")
    if failures:
        print("FAIL: retrieval quality gate")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    complete = policy["baseline"]["complete_evidence_count"]
    print(f"PASS: retrieval quality gate (complete evidence >= {complete})")


if __name__ == "__main__":
    main()
