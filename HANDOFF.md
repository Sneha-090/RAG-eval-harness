# Master project handoff and continuation plan

- Last verified: **22 November 2026**
- Repository: <https://github.com/Sneha-090/RAG-eval-harness>
- Original local folder: `D:\rag-eval-harness`
- Live dashboard: <https://sneha-rag-eval-harness.streamlit.app/>
Latest implementation/deployment commit before this handoff: `68db6c2`

This is the single starting document for the project owner, a future maintainer,
or another AI coding agent. It replaces missing chat history with facts that can
be checked inside the repository. If an older prose document disagrees with a
versioned JSON report, freeze record, or committed result, the machine-readable
evidence wins.

## 1. The project in very simple language

This is **not only a RAG chatbot**. It contains a small RAG pipeline, but the
main project is an **evaluation and reliability harness** for RAG systems.

It answers questions such as:

1. Did the retriever find the correct document?
2. Did it retrieve the exact sentences needed for the full answer?
3. Is the generated answer correct?
4. Is every claim supported by the retrieved context?
5. Does the model correctly refuse questions that the documents cannot answer?
6. Which retrieval design is best under the same controlled benchmark?
7. Did a new code change reduce retrieval quality?

The project compares four retrieval configurations while keeping the corpus,
questions, top-k value, and metric definitions fixed:

| Config | Pipeline |
| --- | --- |
| A | Fixed-size chunking + dense retrieval |
| B | Semantic chunking + dense retrieval |
| C | Fixed-size chunking + BM25/dense hybrid retrieval |
| D | Fixed-size chunking + hybrid retrieval + cross-encoder reranking |

Configuration B is currently selected on development data. The important
result is not simply that B won. The harness also shows that retrieving the
correct page is not the same as retrieving all evidence required for a grounded
answer.

## 2. What has been completed

### 2.1 Core FastAPI benchmark v1 — complete and resume-ready

- 12 official FastAPI tutorial documents are pinned to upstream commit
  `3e33a03bdaa3a89f27d5e0c390c4ba9032f14b5e`.
- The corpus contains 107,828 bytes and 15,069 words.
- A 50-question evidence-backed benchmark exists: 40 development questions and
  10 reserved-test questions.
- The four retrieval configurations are implemented and were compared only on
  development data before selection.
- Semantic chunking + dense retrieval, configuration B, was selected.
- Correctness, faithfulness, and abstention are scored separately.
- Human labels were frozen before comparison with hidden judge verdicts.
- Corpus, dataset, pipeline, prompts, models, and protocol were fingerprinted
  and committed before the reserved test.
- The 10-question reserved test was run once and its result is versioned.
- A deterministic GitHub Actions regression gate protects the selected
  FastAPI development baseline without using paid LLM calls.
- A saved-results dashboard and a local blind-review interface exist.
- The full repository passes `ty check` and **77 functional tests**.

### 2.2 Django second-domain benchmark v2 — development stage

- 12 official Django 5.2.19 LTS documentation files are pinned to upstream
  commit `a3510e06a7598039d0992dd00c736e25dbdc9aab`.
- The Django corpus is isolated from FastAPI and selected with the corpus key
  `django-5.2`.
- Corpus-selectable indexing, validation, capture, and reporting are
  implemented. FastAPI v1 paths and historical results remain unchanged.
- The Django corpus contains 439,859 bytes and 54,957 words.
- A separate 50-question draft exists: 40 development and 10 reserved test;
  45 answerable and 5 deliberately unanswerable.
- Every answerable draft record has exact evidence from the pinned local
  corpus. Structural and exact-evidence validation pass.
- All four retrieval configurations were compared on Django **development data
  only**. The reserved split remains untouched.
- Configuration B again produced the highest complete-evidence rate.
- The Django result is displayed honestly as development evidence on the live
  dashboard. It is not presented as a final cross-domain benchmark claim.

### 2.3 Engineering and presentation work — complete

- The repository is type-clean with `ty`.
- The generic report path was fixed so scoring uses the selected corpus instead
  of assuming FastAPI.
- Streamlit Community Cloud uses a lightweight dashboard-only dependency file.
- The dashboard is deployed at
  <https://sneha-rag-eval-harness.streamlit.app/> and has been visually checked
  with both FastAPI and Django sections loaded.
- The deployment is connected to `main` using
  `dashboard/streamlit_app.py` and Python 3.13.
- No dashboard secrets or model calls are required because it reads committed
  result files.

## 3. Exact measured results

### 3.1 FastAPI development selection

There are 36 answerable development questions. The primary selection metric is
complete gold evidence in the top five retrieved chunks.

