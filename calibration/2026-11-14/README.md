# Fresh mixed blind calibration

This packet contains 10 previously unused development questions selected before
any judge call: eight answerable questions across four categories and two
unanswerable questions. Configuration B generated every saved answer. The
packet was exported with no judge verdicts and blank `labels.csv` values. The
author then completed and committed all labels before the hidden judge run. The
measured outcome is preserved in `agreement.json` and `RESULT.md`.

## Review procedure used

Open Command Prompt or PowerShell and run:

    cd /d D:\rag-eval-harness
    .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py

If PowerShell rejects `cd /d`, use this first line instead:

    Set-Location D:\rag-eval-harness

For answerable questions, choose correctness and whether every claim is
supported by the displayed retrieved context. For unanswerable questions,
choose whether the answer correctly refused or invented missing information.
Optional notes are useful only when something is unclear.

The screen saved after every item and resumed at the first unfinished item.
All ten labels were frozen in commit `ac4cf7a` before the hidden judge was run.

## Integrity

- Packet version: 2 (mixed answerable/unanswerable review)
- Reserved test questions used: none
- Judge verdicts created before review: no
- Human labels at export: blank
- Selection: deterministic category round-robin, independent of judge scores
- Human labels frozen before judge: yes
- Exact agreement: 100% for correctness (8), faithfulness (8), and abstention (2)
