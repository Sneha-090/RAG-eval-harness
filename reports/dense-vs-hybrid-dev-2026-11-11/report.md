# Dense vs. hybrid retrieval on the draft development benchmark

Measured 11 November 2026. Both configurations processed all 40 development
questions successfully. Evidence metrics use the 36 answerable questions.
The ten reserved test questions remain unevaluated.

A uses the original dense search. C searches the same chunks with dense search
and BM25, then combines ranks using reciprocal rank fusion (RRF). Each ranker
supplies up to 20 candidates, RRF uses a constant of 60, and both configurations
return five passages. The corpus, chunks, embedding model, and metric definitions
match across runs. This experiment measures retrieval. Generation and judging
are outside the measured run.

| Metric | A: dense | C: hybrid |
|---|---:|---:|
| Questions with complete evidence | 27/36 (75.0%) | 26/36 (72.2%) |
| Mean evidence coverage@5 | 83.75% | 83.02% |
| Page Hit@5 | 100.00% | 97.22% |
| Mean retrieval time | 21.0 ms | 20.4 ms |
| P95 retrieval time | 25.4 ms | 23.7 ms |

Hybrid recovered complete evidence on 3 questions and lost it on
4. Timings come from one local run per configuration (A followed by
C) and exclude model loading and keyword index construction. Evidence coverage
uses the existing exact-text rubric. Benchmark review and the original index
embedding revision remain limitations.

## Changed cases

- **Recovered complete evidence (q011)** — What class should a request-body data model inherit from?
  Evidence coverage moved from 0.0% to 100.0%.
  Gold source(s): body.md. Both ranked passage lists are in the JSON report.
- **Lost complete evidence (q005)** — How do I explicitly read a header versus a cookie, rather than treating either as a query parameter?
  Evidence coverage moved from 100.0% to 50.0%.
  Gold source(s): header-params.md, cookie-params.md. Both ranked passage lists are in the JSON report.

## Reproduce

Use the existing baseline index and the environment described in [RUNNING_EVAL.md](../../RUNNING_EVAL.md).

    python -m src.evaluation.run --config A --split dev --output runs/dev-dense
    python -m src.evaluation.report --run runs/dev-dense
    python -m src.evaluation.run --config C --split dev --output runs/dev-hybrid
    python -m src.evaluation.report --run runs/dev-hybrid

[Paired observations and run settings](comparison.json)
