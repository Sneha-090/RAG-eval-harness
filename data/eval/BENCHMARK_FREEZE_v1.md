# Benchmark freeze v1

The 50-question FastAPI benchmark and selected configuration B pipeline were
frozen before the reserved-test run on 22 November 2026. The machine-readable
contract is `benchmark-freeze-v1.json`.

## What is frozen

- Twelve pinned FastAPI documentation pages, identified by per-file hashes.
- Fifty questions: 40 development and 10 reserved test.
- Configuration B: semantic chunking, dense retrieval and top-k 5.
- `all-MiniLM-L6-v2` at the pinned model revision.
- Groq `openai/gpt-oss-120b` with the hashed answer prompt.
- Gemini `gemini-3.5-flash` with the calibrated, hashed judge prompt.
- The deterministic retrieval metric definitions and the stored semantic index
  content fingerprint captured by the evaluation runner.

## Review evidence and limitation

All 50 references received an AI-assisted NotebookLM cross-check against the
pinned corpus, followed by programmatic evidence validation. A fresh blind
human review of ten generated development outputs matched the hidden judge on
8/8 correctness, 8/8 faithfulness and 2/2 abstention labels.

The full 50-item author checklist is not complete. This limitation is preserved
in the freeze manifest and must accompany final claims. The reserved test is a
held-out question split over the same 12-page FastAPI domain, not evidence of
cross-domain generalization.

## Test discipline

The ten reserved IDs are q019, q020, q021, q029, q030, q035, q036, q045, q046
and q050. They may be evaluated once with the frozen pipeline. Test failures
must be reported, not used to tune this version. Any later changes require a
new named version rather than silently replacing this result.
