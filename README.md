# RAG Evaluation Harness

[![Retrieval quality gate](https://github.com/Sneha-090/RAG-eval-harness/actions/workflows/retrieval-quality.yml/badge.svg)](https://github.com/Sneha-090/RAG-eval-harness/actions/workflows/retrieval-quality.yml)

A document-based RAG baseline and an evaluation harness for measuring retrieval
quality separately from generated-answer quality. The completed first benchmark
uses 12 version-pinned FastAPI tutorial pages. A separate Django 5.2 LTS corpus
now tests whether the same generic harness can transfer to a second domain.

New here? Start with the [project status and roadmap](PROJECT_STATUS.md), then read the
[project guide](docs/PROJECT_GUIDE.md), [runbook](docs/RUNBOOK.md), and
[study/interview guide](docs/STUDY_AND_INTERVIEW.md).

**Current status:** resume-ready FastAPI benchmark v1 is complete. Four retrieval
configurations were compared, configuration B was selected on development,
and a CI regression gate protects it. A fresh mixed blind calibration matched
the hidden judge on 8/8 correctness, 8/8 faithfulness and 2/2 abstention labels.
After a recorded freeze, the one-time reserved test achieved 100% Page Hit@5,
77.8% answer correctness, 77.8% faithfulness and 100% abstention. See the
[final report](reports/final-test-v1-2026-11-22/SUMMARY.md). No production-
readiness claim is made. Django benchmark v2 is in progress: its 12 official
documentation sources and 50-question draft are versioned. Development-only
comparison selected configuration B with complete evidence on 30/36 answerable
questions; semantic author review, freeze and reserved test remain pending.

## Implemented

- Markdown/text loading with documented normalization.
- Fixed-size chunking (550 characters, 80 overlap), local MiniLM embeddings,
  persistent Chroma storage and top-5 dense retrieval.
- Embedding-based semantic chunking with recorded boundary and size settings.
- BM25/dense reciprocal-rank fusion and pinned local cross-encoder reranking.
- A pinned embedding revision and GitHub Actions gate that rebuilds B, reruns
  development retrieval and rejects metric or provenance regressions.
- Context-only answer generation through a replaceable HTTP LLM client.
- A frozen 50-question benchmark with exact evidence: 40 development, 10 reserved test.
- Corpus/evidence validation, atomic question checkpoints and resumable capture.
- Deterministic retrieval scoring and per-category JSON/Markdown reports.
- Provisional correctness/faithfulness/abstention judging with strict output validation.
- Deterministic answer-quality, calibration and successful-stage latency reports.
- Blind human-review export and input-pinned agreement comparison.
- A guided local review screen that saves blind human labels without showing judge scores.
- A versioned corpus registry that keeps FastAPI v1 and Django v2 datasets,
  Chroma collections and provenance separate.
- 77 automated tests covering chunking, retrieval, quality gates, validation, resume/error handling,
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

Inspect or index the pinned Django 5.2 LTS corpus without touching FastAPI v1:

    python -m scripts.inspect_corpus --corpus django-5.2
    python -m src.retrieval.index --corpus django-5.2 --config B

All commands default to `fastapi-v1` for backward compatibility. Django uses
separate dataset paths and Chroma collection names. Its evaluation command will
be enabled after the new questions are reviewed and frozen.

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

Open the saved-results dashboard (no API keys or model calls required):

**Live dashboard:** https://sneha-rag-eval-harness.streamlit.app/

    python -m streamlit run streamlit_app.py

The default view shows the frozen final metrics, four-configuration comparison,
pipeline flow, category evidence, per-question outcomes and failure analysis.
Use the sidebar to switch to Blind review, which shows the reference, generated
answer and retrieved context and saves human decisions to the labels file.

For Streamlit Community Cloud, deploy `dashboard/streamlit_app.py` from the
`main` branch. Its local dependency file contains only Streamlit and pandas, so
the public saved-results dashboard does not install the evaluation stack. No
secrets are required. Community Cloud executes from the repository root, so
the versioned report paths and root theme remain valid.

## Next milestones

Benchmark v1, mixed calibration, the one-time reserved test, results dashboard,
architecture guide and portable learning handoff are complete. The second
Django corpus is pinned and isolated, its 50-question benchmark draft is
structurally validated, and the four development configurations have been
compared. The live dashboard shows these v2 development results without
rewriting the frozen v1 result. Semantic author review, a fresh v2 freeze and
the untouched Django reserved test remain before making a final v2 claim.
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

## First provisional answer-quality result (13 November 2026)

The version-pinned historical configuration A capture contains 15 development
answers: 14 answerable and one unanswerable. The calibrated-but-still-
provisional judge scored correctness **13/14 (92.9%)**, faithfulness **13/14
(92.9%)** and abstention **1/1**. The abstention result is not human-calibrated.
Mean successful-stage answer latency (retrieval plus generation) was **1.1107
seconds** and nearest-rank P95 was **1.8977 seconds**. Scheduling waits, judge
time, model preload and failed-attempt time are excluded.

The two observed failures are useful: q011 incorrectly refused an answerable
request-body question, while q001 added a code example absent from its retrieved
context. Four questions resumed after earlier transient failures, so historical
total retry cost cannot be reconstructed. See the
[full answer-quality report](reports/answer-quality-config-a-calibration-2026-11-13/report.md).
These numbers describe a small development sample for configuration A, not the
selected B pipeline, the reserved test split or general RAG accuracy.

## First provisional A-versus-B answer comparison (14 November 2026)

Generated and judged 15 configuration B answers with zero final failures, then
paired them question-by-question with the existing configuration A calibration
run. Fairness checks require identical questions, references, corpus, retrieval
depth, generator, answer prompt, embedding model, judge and judge prompt; only
the retrieval configuration differs.

Both configurations scored **13/14 (92.9%) correctness**, **13/14 (92.9%)
faithfulness** and **1/1 abstention**. Correctness tied on all 14 answerable
questions. Faithfulness improved on q001, regressed on q009 and tied on the
remaining 12. Both configurations incorrectly refused q011. Mean successful-
stage answer latency was 1.1107 seconds for A and 1.3936 seconds for B, but the
runs happened on different dates, so this is descriptive rather than a
controlled speed comparison.

The [paired report](reports/config-a-vs-b-calibration-2026-11-14/report.md)
preserves exact answers, retrieved contexts, scores and provenance. It is
explicitly provisional: candidate outputs have not received a fresh independent
blind review, abstention has one uncalibrated example and the reserved test
split remains untouched. Therefore the report does **not** claim an answer-
quality winner.

## Fresh mixed blind calibration completed (22 November 2026)

Prepared a second independent packet from ten previously unused development
questions: two direct, two similar-page, two multi-part, two paraphrase and two
unanswerable. Configuration B generated all 10 answers with zero final errors.
Exact question-ID selection is recorded in the capture contract. Human labels
were committed before the hidden judge run. Exact agreement was 100% for
correctness (8 labels), faithfulness (8 labels) and abstention (2 labels), with
no disagreements.

The guided Streamlit screen now supports both scoring paths: correctness plus
faithfulness for answerable questions, and abstention for unanswerable
questions. It preserves the original version-1 calibration format while using
a signed version-2 mixed packet for the new sample. See
[calibration/2026-11-14](calibration/2026-11-14/README.md).

## Frozen v1 reserved-test result (22 November 2026)

The benchmark and selected configuration B pipeline were frozen in commit
`7ff5a61` before the ten reserved questions were run. Retrieval found a relevant
source for all 9/9 answerable questions and ranked it first every time, but
complete exact evidence was present for 5/9. The calibrated judge scored answer
correctness 7/9, faithfulness 7/9 and the single unanswerable abstention 1/1.
Mean successful-stage answer latency was 1.1764 seconds.

The [final report](reports/final-test-v1-2026-11-22/SUMMARY.md) explains the four
metric-level failures and preserves machine-readable results. No v1 tuning was
performed from the reserved-test outcomes.
