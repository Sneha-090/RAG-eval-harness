# Final reserved-test answer-quality report

Configuration B; 10/10 saved answers scored.
Generator: `groq / openai/gpt-oss-120b`.
Judge: `gemini / gemini-3.5-flash`.

## Answer quality

| Metric | Result |
|---|---:|
| Correctness | 7/9 (77.8%) |
| Faithfulness | 7/9 (77.8%) |
| Abstention | 1/1 (100.0%) |

These are calibrated model-judge estimates, not general RAG accuracy.

## Human calibration

Blind exact agreement: correctness 100.0% on 8 labels; faithfulness 100.0% on 8 labels; abstention 100.0% on 2 labels.

## Latency

| Stage | Count | Mean | Nearest-rank P95 |
|---|---:|---:|---:|
| Retrieval | 10 | 0.0337 s | 0.0482 s |
| Generation | 10 | 1.1427 s | 1.5598 s |
| Answer: successful stages | 10 | 1.1764 s | 1.5912 s |
| Judge (excluded) | 10 | 4.2009 s | 7.9571 s |

Resumed questions: 0.

## Per-question scores

| ID | Category | Answerable | Correctness | Faithfulness | Abstention | Resumed |
|---|---|---:|---:|---:|---:|---:|
| q019 | direct | yes | 1 | 1 | — | no |
| q020 | direct | yes | 1 | 1 | — | no |
| q021 | direct | yes | 0 | 1 | — | no |
| q029 | similar_page | yes | 1 | 1 | — | no |
| q030 | similar_page | yes | 1 | 1 | — | no |
| q035 | multi_part | yes | 1 | 1 | — | no |
| q036 | multi_part | yes | 1 | 0 | — | no |
| q045 | paraphrase | yes | 0 | 1 | — | no |
| q046 | paraphrase | yes | 1 | 0 | — | no |
| q050 | unanswerable | no | — | — | 1 | no |

## Limitations

- Judge scores are model-based estimates backed by a small, single-reviewer human calibration; they are not general RAG accuracy.
- The reserved split covers the same frozen FastAPI corpus as development and does not establish cross-domain generalization.
- Successful-stage answer latency is retrieval plus successful generation; scheduling delays, judge time, model preload and failed-attempt time are excluded.
