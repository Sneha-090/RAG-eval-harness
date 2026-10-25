# Draft development snapshot

Captured on 25 October 2026 using configuration A and metric contract v2.
The manifest pins the code at capture, selected development records, corpus and
settings. evaluation.json additionally hashes the scorer used to generate scores.
The report-display/scorer labels were finalized after capture without changing
retrieval observations or the metric contract. No model/API calls are required
to inspect the saved observations.

40/40 retrievals completed; 36 are answerable. The four unanswerable retrievals
do not contribute to quality scores. All 10 test questions remain unevaluated.
Full evidence was retrieved on 27/36 answerable questions despite 36/36 page hits.
No labels or pipeline settings were tuned after these scores were viewed.

These are draft benchmark measurements, not a frozen regression baseline or
validated answer-quality results. Review and freezing, index embedding revision
provenance, answer judging and human judge agreement remain pending.

observations.jsonl deliberately contains retrieved corpus text and timings only;
the local API keys, HTTP response headers, model cache and database are excluded.
