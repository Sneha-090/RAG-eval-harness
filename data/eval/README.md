# Evaluation set — draft version 0.2

50 evidence-backed questions cover all 12 frozen FastAPI tutorial pages.
This is a draft benchmark, not a human-approved or frozen evaluation set.

| Category | Development | Reserved test | Total |
|---|---:|---:|---:|
| Direct | 12 | 3 | 15 |
| Similar content | 8 | 2 | 10 |
| Multi-part | 6 | 2 | 8 |
| Paraphrase | 10 | 2 | 12 |
| Unanswerable | 4 | 1 | 5 |
| Total | 40 | 10 | 50 |

Only development questions are run while building and tuning the pipeline.
Reserved test questions have not been evaluated. Concepts and source pages
overlap between splits, so this is not a claim of independent domain generalization.
The author must review wording, reference correctness, sufficient evidence,
ambiguity, related-question leakage and absence of answers for unanswerable items
before freezing this version. REVIEW.md provides the complete review sheet.

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

The developer may correct factual/format errors during review, recording the
reason and changing the dataset hash. Do not revise labels because a pipeline
scored poorly. After human review, create a named dataset version and content
hash before comparison experiments. METRICS.md version 2 defines deterministic
retrieval scoring. Provisional answer judging is implemented; human judge validation remains pending (see JUDGING.md).

See RUNNING_EVAL.md for observation capture and offline report commands.
