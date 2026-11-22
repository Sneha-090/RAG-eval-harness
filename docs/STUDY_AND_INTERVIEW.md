# Study, resume and interview guide

## The 30-second explanation

“I built a RAG evaluation harness, not just a chatbot. It benchmarks four
retrieval pipelines on a frozen 50-question FastAPI documentation dataset,
scores retrieval and generated answers separately, validates an LLM judge
against blind human labels, and blocks retrieval regressions in GitHub Actions.
The selected semantic-chunking pipeline achieved 100% Page Hit@5 on the frozen
reserved split, while answer correctness and faithfulness were both 77.8%,
which exposed over-abstention and missing-evidence failures.”

## The two-minute explanation

“The problem I wanted to solve was that RAG demos often show a few good answers
but do not prove what improved or detect regressions. I pinned 12 FastAPI docs,
built a 50-question evidence-backed benchmark with development and reserved
splits, and implemented four controlled retrieval configurations: fixed+dense,
semantic+dense, hybrid, and hybrid+reranker.

I defined metrics before the final comparison: Page Hit@K, MRR, required-source
recall, exact evidence coverage, complete evidence, correctness, faithfulness,
abstention and stage-separated latency. Semantic+dense won development complete
evidence at 29/36, so I protected it with a GitHub Actions gate.

For answer evaluation I used a strict model judge, but first froze human labels
without showing judge verdicts. On a fresh mixed sample they agreed 100% on 8
correctness, 8 faithfulness and 2 abstention decisions. I then froze hashes for
the benchmark, corpus, pipeline and prompts before running ten reserved
questions once. Retrieval found the right page for every answerable question,
but complete evidence was only 5/9; correctness and faithfulness were 7/9. That
gap is the key result: finding the right page is not the same as grounding every
answer claim.”

## Glossary

| Term | Easy meaning | This project |
|---|---|---|
| RAG | Retrieve documents, then let an LLM answer from them. | Top-5 FastAPI chunks become the answer context. |
| Corpus | The documents a system may use. | 12 pinned FastAPI Markdown pages. |
| Chunk | A smaller passage cut from a document. | Fixed or semantic chunks with deterministic IDs. |
| Embedding | A numeric vector representing meaning. | Pinned MiniLM model for chunks and questions. |
| Dense retrieval | Finds vectors that are semantically close. | Used by A and B; part of C and D. |
| BM25 | Keyword-based ranking. | Combined with dense results in C/D. |
| RRF | Merges rank lists using positions rather than raw score scales. | Combines BM25 and dense rankings. |
| Reranker | A stronger model that reorders retrieved candidates. | Cross-encoder in D. |
| Top-k | Number of chunks returned. | k=5. |
| Gold source | Document known to contain the answer. | Stored per benchmark row. |
| Gold evidence | Exact source quote supporting the reference. | Used for coverage and completeness. |
| Hit@K | Was at least one gold source retrieved? | Final 9/9 answerable. |
| MRR@K | How early did the first gold source appear? | Final 1.0: rank 1 every time. |
| Source recall | Fraction of all required source pages retrieved. | Final 1.0. |
| Evidence coverage | Fraction of required exact quote text covered by chunks. | Final mean 0.6389. |
| Complete evidence | Did retrieval cover every required quote? | Final 5/9. |
| Correctness | Does the answer agree with the reference? | Final 7/9. |
| Faithfulness | Is every factual claim supported by retrieved context? | Final 7/9. |
| Abstention | Does the model refuse when the corpus lacks the answer? | Final 1/1. |
| Calibration | Compare judge labels with independent human labels. | Mixed sample: 8+8+2 exact matches. |
| Development split | Questions allowed for choosing/tuning. | 40 questions. |
| Reserved test | Questions hidden from tuning until the pipeline is frozen. | 10 questions, run once for v1. |
| Checkpoint | Saved progress for one item. | Prevents repeating successful API calls. |
| Provenance | Evidence of exact data/code/model/settings used. | Hashes and signed manifests. |
| Regression gate | Automated rule that rejects quality drops. | GitHub Actions protects B development baseline. |

## Seven-session study plan

Do one session at a time. At the end, explain it aloud without reading.

### Session 1 — Project story and RAG basics

- Read `README.md` and `docs/PROJECT_GUIDE.md` through “Architecture.”
- Learn corpus, chunk, embedding, retrieve, generate.
- Draw the data flow from memory.
- Practice: explain why this project is more than a FastAPI Q&A bot.

### Session 2 — Chunking and the four configurations

- Read `src/chunking/fixed.py`, then `src/chunking/semantic.py`.
- Read `src/retrieval/dense.py`, `hybrid.py`, `rerank.py`.
- Open `reports/four-config-dev-2026-11-12/report.md`.
- Practice: explain why B won although D had higher average coverage.

### Session 3 — Benchmark and retrieval metrics

- Read `METRICS.md` retrieval sections and five rows from the JSONL dataset.
- Read `src/evaluation/metrics.py` tests before its implementation.
- Manually calculate Hit@5 and reciprocal rank for one example.
- Practice: explain page hit versus complete evidence.

### Session 4 — Resumability, signatures and CI

- Read `src/evaluation/run.py`, `quality-gate.json` and the workflow YAML.
- Follow one record from manifest to checkpoint to report.
- Practice: explain why changed inputs require a new output directory.
- Trigger no paid calls; use the dev retrieval commands in `RUNBOOK.md`.

### Session 5 — Answer quality and judge calibration

- Read `src/generation/answer.py`, `src/evaluation/judge.py` and
  `human_review.py`.
- Open `calibration/2026-11-14/RESULT.md`.
- Practice classifying: incorrect-but-faithful, correct-but-unfaithful, and
  correct abstention.