| Config | Complete evidence@5 |
| --- | ---: |
| A | 27/36 (75.0%) |
| **B** | **29/36 (80.6%) — selected** |
| C | 26/36 (72.2%) |
| D | 27/36 (75.0%) |

### 3.2 FastAPI judge calibration

On the fresh mixed calibration sample:

- correctness exact agreement: 8/8;
- faithfulness exact agreement: 8/8;
- abstention exact agreement: 2/2.

This is useful evidence, but it is still a small sample with one human reviewer.

### 3.3 Frozen FastAPI v1 reserved test

The final split contains nine answerable and one unanswerable question.

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
| Latency | Mean retrieval | 0.0337 s |
| Latency | Mean successful answer stages | 1.1764 s |

Failure analysis:

- `q021` and `q045`: the context was useful, but the generator refused an
  answerable question. These are over-abstention/correctness failures.
- `q036` and `q046`: the answers matched their references, but a requested fact
  was missing from the retrieved context. These are faithfulness failures.
- `q050`: the corpus did not support the question and the model correctly
  abstained.

### 3.4 Django v2 development retrieval comparison

The table covers 36 answerable development questions. Four unanswerable
development questions are excluded from retrieval-quality metrics.

| Config | Hit@5 | Evidence coverage@5 | Complete evidence@5 | Mean retrieval |
| --- | ---: | ---: | ---: | ---: |
| A | 100% | 79.80% | 20/36 (55.56%) | 49.9 ms |
| **B** | **100%** | **84.72%** | **30/36 (83.33%)** | **42.8 ms** |
| C | 100% | 91.28% | 28/36 (77.78%) | 52.3 ms |
| D | 100% | 91.14% | 27/36 (75.00%) | 1,362.2 ms |

B was selected because complete evidence is the primary metric. C and D had
higher average evidence coverage, but they did not completely recover every
required quote as often as B. D also added roughly 1.3 seconds of retrieval
latency per question on the measured machine.

These are **development retrieval metrics**, not answer accuracy and not final
held-out Django results.

## 4. How the system works

For a single question:

1. Load the versioned question, reference, gold sources, and exact evidence.
2. Select the requested corpus and one of configurations A–D.
3. Retrieve the top five chunks and save retrieval latency immediately.
4. Optionally generate a context-only answer and checkpoint it.
5. Compute deterministic retrieval metrics from sources and exact evidence.
6. Judge the already-saved answer for correctness and faithfulness; do not
   regenerate an answer during judging.
7. Score abstention separately for unsupported questions.
8. Bind the report to dataset, corpus, model, code, and settings signatures.
9. Publish versioned reports and let CI reject deterministic regressions.

The pipeline is resumable. Successful API calls are checkpointed, a lock stops
concurrent writers, atomic writes reduce corruption risk, and changed inputs
cannot silently resume into the same run folder.

## 5. Important files

| Path | Purpose |
| --- | --- |
| `README.md` | Public project overview and quick start. |
| `HANDOFF.md` | This master truth/continuation document. |
| `src/corpora.py` | Registry separating FastAPI v1 and Django v2. |
| `data/raw/` | Frozen FastAPI Markdown corpus. |
| `data/corpora/django-5.2/raw/` | Frozen Django RST text corpus. |
| `data/CORPUS.md` | FastAPI provenance. |
| `data/corpora/django-5.2/CORPUS.md` | Django provenance and source list. |
| `data/eval/questions.draft.jsonl` | Historical filename for frozen FastAPI v1 questions. |
| `data/eval/benchmark-freeze-v1.json` | FastAPI v1 machine-readable freeze. |
| `data/eval/django-5.2/questions.draft.jsonl` | Separate Django v2 draft. |
| `data/eval/django-5.2/REVIEW.md` | Django semantic author-review checklist. |
| `src/chunking/` | Fixed and semantic chunking implementations. |
| `src/retrieval/` | Embeddings, indexes, dense, hybrid, and reranked retrieval. |
| `src/generation/` | Replaceable LLM clients and context-only answer generation. |
| `src/evaluation/` | Validation, capture, metrics, judge, reports, review, and gate. |
| `quality-gate.json` | Frozen FastAPI B development policy and provenance. |
| `.github/workflows/retrieval-quality.yml` | Tests, rebuild, evaluation, gate, and degradation proof. |
| `calibration/2026-11-14/` | Mixed blind human–judge calibration evidence. |
| `reports/final-test-v1-2026-11-22/` | Frozen FastAPI final evidence. |
| `reports/four-config-django-v2-dev-2026-11-22/` | Django development comparison. |
| `streamlit_app.py` | Canonical local dashboard and blind-review UI. |
| `dashboard/streamlit_app.py` | Lightweight Streamlit Cloud entrypoint. |
| `docs/RUNBOOK.md` | Commands and troubleshooting. |
| `docs/PROJECT_GUIDE.md` | Detailed architecture and experiment story. |
| `docs/STUDY_AND_INTERVIEW.md` | Learning plan, resume bullets, and interview practice. |
| `PROJECT_LOG.md` | Chronological evidence of decisions and changes. |

