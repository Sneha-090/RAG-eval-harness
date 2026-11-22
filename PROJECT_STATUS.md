# Project status and roadmap

Last updated: **22 November 2026**

- Repository: <https://github.com/Sneha-090/RAG-eval-harness>
- Live dashboard: <https://sneha-rag-eval-harness.streamlit.app/>
- Core benchmark: FastAPI v1, frozen and complete
- Cross-domain extension: Django 5.2 v2, development evaluation complete

## Project objective

This project is a reproducible evaluation and reliability harness for
retrieval-augmented generation systems. It measures retrieval quality,
exact-evidence completeness, answer correctness, faithfulness, abstention, and
latency separately instead of reducing RAG performance to one accuracy score.

Four controlled retrieval configurations are compared using the same corpus,
questions, top-k value, embedding revision, and metric definitions:

| Config | Pipeline |
| --- | --- |
| A | Fixed-size chunking + dense retrieval |
| B | Semantic chunking + dense retrieval |
| C | Fixed-size chunking + BM25/dense hybrid retrieval |
| D | Fixed-size chunking + hybrid retrieval + cross-encoder reranking |

## Completed FastAPI v1 benchmark

- 12 official FastAPI tutorial documents pinned to upstream commit
  `3e33a03bdaa3a89f27d5e0c390c4ba9032f14b5e`.
- 50 evidence-backed questions: 40 development and 10 reserved test.
- Configuration B selected on development complete evidence: 29/36 (80.6%).
- Blind human–judge calibration completed before the final evaluation.
- Dataset, corpus, pipeline, prompts, and scoring protocol frozen before the
  reserved test.
- One-time reserved test completed and versioned without post-test v1 tuning.
- Deterministic retrieval regression gate active in GitHub Actions.

### Frozen v1 reserved-test results

The final split contains nine answerable questions and one unanswerable
question.

| Layer | Metric | Result |
| --- | --- | ---: |
| Retrieval | Page Hit@5 | 9/9 (100%) |
| Retrieval | MRR@5 | 1.0000 |
| Retrieval | Required-source recall@5 | 1.0000 |
| Retrieval | Exact evidence coverage@5 | 0.6389 |
| Retrieval | Complete evidence@5 | 5/9 (55.6%) |
| Answer | Correctness | 7/9 (77.8%) |
| Answer | Faithfulness | 7/9 (77.8%) |
| Answer | Correct abstention | 1/1 (100%) |

The gap between 100% page retrieval and 55.6% complete evidence is a central
finding: finding the correct page does not guarantee that every fact required
for a fully grounded answer appears in the retrieved chunks.

## Django 5.2 cross-domain extension

- 12 official Django 5.2.19 LTS documentation sources pinned at commit
  `a3510e06a7598039d0992dd00c736e25dbdc9aab`.
- Separate corpus paths, collection names, dataset, and run provenance.
- 50-question draft: 40 development, 10 reserved test, 45 answerable, and 5
  deliberately unanswerable.
- Exact-evidence and structural validation complete.
- Four configurations compared on development retrieval only.
- Reserved-test questions remain untouched.

### Django development results

The comparison covers 36 answerable development questions.

| Config | Hit@5 | Evidence coverage@5 | Complete evidence@5 | Mean retrieval |
| --- | ---: | ---: | ---: | ---: |
| A | 100% | 79.80% | 20/36 (55.56%) | 49.9 ms |
| **B** | **100%** | **84.72%** | **30/36 (83.33%)** | **42.8 ms** |
| C | 100% | 91.28% | 28/36 (77.78%) | 52.3 ms |
| D | 100% | 91.14% | 27/36 (75.00%) | 1,362.2 ms |

B is the provisional Django development selection because complete evidence is
the primary metric. These numbers are development retrieval results, not answer
accuracy or held-out test results.

## Reliability engineering

- Resumable per-question checkpoints avoid repeating successful API calls.
- Immutable run signatures reject changed inputs in an existing output folder.
- Atomic writes and a run lock protect checkpoint integrity.
- Retrieval capture, generation, and judging are separate stages.
- Strict judge schemas reject malformed or non-finite scores.
- Blind human labels are stored before judge agreement is calculated.
- CI validates provenance and proves a deliberately degraded result fails.
- The repository passes both corpus validators, `ty check`, and 77 functional
  tests.
- The public Streamlit dashboard reads committed reports and requires no API
  secrets or live model calls.

## Current roadmap

The core FastAPI v1 result is complete. The remaining Django v2 work is:

1. Complete semantic author review of all 50 Django benchmark records.
2. Re-run the four development configurations if review changes any record.
3. Calibrate answer judging on a fresh blind Django development sample.
4. Commit a machine-readable v2 freeze before accessing the reserved split.
5. Run the 10-question Django reserved test once and publish failure analysis.
6. Add a separate deterministic Django development gate to CI.
7. Reproduce setup and evaluation on a clean second machine.
8. Update the dashboard and create a tagged release with final v2 artifacts.

## Evaluation rules

- Development data may be used for pipeline selection; reserved tests may not.
- Benchmark records and thresholds are not edited merely to improve metrics.
- FastAPI v1 test results remain historical evidence and are not fresh after a
  rerun.
- Django development results are not presented as final held-out evidence.
- Retrieval, evidence completeness, correctness, faithfulness, abstention, and
  latency remain separate claims.
- Public metrics always include the evaluated sample size and limitations.

## Evidence and documentation

- [Project guide](docs/PROJECT_GUIDE.md)
- [Runbook](docs/RUNBOOK.md)
- [Study and interview guide](docs/STUDY_AND_INTERVIEW.md)
- [FastAPI final summary](reports/final-test-v1-2026-11-22/SUMMARY.md)
- [Django development comparison](reports/four-config-django-v2-dev-2026-11-22/report.md)
- [Metrics contract](METRICS.md)
- [Quality gate policy](QUALITY_GATE.md)
- [Chronological project log](PROJECT_LOG.md)

The current evidence supports a reproducible RAG evaluation engineering
project. It does not claim production readiness or broad domain generalization.
