# Frozen benchmark v1: final reserved-test result

Configuration B was selected on the 40-question development split, then the
benchmark, corpus, pipeline, generator and calibrated judge were frozen in
commit `7ff5a61` before the ten reserved questions were evaluated. No v1 tuning
was performed from these results.

## Final metrics

| Layer | Metric | Result |
|---|---|---:|
| Retrieval | Page Hit@5 | 9/9 (100%) |
| Retrieval | MRR@5 | 1.0000 |
| Retrieval | Required-source recall@5 | 1.0000 |
| Retrieval | Exact evidence coverage@5 | 0.6389 |
| Retrieval | Complete evidence@5 | 5/9 (55.6%) |
| Answer | Correctness | 7/9 (77.8%) |
| Answer | Faithfulness | 7/9 (77.8%) |
| Answer | Abstention | 1/1 (100%) |
| Latency | Mean retrieval | 0.0337 s |
| Latency | Mean successful answer stages | 1.1764 s |

The hidden judge was calibrated on a separate mixed development sample after
human labels were frozen: exact agreement was 8/8 for correctness, 8/8 for
faithfulness and 2/2 for abstention.

## What the failures show

- q021 and q045 were answerable and had useful context, but the generator
  refused. These are correctness failures caused by over-abstention.
- q036 and q046 matched the reference answer, but one requested fact was absent
  from the retrieved chunks. These are faithfulness failures even though the
  answers sounded correct.
- q050 was unsupported by the corpus and the generator correctly abstained.

This separation is the purpose of the harness: finding the correct page is not
the same as retrieving every required fact, and a reference-correct answer is
not necessarily grounded in the supplied context.

## Reproducibility and limitations

The machine-readable freeze is in
`data/eval/benchmark-freeze-v1.json`. `retrieval.json` contains deterministic
retrieval scores, while `evaluation.json` contains answer scores, calibration
provenance, latency and per-question outcomes.

The benchmark is small, uses one FastAPI domain and has a ten-question reserved
split. All 50 references were AI-assisted cross-checked against the pinned
sources, but the full item-by-item author checklist is incomplete. Judge
calibration has one human reviewer and only ten outputs. These results are a
reproducible project evaluation, not a claim of production readiness or broad
domain generalization.
