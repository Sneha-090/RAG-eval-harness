# Runbook

This file is the practical guide for setting up, checking, running and
troubleshooting the repository. Commands assume Windows and the repository at
`D:\rag-eval-harness`; change the path if the clone is elsewhere.

## Shell rule that caused earlier confusion

PowerShell and Command Prompt use different drive-changing syntax.

PowerShell:

```powershell
Set-Location D:\rag-eval-harness
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Command Prompt:

```bat
cd /d D:\rag-eval-harness
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Do not use `cd /d` in PowerShell. Do not use PowerShell's leading `&` in
Command Prompt.

## Clean setup

```powershell
Set-Location D:\rag-eval-harness
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The first embedding run downloads pinned Hugging Face models unless they are
already cached. A completely clean installation has not been independently
reproduced on a second machine; record any issue instead of silently changing
versions.

## Environment variables and secrets

Retrieval, tests, reports and dashboard do not need paid API keys.

Answer generation/judging needs an ignored `.env` file:

```text
GROQ_API_KEY=...
GEMINI_API_KEY=...
```

Never commit `.env`, keys, provider response bodies or local caches.

## The normal verification sequence

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.validate
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Expected current state: both 50-record benchmark files validate, 77 functional
tests pass and the full repository type check is clean:

```powershell
& .\.venv\Scripts\ty.exe check
```

## Open the local dashboard

```powershell
& .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the localhost URL printed by Streamlit. The default Results dashboard
reads committed JSON reports and makes no model/API calls. Use the sidebar for
Blind review.

## Rebuild the retrieval indexes

Configuration A/C/D fixed chunks:

```powershell
& .\.venv\Scripts\python.exe -B -m src.retrieval.index
```

Configuration B semantic chunks:

```powershell
& .\.venv\Scripts\python.exe -B -m src.retrieval.index --config B
```

The runner checks that the stored index exactly matches current corpus and
chunking output before it will reuse it.

## Safe development retrieval evaluation

Use a new output folder every time inputs intentionally change:

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.run `
  --config B --split dev --output runs\my-config-b-dev
& .\.venv\Scripts\python.exe -B -m src.evaluation.report `
  --run runs\my-config-b-dev
```

This performs no generator or judge calls. Results appear inside the run folder.

## Enforce the local quality gate

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.gate `
  --run runs\my-config-b-dev
& .\.venv\Scripts\python.exe -B -m src.evaluation.gate_demo `
  --run runs\my-config-b-dev
```

The first must accept a matching B development result. The second deliberately
degrades one result and succeeds only when the gate rejects it.

## Generate development answers

This makes external Groq calls, so choose explicit IDs or a small limit first:

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.run `
  --config B --split dev --mode answers `
  --ids q001 q002 --output runs\answer-smoke
```

On a transient failure, reuse the same unchanged inputs and add
`--retry-errors`. Completed checkpoints are not repeated.

## Judge already-saved answers

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.judge `
  --run runs\answer-smoke --output runs\judge-answer-smoke
```

Retry only failures:

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.judge `
  --run runs\answer-smoke --output runs\judge-answer-smoke --retry-errors
```

Do not judge a human-calibration packet until its human labels are saved,
committed and frozen.

## Recompute mixed calibration agreement

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.human_review compare `
  --packet calibration\2026-11-14\packet.json `
  --labels calibration\2026-11-14\labels.csv `
  --judge runs\judge-blind-calibration-20261114 `
  --output runs\agreement-check.json
```

Expected exact agreement: correctness 1.0 on 8, faithfulness 1.0 on 8 and
abstention 1.0 on 2.

## Generate a calibrated answer report

The scored run and calibration run are deliberately separate. Their judge
model, prompt and implementation contracts must match.

```powershell
& .\.venv\Scripts\python.exe -B -m src.evaluation.answer_report `
  --run runs\final-test-v1-20261122 `
  --judge runs\judge-final-test-v1-20261122 `
  --calibration-judge runs\judge-blind-calibration-20261114 `
  --packet calibration\2026-11-14\packet.json `
  --labels calibration\2026-11-14\labels.csv `
  --agreement calibration\2026-11-14\agreement.json `
  --output runs\my-final-report-check
```

The historical ignored `runs/` folders are local evidence. The public,
versioned final report is under `reports/final-test-v1-2026-11-22/`.

## GitHub Actions

Every push to `main` and every pull request:

1. installs requirements on Python 3.13;
2. runs all functional tests;
3. validates all benchmark evidence;
4. builds the semantic B index;
5. captures 40 development retrievals;
6. scores them and enforces `quality-gate.json`;
7. proves a deliberately degraded result is rejected;
8. uploads run evidence.

LLM generation/judging is intentionally not part of push CI because it is
paid/rate-limited and less deterministic.

## Troubleshooting

### “File does not exist: streamlit_app.py”

The shell is not in the repository. Run the correct `Set-Location` or `cd /d`
command from the first section, or pass the absolute file path.

### “.venv\\Scripts\\python.exe is not recognized”

Either the shell is in the wrong directory or `.venv` does not exist. Check:

```powershell
Test-Path D:\rag-eval-harness\.venv\Scripts\python.exe
```

Create the environment if this returns `False`.

### “Run inputs changed. Use a new output directory.”

This is a safety feature. A signed run folder cannot mix changed questions,
settings or source files. Use a new output folder. Use `--retry-errors` only
when the inputs are unchanged.

### A `.lock` file remains after interruption

First confirm no matching Python evaluation process is still running. Remove
only the exact run folder's stale `.lock`, never a broad path, then resume with
the same command. Existing successful checkpoints will be reused.

### Chroma collection differs from corpus/chunking

Rebuild the relevant index. Do not bypass the equality check.

### Provider 429 or connection error

Wait, then use `--retry-errors` with the same run/output folders. The runner and
judge save successful calls individually.

### Hugging Face unauthenticated warning

Local public models still work, but downloads may be slower/rate-limited. Set a
Hugging Face token only if needed and keep it outside Git.

## Never repeat these final-test actions casually

The v1 reserved split has already been used. Do not tune v1 from it or present a
rerun as a fresh held-out test. Any future algorithm/label change needs a named
v2 protocol, new development work and a newly declared untouched test source.
