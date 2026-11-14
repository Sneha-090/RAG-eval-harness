# Fresh mixed blind calibration

This packet contains 10 previously unused development questions selected before
any judge call: eight answerable questions across four categories and two
unanswerable questions. Configuration B generated every saved answer. The
packet contains no judge verdicts, and `labels.csv` starts blank.

## Complete the guided review

Open Command Prompt or PowerShell and run:

    cd /d D:\rag-eval-harness
    .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py

If PowerShell rejects `cd /d`, use this first line instead:

    Set-Location D:\rag-eval-harness

For answerable questions, choose correctness and whether every claim is
supported by the displayed retrieved context. For unanswerable questions,
choose whether the answer correctly refused or invented missing information.
Optional notes are useful only when something is unclear.

The screen saves after every item and resumes at the first unfinished item.
When all 10 are complete, stop. Do not generate or inspect judge verdicts yet;
tell the project agent that the blind review is finished. The frozen human
labels must exist before the judge run is created.

## Integrity

- Packet version: 2 (mixed answerable/unanswerable review)
- Reserved test questions used: none
- Judge verdicts created before review: no
- Human labels at export: blank
- Selection: deterministic category round-robin, independent of judge scores
