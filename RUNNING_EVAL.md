# Draft evaluation runs

Run commands from D:\rag-eval-harness with the existing virtual environment active.

For the model cache downloaded during setup, set this once per PowerShell session:

    $env:HF_HOME = 'D:\rag-eval-harness\.cache\huggingface'

    python -m src.evaluation.validate
    python -m unittest discover -s tests -v
    python -m src.evaluation.run --output runs/dev-retrieval-01

The default mode only retrieves; it makes no generator or judge API calls.
The local embedding model must already be cached to work offline.
The baseline Chroma index must exist and match the current document chunks.
If necessary, build it with `python -m src.retrieval.index`.

To explicitly call the configured answer generator:

    python -m src.evaluation.run --mode answers --limit 2 --output runs/dev-answers-01

This uses GROQ_API_KEY from the local .env and waits 15 seconds before each
generation call. Adjust --delay for your actual rate limits. No judge is called.
No keys or HTTP response headers are saved.

Each output directory contains a manifest (selected questions, settings, source
and corpus hashes, code commit, index metadata), one JSON checkpoint per question,
and a summary with completed/failed counts. Retrieved chunk text and separate
retrieval/generation timing are retained. Quality scores are deliberately absent:
the benchmark and evidence-scoring contract still need review.

Re-run the identical command to skip completed questions. Failed questions are
retained unless --retry-errors is supplied. Retrieval is saved before generation,
so a failed generation can retry without repeating retrieval. Changed inputs,
source, settings, index content, or code commit require a new output directory.
Avoid editing the code or rebuilding the index during a run.

Only one process can use an output directory at a time. After a forced process
termination, confirm the process has stopped before removing its .lock file.
Checkpoints are atomic, but an API response received immediately before a crash
cannot always be saved; a retry may repeat that call.

Errors store exception types only to avoid leaking credentials. A failed run
exits nonzero. Inspect the local setup/provider console when investigating an
error. Results and API keys must not be committed automatically.

The elapsed_s field is diagnostic wall time (including pacing and failed
attempts); it is not the benchmark latency metric. Per-stage times exclude the
runner's pacing. No average/P95 latency result is claimed yet. First retrieval
may include embedding model loading. The current index can validate stored text
and metadata, but its original embedding model revision is not recorded; future
index provenance must fix this before controlled comparisons.

## Verification on 25 October 2026

All 13 unit tests passed. The local index matched the current corpus/chunks.
The public embedding model was downloaded into the ignored project cache.
A retrieval-only run completed all 10 draft questions with zero errors; repeating
it offline left all 10 question checkpoint timestamps unchanged. No generator
or judge API calls were made. This is execution verification, not quality scoring.
An earlier offline attempt failed because the model had not yet been cached;
the runner now loads the model before starting question checkpoints.
