# Provisional answer-quality report

Configuration A; 15/15 saved answers scored.
Generator: `groq / openai/gpt-oss-120b`.
Judge: `gemini / gemini-3.5-flash`.

## Answer quality

| Metric | Result |
|---|---:|
| Correctness | 13/14 (92.9%) |
| Faithfulness | 13/14 (92.9%) |
| Abstention | 1/1 (100.0%) |

These are provisional judge scores, not general RAG accuracy.

## Human calibration

Blind exact agreement on 14 answerable outputs: correctness 100.0%; faithfulness 78.6%. Abstention was not human-calibrated.

## Latency

| Stage | Count | Mean | Nearest-rank P95 |
|---|---:|---:|---:|
| Retrieval | 15 | 0.0366 s | 0.1350 s |
| Generation | 15 | 1.0740 s | 1.8681 s |
| Answer: successful stages | 15 | 1.1107 s | 1.8977 s |
| Judge (excluded) | 15 | 6.2032 s | 18.6297 s |

Resumed questions: 4.

## Per-question scores

| ID | Category | Answerable | Correctness | Faithfulness | Abstention | Resumed |
|---|---|---:|---:|---:|---:|---:|
| q001 | direct | yes | 1 | 0 | — | no |
| q002 | direct | yes | 1 | 1 | — | no |
| q003 | direct | yes | 1 | 1 | — | no |
| q004 | direct | yes | 1 | 1 | — | no |
| q005 | similar_page | yes | 1 | 1 | — | no |
| q006 | multi_part | yes | 1 | 1 | — | no |
| q007 | multi_part | yes | 1 | 1 | — | no |
| q008 | paraphrase | yes | 1 | 1 | — | no |
| q009 | paraphrase | yes | 1 | 1 | — | yes |
| q010 | unanswerable | no | — | — | 1 | yes |
| q011 | direct | yes | 0 | 1 | — | yes |
| q012 | direct | yes | 1 | 1 | — | yes |
| q013 | direct | yes | 1 | 1 | — | no |
| q014 | direct | yes | 1 | 1 | — | no |
| q015 | direct | yes | 1 | 1 | — | no |

## Limitations

- Draft development sample of 15 questions; the reserved test split was not used.
- Judge scores are provisional: correctness agreement was measured on 14 answers, faithfulness agreement was 78.6%, and abstention has no human calibration.
- The historical capture uses configuration A, not the selected configuration B.
- Successful-stage answer latency is retrieval plus successful generation; scheduling delays, judge time, model preload and failed-attempt time are excluded.
- Four resumed questions are identified, but total retry cost cannot be reconstructed from the saved historical checkpoints.
