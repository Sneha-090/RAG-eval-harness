# Retrieval quality regression gate

The selected development configuration is B: semantic chunking plus dense
retrieval. GitHub Actions rebuilds its index, runs all 40 development questions,
scores the 36 answerable questions and fails when quality drops below the
versioned policy in `quality-gate.json`.

The reserved test split is deliberately excluded from CI so repeated pull
requests cannot tune against it. Generator and judge APIs are also excluded;
the gate is deterministic, local and needs no secrets.

## Protected baseline

| Check | Baseline | Allowed drop |
|---|---:|---:|
| Page Hit@5 | 1.0000 | 0 |
| MRR@5 | 0.9537 | 0.0100 |
| Required-source recall@5 | 1.0000 | 0 |
| Exact evidence coverage@5 | 0.8426 | 0.0050 |
| Complete evidence@5 | 29/36 | 0 questions |

The gate also verifies the dataset hash, metric/scorer hashes, embedding model
and pinned revision, semantic chunk settings, configuration, split, K and run
completeness. Missing or non-finite metrics fail instead of being treated as
zeros or ignored.

## Run locally

From the repository root, with dependencies installed:

    python -m src.retrieval.index --config B
    python -m src.evaluation.run --config B --split dev --output runs/local-gate
    python -m src.evaluation.report --run runs/local-gate
    python -m src.evaluation.gate --run runs/local-gate

The following command creates a degraded report in memory by removing one
complete-evidence success. It succeeds only when the gate rejects that change:

    python -m src.evaluation.gate_demo --run runs/local-gate

## Updating the baseline

Do not loosen thresholds merely to make CI green. A policy update requires a
documented pipeline or metric change, a fresh controlled comparison, preserved
old results and an explanation in PROJECT_LOG.md. Never use the reserved test
split to choose or tune a new threshold.
