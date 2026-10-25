# RAG Evaluation Harness

A document-based RAG baseline and an evaluation harness for measuring retrieval
quality separately from generated-answer quality. The first benchmark uses 12
version-pinned FastAPI tutorial pages; core ingestion and retrieval are generic.

**Current status:** baseline implemented; Milestone 3 evaluation work in progress.
The benchmark is draft. LLM judging, four-configuration experiments and CI quality
gates are not implemented yet. No production-readiness claim is made.

## Implemented

- Markdown/text loading with documented normalization.
- Fixed-size chunking (550 characters, 80 overlap), local MiniLM embeddings,
  persistent Chroma storage and top-5 dense retrieval.
- Context-only answer generation through a replaceable HTTP LLM client.
- A 50-question draft with exact evidence: 40 development, 10 reserved test.
- Corpus/evidence validation, atomic question checkpoints and resumable capture.
- Deterministic retrieval scoring and per-category JSON/Markdown reports.
- 23 automated tests covering validation, resume/error handling and metric math.

## Draft development results

Configuration A, K=5, 25 October 2026. All 40 development questions completed
retrieval successfully; retrieval quality uses the 36 answerable questions.
Four unanswerable development questions are excluded. The 10 test questions
have not been run. Human benchmark review is still pending.

| Metric | Result |
|---|---:|
| Page Hit@5 | 36/36 (100%) |
| MRR@5 | 0.9583 |
| Required-source recall@5 | 1.0000 |
| Exact evidence coverage@5 | 0.8375 |
| Complete evidence@5 | 27/36 (75%) |

Finding the correct page does not guarantee retrieval of the required evidence.
Nine development questions lack some or all gold evidence in their top five
chunks. These results describe a small, author-review-pending benchmark; they
are not generated-answer correctness or a general claim about RAG quality.

See [the report](reports/config-a-dev-draft-v2/report.md),
[metric definitions](METRICS.md) and
[benchmark review sheet](data/eval/REVIEW.md). The published report includes
observations and provenance for inspection. Original embedding-index revision
provenance remains a limitation before controlled comparisons.

## Run locally

The existing project environment uses Python 3.13 on Windows. A clean-install
reproduction of requirements.txt has not yet been verified.

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m src.evaluation.validate
    python -m unittest discover -s tests -v

Build the baseline index if it does not exist:

    python -m src.retrieval.index

Capture and score development retrievals (no generator/judge API calls):

    python -m src.evaluation.run --split dev --output runs/my-dev-run
    python -m src.evaluation.report --run runs/my-dev-run

The embedding model downloads on first use unless cached. In this project's
existing environment the cache is under .cache/huggingface; set HF_HOME as
described in [RUNNING_EVAL.md](RUNNING_EVAL.md). Retrieval results and caches are
ignored by Git; selected report snapshots are deliberately versioned.

To explicitly generate answers, configure GROQ_API_KEY in an ignored local .env
and use --mode answers. GEMINI_API_KEY is reserved for the planned judge.
Provider/model availability and clean installation are not verified by the
retrieval-only run. Never commit credentials.

## Next milestones

1. Review and freeze the benchmark; add correctness/faithfulness/abstention
   judging, human judge validation and end-to-end answer timing.
2. Compare semantic chunking, hybrid retrieval and reranking with the baseline
   under the same corpus, questions and generation settings.
3. Add regression thresholds and CI; demonstrate both a failing degraded
   configuration and a passing change.

After those milestones: a second corpus and a small demo/API, if useful.
See [ROADMAP.md](ROADMAP.md) and [PROJECT_LOG.md](PROJECT_LOG.md) for context.
