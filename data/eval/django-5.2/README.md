# Django benchmark v2 draft

This folder is intentionally separate from the frozen FastAPI v1 benchmark.

## Current state

- 50 questions: 40 development and 10 reserved test.
- 45 answerable and 5 deliberately unanswerable.
- 15 direct, 10 similar-page, 8 multi-part, 12 paraphrase and 5
  unanswerable questions.
- All 12 pinned Django source files are represented.
- Every answerable item has exact evidence copied programmatically from the
  normalized local corpus.
- Structural/evidence validation passes.
- The question wording and reference answers are AI-assisted and need an
  author review before the benchmark is frozen.
- The reserved test must not be run until the review and freeze are committed.

## Rebuild and validate

    python -m scripts.build_django_benchmark_draft --force
    python -m src.evaluation.validate --corpus django-5.2

Rebuilding only copies passages from the pinned source files. It does not call
an LLM or the internet. Validation proves that the schema and exact evidence
are valid; it does not prove that reference wording is correct or that an
unanswerable question is absent from every source.

## Review rule

Review development and test records before the freeze, but do not run retrieval
experiments on the test split. After the freeze, configuration selection uses
development only. The test split is opened once for the final v2 result.
