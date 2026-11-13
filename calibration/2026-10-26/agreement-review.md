# Blind human–judge agreement review

Measured on 13 November 2026 from the version-pinned 14-answer development
packet. The human labels were completed without access to the saved Gemini
verdicts. All ten reserved test questions remained untouched.

## Initial blind result

| Metric | Exact agreement |
|---|---:|
| Correctness | 14/14 (100.0%) |
| Faithfulness | 11/14 (78.6%) |

Correctness used the frozen 0/0.5/1 scale; faithfulness used 0/1. The packet
contains answerable questions only, so this comparison does not calibrate the
unanswerable-question abstention score.

## Disagreement inspection

This inspection happened only after the blind agreement result was saved. It
does not change the 78.6% faithfulness agreement number.

| ID | Human | Judge | Evidence inspection |
|---|---:|---:|---|
| q001 | 1 | 0 | The answer added `my_cookie: str = Cookie(...)`; that code example is absent from the retrieved context. The judge's unsupported-claim label is better supported. |
| q003 | 0 | 1 | `handling-errors.md::2` and `::3` explicitly support raising the exception, terminating the request and sending the HTTP error. The judge's supported label is better supported. |
| q012 | 0 | 1 | `response-model.md::5` and `::6` support priority plus documentation, validation and output conversion/filtering. The judge's supported label is better supported. |

The post-hoc inspection suggests these three differences came from inconsistent
human application of the strict “every factual claim” rubric rather than clear
judge failures. That is an interpretation, not a replacement agreement score.

## Decision and limitations

The judge is useful for continued development experiments: it matched all 14
correctness labels and its three faithfulness disagreements have direct textual
support. It remains provisional for final claims because this is one small
sample, one human reviewer, one generator run and no human-labelled
unanswerable questions. A fresh blind calibration sample should be measured
before treating automated faithfulness or abstention scores as final.
