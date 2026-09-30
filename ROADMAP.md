

RAG Eval Harness: Frozen Roadmap (Lean, 5 core milestones)
Status: FROZEN. Changes only after a milestone is completed, and only via PARKING_LOT.md.

Goal
Build a document-agnostic RAG system plus an automated evaluation harness that measures quality, compares four pipeline configurations, and detects regressions in CI.

Benchmark corpus
FastAPI official documentation (tutorial section), 10-12 pages, frozen at one recorded Git commit. FastAPI is only the first benchmark corpus, not the permanent domain. No FastAPI-specific logic inside the RAG core.

Stack
Python, Chroma, GitHub Actions. LLM and embedding providers stay replaceable. Budget: zero to Rs 500.

Milestone 1: Setup + metrics contract
Create repo and environment
Clone the FastAPI source repo, record the commit hash
Select 10-12 tutorial pages (include some closely related pages so retrieval is genuinely tested)
Write METRICS.md: exact definitions and scoring rules for
Retrieval: Hit@K / Recall@K
Answer correctness
Faithfulness
Latency (average + P95)
Small inspection script: file count, size, basic text stats
Done when: the inspection script runs on the selected pages and METRICS.md defines every metric. No embeddings or Chroma before this.

Milestone 2: Baseline RAG (Config A)
Load and normalize documents
Fixed-size chunking
Embeddings + Chroma
Top-k retrieval + LLM answer
Done when: 5 hand-picked questions return sensible answers with their retrieved sources visible.

Milestone 3: Eval set + harness
Eval set of ~50 questions: direct, multi-part, similar-content, and ~5 unanswerable (answer not in corpus)
Each record: question, reference_answer, gold_source, evidence
Harness: one command runs all questions, captures retrieved sources, answer, latency, scores, and writes a report
LLM judge validation: hand-label 10-15 answers yourself and measure how often the judge agrees
Done when: eval set is versioned and frozen, run-eval produces a report, and judge agreement is known.

Milestone 4: Four-config comparison
Config	Pipeline
A: Baseline	Fixed-size chunking + dense retrieval
B: Semantic	Semantic chunking + dense retrieval
C: Hybrid	Fixed-size chunking + BM25 + dense retrieval
D: Reranked	Fixed-size chunking + hybrid retrieval + reranker
Same questions, same corpus, same metric definitions, same generation settings.

Done when: a table of real results exists, with an explanation for any config that does not improve (no gain or a regression is a valid result).

Milestone 5: Regression gate + CI
Save a baseline report
Gate rule: metric must not fall below a configured minimum and must not drop from baseline by more than a documented allowed regression (thresholds chosen after seeing the real baseline)
GitHub Actions runs tests and deterministic checks (e.g. retrieval Hit@K). Full LLM-judged evaluation runs manually or on a schedule with cached outputs, to avoid slow, flaky, rate-limited CI.
Done when: a deliberately bad change makes CI fail, and a good change passes.

Stretch (only after Milestone 5 is complete)
Generic ingestion (TXT/Markdown, PDF, optional DOCX) with FastAPI-specific logic kept out of the core
Simple API/UI for upload and Q&A, plus README with architecture, metrics, limitations, and reproducible setup
Rules
No milestone starts until the previous "Done when" is met.
New ideas go in PARKING_LOT.md, not into the roadmap mid-milestone.
The eval set is not edited during experiments to improve scores.
Pin the FastAPI corpus to the recorded commit.
Define every metric before showing results using it.
Record model, chunking, top-k, and retrieval settings for every run.
README and resume contain only real measured numbers.
When a result gets worse, investigate and explain it instead of hiding it.
Build one layer at a time; understand each component (why, what, code, output) before moving on.
Resume story (fill numbers only after real experiments)
Built a document-agnostic RAG system with an automated evaluation and regression-testing harness; benchmarked four retrieval pipeline configurations on a version-pinned technical documentation corpus, measured retrieval quality, answer quality and latency, and integrated threshold-based checks into GitHub Actions.


