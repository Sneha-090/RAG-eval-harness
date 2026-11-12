# Four-configuration development retrieval comparison

All four configurations were captured from Git commit `a3062d6` with the same
12-page corpus, 40 development questions, MiniLM dense embedding model, top-five
limit and metric implementation. Retrieval metrics score the 36 answerable
questions; four unanswerable questions are excluded by the metric contract. No
reserved test question or answer-generation API was run.

| Config | Pipeline | Hit@5 | MRR@5 | Source recall@5 | Evidence coverage@5 | Complete evidence@5 | Mean retrieval |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Fixed + dense | 1.0000 | **0.9583** | 1.0000 | 0.8375 | 27/36 (75.0%) | 0.0201 s |
| B | Semantic + dense | 1.0000 | 0.9537 | 1.0000 | 0.8426 | **29/36 (80.6%)** | 0.0191 s |
| C | Fixed + hybrid | 0.9722 | 0.9051 | 0.9444 | 0.8302 | 26/36 (72.2%) | 0.0218 s |
| D | Fixed + hybrid + reranker | 0.9722 | 0.9213 | 0.9444 | **0.8516** | 27/36 (75.0%) | 0.8974 s |

Configuration B is the provisional development winner: it has the highest
complete-evidence rate while retaining perfect Page Hit@5 and required-source
recall. A has the best MRR by a small margin. D has the highest average exact
evidence coverage, but it does not beat B on complete evidence and is much
slower in these local retrieval-only measurements.

## What reranking changed

D reranks 20 hybrid candidates with the pinned
`cross-encoder/ms-marco-MiniLM-L6-v2` revision
`233902d25c440f23af6f7d6e94d2946bac0bee0a`. Relative to C, it recovered
complete evidence for q018 and q039 and lost it for q041, producing a net gain
of one complete-evidence question. It improved MRR and evidence coverage over C
but did not recover C's q015 page miss. For q015, the reranker strongly preferred
query-parameter passages for a path-parameter question, leaving the gold page
outside the final top five.

The reranker mean was 0.8974 seconds per question versus roughly 0.02 seconds
for the other configurations. Model loading is excluded, but these are still
single local runs rather than a dedicated latency benchmark; exact speed ratios
should not be generalized.

## Interpretation and limits

- A more complex pipeline did not automatically produce the best retrieval.
- Semantic boundaries helped complete-evidence retrieval on this corpus.
- The general-purpose reranker improved hybrid retrieval but introduced a large
  latency cost and did not outperform B overall.
- The benchmark has an AI-assisted reference cross-check, while the separate
  human-review checkboxes and judge-calibration labels remain incomplete.
- Development results selected B provisionally. The test split must remain
  untouched during further tuning and should be run once after the benchmark is
  frozen.
- Generated-answer correctness, faithfulness, abstention and end-to-end latency
  are not established by this retrieval comparison.

Exact values, run signatures and hashes are stored in `comparison.json`.
