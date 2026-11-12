# Fixed vs. semantic chunking development pilot

Configuration A uses fixed 550-character chunks with 80-character overlap.
Configuration B uses source-contiguous semantic chunks: paragraph/sentence
units are embedded, large adjacent cosine-distance changes become eligible
boundaries, and chunks remain between a soft 300-character minimum and a hard
900-character maximum where possible. Both use the same MiniLM embedding model,
dense retrieval, top-five limit, corpus, development questions and metric code.

The run contains 40 development questions. Retrieval metrics use the 36
answerable questions; four unanswerable questions are excluded as defined in
the metric contract. The ten reserved test questions were not run.

| Metric | A: fixed + dense | B: semantic + dense | Change |
|---|---:|---:|---:|
| Page Hit@5 | 36/36 (100.0%) | 36/36 (100.0%) | 0 |
| MRR@5 | 0.9583 | 0.9537 | -0.0046 |
| Required-source recall@5 | 1.0000 | 1.0000 | 0 |
| Exact evidence coverage@5 | 0.8375 | 0.8426 | +0.0051 |
| Complete evidence@5 | 27/36 (75.0%) | 29/36 (80.6%) | +2 questions |
| Indexed chunks | 215 | 164 | -51 |

Semantic chunking recovered complete evidence for q015, q017, q023, q027 and
q044, while losing it for q022, q039 and q040. The net result is two additional
questions with all required evidence in the top five. This is a modest
improvement, not a universal win: MRR declined slightly and several individual
questions regressed.

The recorded retrieval-only means were 0.0220 seconds for A and 0.0172 seconds
for B; nearest-rank P95 values were 0.0243 and 0.0219 seconds respectively.
These are descriptive local measurements from runs on different dates, so they
do not establish that semantic chunking is faster.

## Limitations

- The small single-domain benchmark has an AI-assisted reference cross-check,
  but the separate human-review checkboxes remain incomplete.
- These are development-set retrieval results, not reserved-test results.
- Exact evidence coverage measures source-text overlap, not answer correctness.
- Generated-answer correctness, faithfulness, abstention and end-to-end latency
  were not compared in this pilot.
- The semantic thresholds were recorded before this run; no development-result
  tuning was performed after seeing these scores.

Machine-readable metrics, changed question IDs and provenance hashes are in
`comparison.json`.
