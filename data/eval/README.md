# Evaluation set (draft, version 0.1)

Milestone 3 is in progress. The first 10 records are author-review candidates,
not a frozen benchmark or measured results. All are development questions;
reserve held-out test questions when expanding to approximately 50 records.
Do not tune against the held-out set.

Run from the repository root (Python standard library only):

    python -m src.evaluation.validate
    python -m unittest discover -s tests -v

Each JSONL record has: id, category (direct, similar_page, multi_part,
paraphrase, unanswerable), split (dev or test), question, answerable (boolean),
reference_answer, gold_sources (filenames), and evidence (source/quote objects).
Answerable records require evidence for every source. Quotes are exact substrings
of the normalized document text used by the pipeline; Markdown is retained.
Unanswerable records have empty source and evidence lists. Their reference
answer describes the expected refusal.

The validator checks structure, uniqueness, source existence, and exact evidence
presence. It cannot establish that the evidence fully supports the reference
answer or that an unanswerable question is absent from every page. Human review
must check these, question ambiguity, and coverage of all requested facts.

Next: review this batch, expand coverage across all 12 pages, choose the final
dev/test allocation, and freeze the dataset with a content hash. Before scoring,
version METRICS.md to define evidence coverage and multi-source scoring. Existing
page-level Hit@K remains unchanged until that contract is agreed. Evidence must
be independent of chunk IDs so chunking methods can be compared fairly.
