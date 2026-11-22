# Evaluation set — frozen benchmark v1

50 evidence-backed questions cover all 12 frozen FastAPI tutorial pages.
The content was frozen before its one-time reserved-test run on 22 November
2026. See `BENCHMARK_FREEZE_v1.md` and `benchmark-freeze-v1.json` for the exact
contract and limitations. The legacy filename `questions.draft.jsonl` is kept
to avoid invalidating historical signed run manifests.

| Category | Development | Reserved test | Total |
|---|---:|---:|---:|
| Direct | 12 | 3 | 15 |
| Similar content | 8 | 2 | 10 |
| Multi-part | 6 | 2 | 8 |
| Paraphrase | 10 | 2 | 12 |
| Unanswerable | 4 | 1 | 5 |
| Total | 40 | 10 | 50 |

Only development questions were used while building and selecting the pipeline.
The reserved split was evaluated once after the v1 freeze. Concepts and source pages
overlap between splits, so this is not a claim of independent domain generalization.
All 50 references received an AI-assisted cross-check and exact evidence
validation. Full item-by-item author review is incomplete; `REVIEW.md` preserves
that status and the review history.

Run from the repository root:

    python -m src.evaluation.validate
    python -m unittest discover -s tests -v

Each JSONL record has: id, category (direct, similar_page, multi_part,
paraphrase, unanswerable), split (dev or test), question, answerable (boolean),
reference_answer, gold_sources (filenames), and evidence (source/quote objects).
All evidence items are required. Quotes are exact substrings of the normalized
document text used by the pipeline; Markdown is retained. Sources must each
have evidence. Gold labels do not depend on chunk IDs.

Unanswerable records have empty sources/evidence and the expected refusal as
their reference. The validator checks structure, uniqueness, source existence,
and exact evidence presence. It does not prove correctness or unanswerability.

The frozen dataset hash is recorded in the v1 manifest. Do not revise labels
because a pipeline scored poorly. METRICS.md version 2 defines deterministic
retrieval scoring. Answer judging has fresh mixed human calibration; see
`calibration/2026-11-14` and JUDGING.md.

See RUNNING_EVAL.md for observation capture and offline report commands.