### Session 6 — Final result and dashboard

- Open the Streamlit dashboard.
- Read the final `SUMMARY.md`, then inspect q021, q036, q045 and q046 in the
  machine-readable report.
- Practice: explain every final metric and limitation without overclaiming.

### Session 7 — Code tour and mock interview

- Use the file table in `PROJECT_GUIDE.md` and open every major file once.
- Run validation and tests.
- Answer all interview questions below aloud.
- Give a future tutor `PROJECT_STATUS.md` and ask it to quiz you section by
  section using the versioned evidence linked there.

## Honest resume bullets

Use two or three depending on space. Do not replace the measured numbers with
larger development-only numbers without naming the split.

- Built a Python RAG evaluation harness over 12 version-pinned FastAPI documents
  and a frozen 50-question evidence-backed benchmark; compared fixed, semantic,
  hybrid and reranked retrieval pipelines using Hit@5, MRR, source recall and
  exact-evidence coverage.
- Selected semantic chunking + dense retrieval through controlled development
  experiments and achieved 100% Page Hit@5/MRR@5 on a one-time 10-question
  reserved test; diagnosed the gap between page retrieval (100%) and complete
  evidence retrieval (55.6%).
- Implemented resumable signed evaluation runs, blind human–LLM judge
  calibration, correctness/faithfulness/abstention reports, a Streamlit results
  dashboard, and a GitHub Actions regression gate backed by 77 functional tests.

Compact single bullet:

- Built a reproducible RAG reliability harness (Python, Chroma, MiniLM,
  Streamlit, GitHub Actions) comparing 4 retrieval pipelines on a frozen
  50-question benchmark; reached 100% Page Hit@5 on the reserved test and added
  calibrated answer scoring plus CI regression protection.

## Claims not to make

- Do not say “95% final accuracy.” The final answer correctness is 77.8% on 9
  answerable reserved questions.
- Do not say “production-ready” or “domain-general.”
- Do not say every benchmark item was manually human-approved.
- Do not say reranking was best; B was selected.
- Do not call the 10-question calibration universal proof of judge reliability.
- Do not say CI calls the paid LLMs; CI protects deterministic retrieval.

## Interview questions with model answers

### 1. What problem does this project solve?

It replaces demo-based RAG evaluation with controlled, repeatable measurement.
It tells me whether failure came from retrieval, missing evidence, generation,
unsupported claims or incorrect refusal, and CI catches deterministic retrieval
regressions.

### 2. Why did you use a development/test split?

The 40 development questions allowed pipeline selection. The 10 reserved
questions were untouched until the corpus, configuration and prompts were
fingerprinted. That reduces overfitting and makes the final result more honest,
although the test is small and in-domain.

### 3. Why is Hit@5 not enough?

Hit@5 only checks whether a relevant page appears. A chunk from that page may
omit the exact sentence needed. Final Hit@5 was 100%, but complete evidence was
only 55.6%, demonstrating the difference.

### 4. How does semantic chunking work here?

The document is split into bounded semantic units, adjacent unit embeddings are
compared, and large meaning changes become candidate boundaries subject to
minimum/maximum chunk-size rules. The settings and model revision are recorded
for reproducibility.

### 5. What is hybrid retrieval?

It combines lexical BM25 ranking with dense semantic ranking using reciprocal-
rank fusion. This lets exact tokens and meaning both contribute without trying
to compare their incompatible raw scores directly.

### 6. Why did configuration D not win?

D's reranker slightly improved mean evidence coverage, but complete evidence
was 27/36 versus B's 29/36 and mean retrieval latency was about 0.897 seconds
versus about 0.019 for B. The added complexity did not optimize the selected
objective.

### 7. How did you evaluate generated answers?

I scored correctness against references, faithfulness only against retrieved
context, and abstention separately for unanswerable questions. The judge accepts
a strict JSON schema and scores fixed saved answers so generation cannot change
during evaluation.

### 8. Why trust an LLM judge?

I do not trust it automatically. Human labels were completed and committed
before the matching hidden judge run. On the fresh mixed sample, exact agreement
was 8/8 correctness, 8/8 faithfulness and 2/2 abstention. I still report the
small sample and single reviewer as limitations.

### 9. Give an example of correct but unfaithful.

q036 and q046 matched their references, but one requested fact was missing from
the retrieved chunks. The answer could be true from model knowledge, yet it was
not grounded in the context supplied to that RAG call.

### 10. What is over-abstention?

The model refuses an answerable question even when context contains the answer.
q021 and q045 show it. Their refusals were faithful in the narrow sense of not
inventing facts, but incorrect because an answer should have been given.

### 11. How is the runner resumable and safe?

It writes an immutable manifest signature and atomic per-question checkpoints.
Successful retrieval survives a generation failure, successful API calls are
not repeated, concurrent writers are blocked by a lock, and changed inputs
cannot resume into the same folder.

### 12. What does the GitHub Actions gate protect?

It rebuilds B, runs all 40 development retrievals, recomputes deterministic
metrics, validates provenance and rejects metrics below the policy. It also
proves a deliberately degraded result fails. Paid LLM calls are excluded.

### 13. What would you improve next?

I would add a second corpus with a new untouched test protocol. Then I would
evaluate retrieval changes aimed at evidence
completeness—such as boundary-aware context expansion—without editing v1 or
reusing its reserved split as fresh evidence.

### 14. What are the biggest limitations?

Small in-domain corpus/test set, one human calibration reviewer, incomplete
full manual benchmark review, provider model drift and no production serving or
load/security evaluation.

### 15. What are you proudest of technically?

The separation of evidence retrieval, correctness and faithfulness; the blind
calibration order; and the signed/resumable workflow. They prevent a strong-
looking metric from hiding where the system actually fails.
