# Provisional paired answer comparison

Configuration A versus configuration B on 15 identical development questions.

**No winner claim is allowed yet.** Candidate answers have not received a fresh blind human review.

## Fairness checks

| Check | Result |
|---|---:|
| Same Questions And References | pass |
| Same Corpus | pass |
| Same Generator | pass |
| Same Answer Prompt | pass |
| Same Retrieval Depth | pass |
| Same Embedding Model | pass |
| Same Judge | pass |
| Same Judge Prompt | pass |

## Answer quality

| Metric | Config A | Config B | Mean delta | Improved | Regressed | Tied |
|---|---:|---:|---:|---:|---:|---:|
| Correctness | 92.9% | 92.9% | +0.0% | 0 | 0 | 14 |
| Faithfulness | 92.9% | 92.9% | +0.0% | 1 | 1 | 12 |
| Abstention | 100.0% | 100.0% | +0.0% | 0 | 0 | 1 |

The aggregate scores tie. Config B improves one faithfulness case and regresses one other case.

## Latency (descriptive)

| Stage | Config A mean | Config B mean | Config A P95 | Config B P95 |
|---|---:|---:|---:|---:|
| Retrieval | 0.0366 s | 0.0509 s | 0.1350 s | 0.0940 s |
| Generation | 1.0740 s | 1.3427 s | 1.8681 s | 1.8156 s |
| Answer: successful stages | 1.1107 s | 1.3936 s | 1.8977 s | 1.8600 s |

## Per-question paired scores

| ID | Correctness A→B | Faithfulness A→B | Abstention A→B | Answer changed |
|---|---:|---:|---:|---:|
| q001 | 1→1 | 0→1 | —→— | yes |
| q002 | 1→1 | 1→1 | —→— | yes |
| q003 | 1→1 | 1→1 | —→— | yes |
| q004 | 1→1 | 1→1 | —→— | yes |
| q005 | 1→1 | 1→1 | —→— | yes |
| q006 | 1→1 | 1→1 | —→— | yes |
| q007 | 1→1 | 1→1 | —→— | yes |
| q008 | 1→1 | 1→1 | —→— | yes |
| q009 | 1→1 | 1→0 | —→— | yes |
| q010 | —→— | —→— | 1→1 | no |
| q011 | 0→0 | 1→1 | —→— | no |
| q012 | 1→1 | 1→1 | —→— | yes |
| q013 | 1→1 | 1→1 | —→— | yes |
| q014 | 1→1 | 1→1 | —→— | yes |
| q015 | 1→1 | 1→1 | —→— | yes |

## Changed score cases

- **q001**: faithfulness +1. Candidate judge: The answer accurately states that `Cookie` must be imported and declared to read a cookie instead of a query parameter, which agrees with the reference answer and is fully supported by the retrieved context.
- **q009**: faithfulness -1. Candidate judge: The answer correctly states that a query argument is made mandatory by omitting a default value, matching the reference answer. However, it fails faithfulness because it includes code examples using `Query(...)` (ellipsis syntax) which are not present anywhere in the retrieved context.

## Shared correctness failures

- **q011**: both configurations scored below fully correct. Candidate judge: The model stated it could not find the information, which constitutes an unjustified refusal since the question is marked as answerable. Faithfulness is 1 because a simple refusal contains no unsupported factual claims.

## Limitations

- This is a 15-question development calibration sample, not the reserved test split.
- Candidate judge scores have not received an independent blind human review.
- Abstention has only one example and has not been human-calibrated.
- Latency came from separate historical runs, so it is descriptive rather than a controlled speed benchmark.
- A winner must not be claimed from this provisional report.
