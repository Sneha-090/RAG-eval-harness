# RAG Evaluation Harness

A document-based RAG baseline and an evaluation harness for measuring retrieval
quality separately from generated-answer quality. The first benchmark uses 12
version-pinned FastAPI tutorial pages; core ingestion and retrieval are generic.

**Current status:** baseline and three retrieval configurations implemented;
Milestone 3 validation and Milestone 4 comparison work remain in progress.
The benchmark is draft. Provisional LLM judging and blind human-review tools
are implemented; human validation, four-configuration experiments and CI quality
gates remain pending. No production-readiness claim is made.

## Implemented

- Markdown/text loading with documented normalization.
- Fixed-size chunking (550 characters, 80 overlap), local MiniLM embeddings,
  persistent Chroma storage and top-5 dense retrieval.
- Embedding-based semantic chunking with recorded boundary and size settings.
- Context-only answer generation through a replaceable HTTP LLM client.
- A 50-question draft with exact evidence: 40 development, 10 reserved test.
- Corpus/evidence validation, atomic question checkpoints and resumable capture.
- Deterministic retrieval scoring and per-category JSON/Markdown reports.
- Provisional correctness/faithfulness/abstention judging with strict output validation.
- Blind human-review export and input-pinned agreement comparison.
- 48 automated tests covering chunking, validation, resume/error handling,
  metrics and judging.

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

## Dense vs. hybrid development pilot

Dense search (A) found complete evidence on **27/36** answerable
development questions. Hybrid search (C) found complete evidence on
**26/36**. Both used the same corpus, chunks and top-five limit.
The [paired report](reports/dense-vs-hybrid-dev-2026-11-11/report.md)
shows the timing and question-level changes. Human judge validation and
reserved-test evaluation remain pending.

## Fixed vs. semantic chunking development pilot

Semantic chunking (B) returned complete evidence for **29/36 (80.6%)**
answerable development questions, compared with **27/36 (75.0%)** for fixed
chunking (A). Page Hit@5 and source recall stayed at 100%; exact evidence
coverage increased from 0.8375 to 0.8426, while MRR decreased slightly from
0.9583 to 0.9537. B recovered five cases and lost three. The
[paired report](reports/fixed-vs-semantic-dev-2026-11-12/report.md) records the
settings, question-level changes and limitations. Reserved-test and generated-
answer results remain pending.

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

Build the separate semantic index:

    python -m src.retrieval.index --config B

Capture and score development retrievals (no generator/judge API calls):

    python -m src.evaluation.run --split dev --output runs/my-dev-run
    python -m src.evaluation.report --run runs/my-dev-run

Select semantic chunking with `--config B` or fixed-chunk hybrid retrieval with
`--config C`. Each configuration requires a new output directory.

The embedding model downloads on first use unless cached. In this project's
existing environment the cache is under .cache/huggingface; set HF_HOME as
described in [RUNNING_EVAL.md](RUNNING_EVAL.md). Retrieval results and caches are
ignored by Git; selected report snapshots are deliberately versioned.

To explicitly generate answers, configure GROQ_API_KEY in an ignored local .env
and use --mode answers. GEMINI_API_KEY is used by the provisional judge. See [JUDGING.md](JUDGING.md).
Provider/model availability and clean installation are not verified by the
retrieval-only run. Never commit credentials.

## Next milestones

1. Review and freeze the benchmark; independently label the calibration
   packet, measure judge agreement, and finish answer-quality reporting and
   end-to-end timing.
2. Add reranking (D), then complete the four-configuration comparison under the
   same corpus, questions and generation settings.
3. Add regression thresholds and CI; demonstrate both a failing degraded
   configuration and a passing change.

After those milestones: a second corpus and a small demo/API, if useful.
See [ROADMAP.md](ROADMAP.md) and [PROJECT_LOG.md](PROJECT_LOG.md) for context.


## Human review ready (26 October 2026)

Generated and provisionally judged 15 development answers, with zero final
errors after resuming four transient connection failures. Fourteen answerable
outputs are ready for independent correctness/faithfulness labels:
[review sheet](calibration/2026-10-26/review.md) and
[blank labels](calibration/2026-10-26/labels.csv).
Judge verdicts are deliberately excluded from the blind packet. All ten test
questions remain untouched. No human judge-agreement number exists yet.