## 6. What should be done next to make it the strongest project

The order matters. Do not jump directly to the Django reserved test.

### Priority 1 — Complete Django semantic author review

Goal: turn the mechanically valid AI-assisted draft into a human-approved
benchmark.

For all 50 records, check:

1. The question has one clear meaning.
2. The reference answer says no more than the evidence supports.
3. The exact quote directly proves the answer.
4. The category is reasonable.
5. Every unanswerable topic is genuinely absent from all 12 files.

Important rules:

- Review both development and test wording before the freeze, but do not run
  retrieval or answer experiments on the test split.
- Correct factual mistakes even if a correction lowers development scores.
- Never edit a label only to make a retrieval method look better.
- Record reviewer name/role, review date, and status for each item.

Definition of done:

- all 50 records have explicit author-review status;
- `python -m src.evaluation.validate --corpus django-5.2` passes;
- review decisions and any factual edits are committed before new comparisons.

### Priority 2 — Re-run the four Django development configurations

Author review may change wording, evidence, or categories, so the current
comparison must be treated as provisional after any benchmark edit.

Definition of done:

- A, B, C, and D use the same reviewed dataset, corpus, k, embedding revision,
  and metric code;
- a new versioned comparison report explains the selection rule and latency;
- the selected configuration is based only on development data;
- negative results are kept instead of hidden.

### Priority 3 — Calibrate answer judging on Django development data

FastAPI judge agreement should not automatically be presented as proof for a
new domain. Build a fresh blinded Django calibration sample containing:

- correct and incorrect answers;
- grounded and unsupported answers;
- at least one answerable refusal;
- at least one genuinely unanswerable question.

Complete human labels before revealing or comparing judge verdicts. Save the
packet, labels, judge outputs, and agreement report in a new versioned Django
calibration folder.

Definition of done:

- judge schema, prompt, and model are recorded;
- exact agreement is reported with raw counts, not only percentages;
- disagreements are reviewed and limitations name the sample size and single
  reviewer if that remains true.

### Priority 4 — Freeze Django v2 before touching its reserved test

Create a machine-readable freeze similar to FastAPI v1. It should fingerprint:

- reviewed dataset;
- all 12 corpus files;
- selected configuration and chunk settings;
- embedding model and revision;
- generator model/prompt if answer quality will be claimed;
- judge model/prompt and calibration evidence;
- metric/scorer implementations;
- test IDs, k, and evaluation protocol.

Commit and push the freeze before running the test split.

### Priority 5 — Run the Django reserved test once

After the freeze, run the untouched 10-question split once. Measure and publish:

- Page Hit@5, MRR@5, and required-source recall@5;
- exact evidence coverage and complete evidence;
- answer correctness and faithfulness;
- correct abstention;
- stage-separated latency;
- per-question failure analysis.

Do not tune v2 from these results. Fixes inspired by the final v2 test belong
to a named v3 protocol with new untouched evidence.

### Priority 6 — Add the Django deterministic CI gate

Protect the reviewed Django development baseline in GitHub Actions. Keep paid
generation and judging out of push CI. The gate should validate provenance and
prove that one deliberately degraded result is rejected.

Definition of done:

- FastAPI v1 and Django v2 use separate policies;
- both corpus validations and functional tests run;
- CI uses development data only;
- thresholds are explained and are not loosened merely to get a green build.

### Priority 7 — Reproduce setup on a clean second machine

The repository works in the current Windows environment, but an independent
clean installation is stronger evidence. Test the documented Python 3.13 setup,
model downloads, tests, one development retrieval run, and dashboard launch.
Record every issue and the exact fix.

### Priority 8 — Polish the public presentation

After the final v2 report:

- update the dashboard with final Django results while retaining the v1/v2
  distinction;
- add one clear architecture image and two screenshots/GIFs to the README;
- add a short demo video showing the dashboard and one regression-gate failure;
- create a tagged GitHub release with the freeze/report artifacts;
- update resume bullets with only final measured numbers and sample sizes.

### Optional research extensions — only after v2 is frozen

Test one hypothesis at a time on development data:

