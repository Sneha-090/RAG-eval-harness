# Portable project handoff

This is the first file a future maintainer or AI agent should read. It replaces
hidden chat history with repository evidence.

## Current state

Core benchmark v1 is complete and resume-ready:

- one original repository: `https://github.com/Sneha-090/RAG-eval-harness`;
- 12 pinned FastAPI documents;
- 50 evidence-backed questions: 40 development + 10 reserved test;
- four implemented retrieval configurations;
- configuration B selected on development;
- mixed blind human–judge calibration complete;
- benchmark/pipeline freeze committed before the reserved test;
- one-time v1 reserved test complete and versioned;
- deterministic GitHub Actions retrieval gate active;
- saved-results Streamlit dashboard + blind review view;
- 72 passing functional tests;
- final learning, runbook and interview documentation in `docs/`.

## Start reading in this order

1. [README.md](README.md) — public project overview.
2. [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) — story, architecture,
   components, experiments and limitations.
3. [reports/final-test-v1-2026-11-22/SUMMARY.md](reports/final-test-v1-2026-11-22/SUMMARY.md)
   — final result and failure analysis.
4. [docs/RUNBOOK.md](docs/RUNBOOK.md) — exact commands and troubleshooting.
5. [docs/STUDY_AND_INTERVIEW.md](docs/STUDY_AND_INTERVIEW.md) — glossary,
   study plan, resume bullets and interview preparation.
6. [PROJECT_LOG.md](PROJECT_LOG.md) — chronological implementation evidence.

Machine-readable proof:

- `data/eval/benchmark-freeze-v1.json`
- `calibration/2026-11-14/agreement.json`
- `reports/final-test-v1-2026-11-22/retrieval.json`
- `reports/final-test-v1-2026-11-22/evaluation.json`
- `quality-gate.json`

## Final measured numbers

Development selection, 36 answerable questions:

- A complete evidence: 27/36
- B complete evidence: 29/36 — selected
- C complete evidence: 26/36
- D complete evidence: 27/36

Fresh mixed judge calibration:

- correctness exact agreement: 8/8
- faithfulness exact agreement: 8/8
- abstention exact agreement: 2/2

Frozen reserved test, nine answerable + one unanswerable:

- Page Hit@5: 9/9
- MRR@5: 1.0
- source recall@5: 1.0
- exact evidence coverage: 0.6389
- complete evidence: 5/9
- answer correctness: 7/9
- faithfulness: 7/9
- abstention: 1/1
- mean retrieval latency: 0.0337 s
- mean retrieval + generation latency: 1.1764 s

## Known limitations and remaining optional work

Core v1 is complete. The following are improvements, not missing final-result
steps:

1. Complete the 50-item author checklist without changing labels because of
   observed v1 scores; if labels change for factual reasons, create v2.
2. Clear the older full-repository `ty` diagnostics in a behavior-preserving
   refactor. Focused final changed files are already type-clean.
3. Verify clean installation on a second machine.
4. Add a second corpus and a genuinely new held-out protocol for stronger
   domain-generalization evidence.
5. Optionally deploy the saved-results dashboard or add a demo/API, clearly
   separate from the frozen evaluation.

## Non-negotiable continuation rules

- Work only in the original repository; do not create a parallel project.
- Preserve user commit authorship and do not add AI/Codex attribution trailers.
- Inspect `git status` before editing and never overwrite unrelated work.
- Make small, meaningful commits and push after verified milestones.
- Never commit `.env`, credentials, caches or ignored raw provider output.
- Do not edit benchmark labels to improve metrics.
- v1's reserved split is no longer untouched. Never present a rerun as a fresh
  held-out test.
- Any algorithm, prompt or benchmark change that needs a new final claim must
  use a named v2 protocol and newly declared untouched test evidence.
- Keep retrieval, answer correctness, faithfulness and abstention separate.
- Run tests and relevant focused type checks before committing.
- Keep claims tied to versioned evidence and include sample sizes/limitations.
- Explain completed technical work to the owner in very easy Hinglish.

## Ready-to-copy future AI prompt

Copy the following prompt into any capable coding agent after giving it access
to this repository:

```text
You are helping me understand and safely continue my RAG Evaluation Harness.
The repository is https://github.com/Sneha-090/RAG-eval-harness and my local
original folder is D:\rag-eval-harness. Do not create a duplicate project.

First, do not edit anything. Read these repository files in order:
1. HANDOFF.md
2. README.md
3. docs/PROJECT_GUIDE.md
4. reports/final-test-v1-2026-11-22/SUMMARY.md
5. docs/RUNBOOK.md
6. docs/STUDY_AND_INTERVIEW.md
7. data/eval/benchmark-freeze-v1.json
8. calibration/2026-11-14/agreement.json
9. PROJECT_LOG.md

Then inspect git status and the latest commits. Verify every factual claim from
versioned repository evidence; do not depend on a previous chat. Explain the
project to me in very easy Hinglish, one layer at a time, and quiz me after each
layer. I want to understand what problem it solves, the full data flow, every
major file, all metrics, why Config B was selected, judge calibration, CI, the
final failures, limitations, and how to run/debug it.

Important rules:
- Frozen benchmark v1 and its reserved-test result are historical evidence.
  Never tune v1 from the test or call a rerun fresh held-out evidence.
- Keep correctness, faithfulness, abstention and retrieval evidence separate.
- Work only in D:\rag-eval-harness.
- Preserve my Git author; never add Codex/AI attribution or co-author trailers.
- Make small meaningful commits, test before commit, and push verified work.
- Never expose or commit API keys.
- Before changing scope, tell me what exists, what you propose, why, and how it
  affects the resume story.

Start by giving me:
A. a five-sentence plain-language project story,
B. a simple architecture walkthrough,
C. the exact current progress and optional remaining work,
D. the first 30-minute study lesson.
Do not implement anything until I explicitly ask after that explanation.
```

## Resume truth source

Use the bullets in `docs/STUDY_AND_INTERVIEW.md`. If the README, resume and a
future change disagree, the frozen JSON reports and their sample sizes win.
