# Answer judging (provisional)

Capture answers first, then judge the saved answers without regenerating them:

    python -m src.evaluation.run --mode answers --limit 15 --output runs/answers-dev-01
    python -m src.evaluation.judge --run runs/answers-dev-01 --output runs/judge-dev-01

This explicitly calls external providers using the ignored local .env keys.
The generator is configured in src/generation/llm.py, as is the default judge.
The judge CLI can record an explicit model override with --model. A listed
model must still be checked for availability before a large run.

Only answer-mode captures can be judged. The input manifest is checked, captured
answers and context are preserved, and the judge never edits the original run.
Outputs contain a manifest, per-question verdicts and a summary. Judge responses
must satisfy the exact numeric/null schema defined by the frozen metric scales.
Malformed output or API errors are recorded as failures, never as zero scores.
Provider response bodies, headers and invalid raw output are not persisted.

Repeat the same command to reuse successful verdicts. Failed verdicts retry only
with --retry-errors; changes to captured answers, model, prompt or implementation
require a new output directory. --delay controls scheduling between judge calls.
It defaults to five seconds; adjust it to your actual provider rate limits.

All summary scores are **provisional**, with human_validated=false. They must
not support pipeline-comparison claims until an independently labelled human
sample has been compared with the judge. Correctness uses 0/0.5/1; faithfulness
uses 0/1; both exclude unanswerable questions. Abstention uses 0/1 on unanswerable
questions only. No exact refusal phrase is required by the judge.

Validation on 26 October 2026: 34 offline tests passed. This initial checkpoint
does not claim a successful live provider call or human agreement score.