- parent/child or boundary-aware context expansion to improve complete evidence;
- contextual chunk headers;
- query rewriting or multi-query retrieval;
- retrieval-error taxonomy and per-category analysis;
- cost/token metrics for answer generation;
- robustness tests for paraphrases and adversarial unsupported questions.

Do not add every fashionable RAG technique. A controlled experiment with a
clear hypothesis is stronger than a large pipeline whose improvements cannot
be attributed.

## 7. Definition of the best realistic final version

The project is in its strongest honest state when all of the following are
true:

- two version-pinned documentation domains have reviewed 50-question datasets;
- each domain has a 40/10 development/reserved protocol;
- four retrieval pipelines are compared under controlled settings;
- both reserved tests are run once only after committed freezes;
- retrieval, evidence completeness, correctness, faithfulness, abstention, and
  latency are separately reported;
- judge agreement is calibrated and limitations are explicit;
- deterministic development regressions for both domains fail CI;
- 100% of tests and the type check pass on a clean installation;
- the live dashboard reads only versioned result evidence;
- README, dashboard, resume, and interview answers all use the same numbers.

That would support a strong claim of **reproducible cross-domain RAG evaluation
engineering**. It still would not justify calling the system production-ready
without load, security, observability, and serving evaluations.

## 8. Commands a future agent can safely run now

PowerShell:

```powershell
Set-Location D:\rag-eval-harness

# Verify both benchmarks, tests, and typing.
& .\.venv\Scripts\python.exe -B -m src.evaluation.validate
& .\.venv\Scripts\python.exe -B -m src.evaluation.validate --corpus django-5.2
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
& .\.venv\Scripts\ty.exe check

# Inspect the second corpus and rebuild B if needed.
& .\.venv\Scripts\python.exe -m scripts.inspect_corpus --corpus django-5.2
& .\.venv\Scripts\python.exe -B -m src.retrieval.index --corpus django-5.2 --config B

# Run Django development retrieval only; use a new output directory.
& .\.venv\Scripts\python.exe -B -m src.evaluation.run `
  --corpus django-5.2 --config B --split dev `
  --output runs\django-b-dev-new
& .\.venv\Scripts\python.exe -B -m src.evaluation.report `
  --run runs\django-b-dev-new

# Open the local dashboard.
& .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Command Prompt uses `cd /d D:\rag-eval-harness` and must not use PowerShell's
leading `&`. Full setup and troubleshooting remain in `docs/RUNBOOK.md`.

Do **not** run `--split test` for Django until author review and the v2 freeze
are committed.

## 9. Non-negotiable continuation rules

- Work only in `D:\rag-eval-harness`; do not create a parallel copy as a new
  project.
- Inspect `git status` before editing and preserve unrelated user changes.
- Preserve the owner's configured Git author. Do not add AI/Codex attribution,
  co-author trailers, or wording claiming that an agent owns the work.
- Make small, meaningful commits and push after verified milestones rather than
  putting the whole project in one giant commit.
- Never commit `.env`, API keys, tokens, caches, local vector stores, or raw
  provider secrets.
- Do not edit benchmark labels or gate thresholds merely to improve metrics.
- FastAPI v1's reserved split is historical evidence and is no longer fresh.
- Django's reserved split must remain untouched until its committed freeze.
- Keep retrieval, evidence completeness, answer correctness, faithfulness,
  abstention, and latency separate.
- Do not call development results final test results.
- Tie every public claim to a versioned report and include the sample size.
- Run relevant validation, tests, and `ty check` before committing code.
- Explain completed work to the owner in very easy Hinglish after each step.

## 10. Claims that must not be made

- Do not say “95% final accuracy.” FastAPI final correctness is 7/9 (77.8%).
- Do not call Django's current 83.3% complete-evidence result a held-out result.
- Do not say the system is production-ready or broadly domain-general.
- Do not say all benchmark records have completed human semantic review.
- Do not say reranking was best; B won the selected complete-evidence objective.
- Do not say CI evaluates paid LLM answers; current push CI is deterministic
  retrieval protection for FastAPI v1.
- Do not use the v1 or future v2 final tests repeatedly for tuning.

## 11. Current honest resume version

Use two or three bullets depending on available space:

- Built a Python RAG evaluation harness over two version-pinned documentation
  corpora, implementing fixed, semantic, hybrid, and reranked retrieval with
  separate metrics for page retrieval, exact evidence, answer correctness,
  faithfulness, abstention, and latency.
- Selected semantic chunking + dense retrieval through controlled experiments;
  achieved 100% Page Hit@5/MRR@5 on a one-time 10-question FastAPI reserved
  test while diagnosing the gap between page retrieval and complete evidence
  retrieval (55.6%).
