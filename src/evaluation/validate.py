"""Validate draft JSONL questions against the normalized frozen corpus."""
import argparse
import json
from collections import Counter
from pathlib import Path

from src.ingestion.loader import load_documents

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {"direct", "similar_page", "multi_part", "paraphrase", "unanswerable"}
FIELDS = {"id", "category", "split", "question", "answerable", "reference_answer", "gold_sources", "evidence"}


def validate(records, documents):
    """Return all errors; evidence is an exact substring after loader normalization."""
    errors, ids, questions = [], set(), set()
    for index, row in enumerate(records, 1):
        label = f"record {index}"
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append(f"{label}: expected exactly {sorted(FIELDS)}")
            continue
        for field in ("id", "question", "reference_answer"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"{label}: {field} must be a nonempty string")
        for field, seen in (("id", ids), ("question", questions)):
            value = row[field]
            if isinstance(value, str):
                key = " ".join(value.lower().split())
                if key in seen:
                    errors.append(f"{label}: duplicate {field}")
                seen.add(key)
        if not isinstance(row["category"], str) or row["category"] not in CATEGORIES:
            errors.append(f"{label}: invalid category")
        if row["split"] not in ("dev", "test"):
            errors.append(f"{label}: split must be dev or test")
        if type(row["answerable"]) is not bool:
            errors.append(f"{label}: answerable must be a boolean")
        elif row["answerable"] == (row["category"] == "unanswerable"):
            errors.append(f"{label}: category conflicts with answerable")
        sources, evidence = row["gold_sources"], row["evidence"]
        if not isinstance(sources, list) or not all(isinstance(s, str) for s in sources):
            errors.append(f"{label}: gold_sources must be a list of strings")
            continue
        if len(sources) != len(set(sources)):
            errors.append(f"{label}: duplicate gold source")
        if not isinstance(evidence, list):
            errors.append(f"{label}: evidence must be a list")
            continue
        if row["answerable"] and (not sources or not evidence):
            errors.append(f"{label}: answerable questions require sources and evidence")
        if row["answerable"] is False and (sources or evidence):
            errors.append(f"{label}: unanswerable questions must have empty sources and evidence")
        for source in sources:
            if source not in documents:
                errors.append(f"{label}: unknown source {source}")
        covered = set()
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {"source", "quote"}:
                errors.append(f"{label}: evidence needs source and quote")
                continue
            source, quote = item["source"], item["quote"]
            if not isinstance(source, str) or source not in sources:
                errors.append(f"{label}: evidence source must be in gold_sources")
                continue
            covered.add(source)
            if not isinstance(quote, str) or not quote.strip():
                errors.append(f"{label}: empty evidence quote")
            elif quote not in documents.get(source, ""):
                errors.append(f"{label}: evidence not found in {source}")
        if set(sources) - covered:
            errors.append(f"{label}: each gold source needs evidence")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=Path, default=ROOT / "data/eval/questions.draft.jsonl")
    args = parser.parse_args()
    try:
        records = [json.loads(line) for line in args.dataset.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not records:
            raise ValueError("dataset is empty")
        documents = {d.doc_id: d.text for d in load_documents(ROOT / "data/raw")}
        errors = validate(records, documents)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    if errors:
        parser.exit(1, "Validation failed:\n" + "\n".join(errors) + "\n")
    print(f"PASS: {len(records)} records; all evidence exists in the corpus.")
    print(f"Categories: {dict(Counter(r['category'] for r in records))}")
    print("Structural validation does not establish answer correctness or unanswerability.")


if __name__ == "__main__":
    main()
