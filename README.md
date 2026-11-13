# RAG Evaluation Harness

[![Retrieval quality gate](https://github.com/Sneha-090/RAG-eval-harness/actions/workflows/retrieval-quality.yml/badge.svg)](https://github.com/Sneha-090/RAG-eval-harness/actions/workflows/retrieval-quality.yml)

A document-based RAG baseline and an evaluation harness for measuring retrieval
quality separately from generated-answer quality. The first benchmark uses 12
version-pinned FastAPI tutorial pages; core ingestion and retrieval are generic.

**Current status:** all four retrieval configurations are compared and a
development retrieval regression gate is implemented. The first blind
human–judge calibration measured 100.0% correctness agreement and 78.6%
faithfulness agreement on 14 answerable development outputs. The benchmark,
judge and answer-quality results remain provisional; a fresh calibration,
human benchmark review and final answer experiments are still pending. No
production-readiness claim is made.

## Implemented

- Markdown/text loading with documented normalization.
- Fixed-size chunking (550 characters, 80 overlap), local MiniLM embeddings,
  persistent Chroma storage and top-5 dense retrieval.
- Embedding-based semantic chunking with recorded boundary and size settings.
- BM25/dense reciprocal-rank fusion and pinned local cross-encoder reranking.
- A pinned embedding revision and GitHub Actions gate that rebuilds B, reruns
  development retrieval and rejects metric or provenance regressions.
- Context-only answer generation through a replaceable HTTP LLM client.
- A 50-question draft with exact evidence: 40 development, 10 reserved test.
- Corpus/evidence validation, atomic question checkpoints and resumable capture.
- Deterministic retrieval scoring and per-category JSON/Markdown reports.
- Provisional correctness/faithfulness/abstention judging with strict output validation.
- Blind human-review export and input-pinned agreement comparison.
- A guided local review screen that saves blind human labels without showing judge scores.
- 61 automated tests covering chunking, retrieval, quality gates, validation, resume/error handling,
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

## Four-configuration development comparison

All four roadmap retrieval pipelines now have current-snapshot development
results. B (semantic chunking + dense retrieval) is the provisional winner with
complete evidence on **29/36 (80.6%)** answerable questions while retaining
100% Page Hit@5 and source recall. D (hybrid + cross-encoder reranking) achieved
the best average evidence coverage, 0.8516, but complete evidence was 27/36 and
mean retrieval time was 0.8974 seconds versus about 0.02 seconds for A/B/C.
The [four-way report](reports/four-config-dev-2026-11-12/report.md) explains why
more complexity did not automatically win. Test-split and generated-answer
comparisons remain pending.

## Automated regression protection

The [quality-gate policy](quality-gate.json) freezes B's development baseline.
Every push to `main` and pull request rebuilds the semantic index, retrieves all
40 development questions and fails if complete evidence drops below 29/36,
Page Hit@5 or source recall drops below 100%, or tolerance-limited metrics
regress. CI also proves that a deliberately degraded one-question result is
rejected. See [QUALITY_GATE.md](QUALITY_GATE.md) for thresholds and update rules.
The reserved test split and paid APIs are not used in CI.

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

Select semantic chunking with `--config B`, fixed-chunk hybrid retrieval with
`--config C`, or hybrid plus cross-encoder reranking with `--config D`. Each
configuration requires a new output directory. D downloads its pinned local
reranker model on first use.

The embedding model downloads on first use unless cached. In this project's
existing environment the cache is under .cache/huggingface; set HF_HOME as
described in [RUNNING_EVAL.md](RUNNING_EVAL.md). Retrieval results and caches are
ignored by Git; selected report snapshots are deliberately versioned.

To explicitly generate answers, configure GROQ_API_KEY in an ignored local .env
and use --mode answers. GEMINI_API_KEY is used by the provisional judge. See [JUDGING.md](JUDGING.md).
Provider/model availability and clean installation are not verified by the
retrieval-only run. Never commit credentials.

Review the saved real calibration packet through the local guided screen (no
API keys or model calls required):

    python -m streamlit run streamlit_app.py

It shows the reference, generated answer and retrieved context, then saves two
human decisions per item to the versioned labels file. Judge verdicts stay
hidden until the independent review is complete.

## Next milestones

1. Review and freeze the benchmark, then run a fresh blind calibration sample
   that also validates abstention on unanswerable questions.
2. Compare generated-answer quality and end-to-end timing for the selected
   pipelines using the calibrated judge.
3. Run the reserved test split once on the frozen benchmark, then finalize
   architecture documentation, results dashboard and resume wording.

After those milestones: a second corpus and a small demo/API, if useful.
See [ROADMAP.md](ROADMAP.md) and [PROJECT_LOG.md](PROJECT_LOG.md) for context.


## First human calibration measured (13 November 2026)

Generated and provisionally judged 15 development answers, with zero final
errors after resuming four transient connection failures. Fourteen answerable
outputs were independently labelled through the [guided review screen](streamlit_app.py).
Exact agreement with the hidden judge was **14/14 (100.0%) for correctness**
and **11/14 (78.6%) for faithfulness**. The
[agreement review](calibration/2026-10-26/agreement-review.md) inspects all
three differences without rewriting the initial blind score. All ten test
questions remain untouched; abstention has not been human-calibrated.
