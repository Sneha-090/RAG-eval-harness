# Draft baseline retrieval report

K = 5; metric contract v2; draft benchmark; splits: dev.

Retrieval complete: True.

Questions: 40; answerable: 36; missing answerable retrievals: 0.

Scores are fractions from 0 to 1. Answer quality has not been evaluated.

| Group | N | Hit@K | MRR@K | Source recall@K | Evidence coverage@K | Complete evidence@K |
|---|---:|---:|---:|---:|---:|---:|
| Overall | 36 | 1.0000 | 0.9583 | 1.0000 | 0.8375 | 0.7500 |
| direct | 12 | 1.0000 | 0.9583 | 1.0000 | 0.8275 | 0.7500 |
| multi_part | 6 | 1.0000 | 1.0000 | 1.0000 | 0.8333 | 0.8333 |
| paraphrase | 10 | 1.0000 | 0.9000 | 1.0000 | 0.9897 | 0.9000 |
| similar_page | 8 | 1.0000 | 1.0000 | 1.0000 | 0.6655 | 0.5000 |

Retrieval timing samples: 40.

Retrieval only: mean 0.0220 s; nearest-rank P95 0.0243 s.

## Limitations

- Draft benchmark; human review and freezing are pending.
- Averages include available retrievals only; missing counts must be reported.
- Evidence scores measure exact text coverage, not semantic sufficiency.
- Retrieval latency excludes model preloading; it is not end-to-end answer latency.
- No correctness, faithfulness, abstention, or judge-agreement scores exist.

## Questions needing evidence investigation

- q011: evidence coverage 0.0000
- q015: evidence coverage 0.9299
- q017: evidence coverage 0.0000
- q023: evidence coverage 0.5258
- q025: evidence coverage 0.0000
- q026: evidence coverage 0.3333
- q027: evidence coverage 0.4650
- q034: evidence coverage 0.0000
- q044: evidence coverage 0.8968
