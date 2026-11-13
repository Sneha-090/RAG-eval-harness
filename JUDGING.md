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


## Independent human review

For the versioned real packet, use the guided screen instead of manually editing
CSV cells:

    python -m streamlit run streamlit_app.py

The screen shows one answer at a time, saves each decision atomically to the
versioned labels file, and resumes at the first unfinished answer. It reads only
the blind packet: judge verdicts stay hidden and no provider/API call is made.
The command-line export and comparison workflow remains the source of truth.

    python -m src.evaluation.human_review export --run runs/answers-dev-01 --output runs/human-dev-01

This selects 10–15 successful answerable DEVELOPMENT answers using category
round-robin, without reading judge scores. Reserved test questions are excluded.
It creates review.md (questions, references, answers and actual retrieved context),
labels.csv (blank scores), and an input-pinned packet.json. The export refuses
to overwrite an existing packet. The human author must fill labels.csv before
inspecting model verdicts; do not copy scores from the judge.

After the human labels are complete:

    python -m src.evaluation.human_review compare --packet runs/human-dev-01/packet.json --labels runs/human-dev-01/labels.csv --judge runs/judge-dev-01 --output runs/agreement-dev-01.json

The comparison rejects blank/incomplete labels, invalid score scales, mismatched
answers and unsuccessful judge verdicts. It reports exact agreement separately
for correctness and faithfulness and lists every disagreement. It does not
automatically approve a judge or invent an acceptance threshold. The calibration
sample is small, developmental and deliberately diverse, not a population estimate.

The initial live check on 26 October 2026 successfully generated and judged one
answer. Both provider calls worked. All 40 offline tests passed after adding the
human-review workflow. No real human agreement score has been measured yet.


## Real calibration packet

The first real packet is versioned at calibration/2026-10-26. The answer capture
requested 15 development questions and completed all 15 after retrying four
transient connection failures. The judge also completed all 15, including the
one unanswerable question; 14 answerable outputs are exported for human review.
No judge scores are in the blind packet. Use the commands in its README after
filling the CSV labels. The saved local judge directory is
runs/judge-calibration-20261026. A repeat reused all 15 saved verdicts.

The author completed the blind 14-answer review on 13 November 2026. Exact
human–judge agreement was 100.0% for correctness and 78.6% for faithfulness.
All three faithfulness differences were inspected only after saving the blind
result; the retrieved text supported the judge label in each case. The original
agreement remains 78.6% and is not rewritten as a post-hoc 100% score. See
calibration/2026-10-26/agreement-review.md. Abstention remains uncalibrated and
the judge remains provisional pending a fresh independent sample.


## Saved answer-quality report

Build a deterministic report without making generator or judge API calls:

    python -m src.evaluation.answer_report --run runs/answers-calibration-20261026 --judge runs/judge-calibration-20261026 --packet calibration/2026-10-26/packet.json --labels calibration/2026-10-26/labels.csv --agreement calibration/2026-10-26/agreement.json --output reports/my-answer-report

The reporter recomputes and verifies human agreement, checks capture and judge
signatures, requires complete successful records, then reports correctness,
faithfulness, abstention, per-question results and nearest-rank P95 latency.
Answer latency is retrieval plus successful generation only. It excludes pacing,
judge time, model preload and failed-attempt time; resumed questions are counted
separately. The first versioned report is under
reports/answer-quality-config-a-calibration-2026-11-13.