- Implemented resumable signed runs, blind human–LLM judge calibration, a
  GitHub Actions regression gate, 77 functional tests, and a public Streamlit
  results dashboard; also reproduced the retrieval comparison on a separate
  Django development benchmark.

Do not put a final Django test number on the resume until priorities 1–5 are
complete.

## 12. Study plan so the owner can explain every part

Study one layer at a time and explain it aloud without reading.

1. **Project story:** read this document and `README.md`; explain why this is an
   evaluation harness rather than only a chatbot.
2. **RAG flow:** read `docs/PROJECT_GUIDE.md`; draw corpus → chunks → index →
   retrieval → answer → scoring.
3. **Four configurations:** read fixed/semantic chunking and dense/hybrid/
   rerank files; explain what changes and what remains controlled.
4. **Metrics:** read `METRICS.md`; manually calculate Hit@5, reciprocal rank,
   and evidence coverage for one example.
5. **Benchmark discipline:** inspect five FastAPI and five Django JSONL rows;
   explain development versus reserved test and why a freeze is required.
6. **Answer evaluation:** read generation, judge, and human-review modules;
   distinguish incorrect-but-faithful, correct-but-unfaithful, and correct
   abstention.
7. **Reliability engineering:** read the runner, freeze record, quality gate,
   and GitHub workflow; explain signatures, checkpoints, and CI.
8. **Results:** study the FastAPI final summary and Django development report;
   explain every number and limitation.
9. **Demo and interview:** open the live dashboard and practice a 30-second and
   two-minute explanation without overclaiming.

## 13. Ready-to-copy prompt for another coding agent

Give the agent repository access, then paste this prompt:

```text
You are continuing my RAG Evaluation Harness. The original repository is
https://github.com/Sneha-090/RAG-eval-harness and the only local working folder
is D:\rag-eval-harness. Do not create a duplicate project.

Before editing anything:
1. Read HANDOFF.md completely.
2. Read README.md, docs/PROJECT_GUIDE.md, docs/RUNBOOK.md,
   docs/STUDY_AND_INTERVIEW.md, and PROJECT_LOG.md.
3. Inspect git status and the latest commits.
4. Verify claims from versioned JSON reports instead of trusting chat history.
5. Explain the current state and your proposed next milestone to me in very
   easy Hinglish.

The core FastAPI v1 benchmark is frozen and complete. Never tune it from its
already-used test split or present a rerun as fresh held-out evidence. The
Django 5.2 corpus and 50-question draft exist, all four development retrieval
configurations were compared, and the Django reserved test is still untouched.
The next required milestone is semantic author review of all 50 Django records,
followed by a reviewed development rerun, Django judge calibration, a committed
v2 freeze, and only then the one-time reserved test.

Rules:
- Work only in D:\rag-eval-harness.
- Preserve my configured Git author and never add Codex/AI attribution or
  co-author trailers.
- Make small meaningful commits and push verified milestones.
- Inspect and preserve unrelated user changes.
- Never commit credentials or caches.
- Never change labels or thresholds just to improve scores.
- Keep retrieval, evidence completeness, correctness, faithfulness,
  abstention, and latency separate.
- Do not run Django --split test before the committed v2 freeze.
- Run validation, relevant tests, and ty check before code commits.
- After every milestone, teach me what changed in very easy Hinglish.

Start by reporting:
A. the five-sentence project story,
B. the exact verified progress,
C. the next milestone and its acceptance criteria,
D. any contradiction you find between documentation and repository evidence.
Do not implement until you have completed that inspection and explanation.
```

## 14. Recent milestone commits

These commits make the latest extension easy to audit:

| Commit | Milestone |
| --- | --- |
| `2582180` | Made the repository type-clean. |
| `e1df2b9` | Added isolated Django corpus support. |
| `3d7b6c2` | Added the grounded Django benchmark draft. |
| `ed00d44` | Made reports score the selected corpus. |
| `56dcacc` | Published the Django four-configuration development comparison. |
| `3deccfe` | Added the cross-domain cloud dashboard. |
| `68db6c2` | Linked the verified live deployment. |

## 15. Truth hierarchy

When sources disagree, use this order:

1. frozen machine-readable manifests and versioned evaluation JSON;
2. committed corpus files and question datasets;
3. executable code and functional tests;
4. result summaries beside the JSON evidence;
5. this handoff;
6. README and older narrative documents;
7. remembered chat history.

The project is already a strong resume project because v1 is complete and
measured. The work above does not rescue a broken project; it upgrades a solid
single-domain evaluation into stronger cross-domain evidence while preserving
experimental honesty.
