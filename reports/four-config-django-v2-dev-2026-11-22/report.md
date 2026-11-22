# Django v2 development retrieval comparison

Date: 22 November 2026  
Corpus: 12 Django 5.2.19 LTS documentation sources pinned at commit
`a3510e06a7598039d0992dd00c736e25dbdc9aab`  
Split: development only (40 questions; 36 answerable)  
Retrieval depth: K = 5

The same questions, evidence, corpus, embedding revision and metric definitions
were used for all four configurations. The ten reserved-test questions were not
run. Retrieval metrics exclude four development questions deliberately marked
unanswerable.

| Config | Pipeline | Hit@5 | MRR@5 | Source recall@5 | Evidence coverage@5 | Complete evidence@5 | Mean retrieval | P95 retrieval |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Fixed + dense | 100% | 0.9375 | 100% | 79.80% | 20/36 (55.56%) | 49.9 ms | 51.8 ms |
| **B** | **Semantic + dense** | **100%** | **0.9384** | **100%** | **84.72%** | **30/36 (83.33%)** | **42.8 ms** | **47.2 ms** |
| C | Fixed + hybrid | 100% | 0.9861 | 100% | 91.28% | 28/36 (77.78%) | 52.3 ms | 56.8 ms |
| D | Fixed + hybrid + reranker | 100% | 1.0000 | 100% | 91.14% | 27/36 (75.00%) | 1,362.2 ms | 1,673.9 ms |

## Decision

Configuration B is selected for the Django v2 development benchmark. The
selection rule prioritizes complete gold evidence in the top five chunks,
because the generator cannot produce a fully grounded answer when required
evidence is missing. B recovered complete evidence for 30 questions, compared
with 28 for C, 27 for D and 20 for A.

C and D ranked the correct source pages slightly better and achieved higher
average evidence coverage. They did not win the primary complete-evidence
metric. D also added roughly 1.3 seconds of per-question retrieval latency on
this machine. This is a useful negative result: more retrieval complexity did
not produce the best outcome for the chosen objective.

## What the numbers mean

All four methods found at least one gold source page for every answerable
development question. That does **not** mean every method retrieved the exact
passage required to answer. A's 100% page hit but 55.56% complete evidence is
the clearest example. The harness measures both so a high page-level score
cannot hide incomplete grounding.

## Limitations and next gate

- The question and reference wording is an AI-assisted draft. Exact evidence
  exists for every answerable item, but semantic author review is pending.
- These are retrieval-only development results; they are not answer accuracy.
- Latency is descriptive for one local Windows machine and excludes model
  startup time.
- The Django reserved test remains untouched. Before opening it, the benchmark
  must receive author review and a committed freeze record.
- No CI threshold will be claimed for Django until the reviewed development
  baseline is frozen.

The machine-readable comparison and per-configuration evaluation JSON files in
this folder preserve the measured values and run signatures.
