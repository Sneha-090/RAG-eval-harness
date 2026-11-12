# Human judge calibration — 26 October 2026

This packet contains 14 real generated answers for independent human review.
The underlying development capture completed 15/15 questions with no errors;
one question is unanswerable and is excluded from correctness/faithfulness
calibration. All ten reserved test questions remain untouched.

1. Start the guided local review screen from the repository root:

       python -m streamlit run streamlit_app.py

   It shows one answer at a time, explains both decisions, saves each response
   to labels.csv, and resumes from the first unfinished answer. It makes no API
   calls and does not reveal judge scores.
2. Alternatively, read review.md and fill labels.csv manually: correctness 0,
   0.5 or 1; faithfulness 0 or 1. Add notes where helpful. Scores are deliberately
   blank and must be filled by the human author.
3. Do not look at judge verdicts before writing independent labels. No model
   verdicts or scores are included here.
4. Compare with the matching local judge capture using the command below.

    python -m src.evaluation.human_review compare --packet calibration/2026-10-26/packet.json --labels calibration/2026-10-26/labels.csv --judge runs/judge-calibration-20261026 --output runs/agreement-calibration-20261026.json

packet.json pins the selected questions, answers and context. capture-manifest.json
records the original capture settings and source hashes. The packet cannot be
silently substituted with answers from another run. Blank labels will be rejected
by the agreement command. No human agreement result exists yet.

This is a small developmental calibration sample, not a frozen benchmark, final
quality comparison or assessment of the system on unseen domains.


Live verification: all 15 captured answers were processed successfully by the
configured judge. The verdicts remain in the ignored local runs directory so
they do not influence this blind review. A resume check reused all saved
verdicts without rewriting them. The four original transient generation
connection failures and one judge request failure were retried successfully
without repeating successful calls. No final answer-quality or human-agreement
claim is made.
