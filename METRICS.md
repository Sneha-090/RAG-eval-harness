# Evaluation metrics — version 2

Effective 25 October 2026, before scoring the expanded draft benchmark.
Version 1 remains available in Git history. Existing Hit@K, MRR and answer-score
scales are retained. Version 2 explicitly defines multi-source behavior and adds
source recall and exact evidence coverage. All configurations must use this
same contract and dataset version. No comparison result exists yet.

## Retrieval metrics

K is the number of returned chunks (default 5). Only the first K ranked chunks
are scored. A gold source is a corpus page listed in gold_sources. Evidence is
an exact quotation from a normalized gold page. All listed evidence items are
required, not alternatives. Chunk IDs are not part of the gold labels.

For each answerable question:

- **Hit@K:** 1 if any top-K chunk comes from any gold source, otherwise 0.
  This preserves the original page-level metric; it does not mean all parts
  of a multi-source question are supported.
- **MRR@K:** reciprocal of the rank of the first chunk from any gold source;
  0 when none appears. Average question scores to obtain mean reciprocal rank.
- **Source recall@K:** number of distinct gold pages retrieved divided by the
  number of required gold pages. Duplicate chunks from one page do not inflate it.
- **Evidence coverage@K:** for each evidence quote, the fraction of its
  non-whitespace characters covered by retrieved chunk intervals on that same
  source page. Take the union of intervals so overlaps cannot double-count.
  Then average across required quotes with equal weight. Coverage may combine
  multiple chunks, including a quote split at a chunk boundary. If identical
  text occurs repeatedly in a page, use its best-covered occurrence; the text
  itself is equivalent evidence. No case folding or Markdown stripping occurs.
- **Complete evidence@K:** 1 only when every required quote has full coverage;
  otherwise 0. Long quotes and exact matching can make this conservative.

All metrics are averaged per question (macro average), overall and by category.
Saved fractions are in [0,1]; multiply by 100 only for percentage presentation.
Unanswerable questions are excluded from every retrieval quality average.
An empty but successful retrieval scores 0 on every answerable retrieval metric.
Missing/failed retrieval has no score: report its count and label averages as
conditional on available retrievals. An incomplete run is not a valid baseline.
A generator failure does not invalidate a separately successful retrieval.
Unknown sources, fabricated chunk text and duplicate chunk IDs are data errors,
not silently scored as retrieval failures.

Exact evidence coverage measures lexical availability, not whether a passage is
semantically sufficient or the only valid evidence. Human label review remains
required. Never tune labels or metric definitions to improve observed results.

## Answer metrics (not implemented yet)

- **Correctness:** judge compares answer with the reference: 1 correct,
  0.5 partly correct, 0 incorrect; average over answerable questions.
- **Faithfulness:** 1 if every claim is supported by retrieved context,
  0 if any claim is unsupported; average over answerable questions.
- **Abstention:** only for unanswerable questions: 1 for declining to answer,
  0 for an invented answer. Report separately, including numerator/denominator.

Validate the judge against 10–15 human-labelled answers before interpreting
comparison scores. Human correctness labels must include the same 0/0.5/1 scale;
faithfulness uses 0/1. Report exact agreement separately for each metric.
No invented judge score or automatic citation-based proxy may fill these fields.

## Timing and provenance

End-to-end answer latency runs from receiving a question to its final answer,
excluding experiment scheduling waits, judge calls and report writing. Failed
and resumed multi-attempt questions must be identified separately. Report mean
and nearest-rank P95: sorted sample at ceil(0.95*N), using one-based indexing.

The current retrieval-only report records **retrieval-stage** mean and P95 over
available retrievals, including answerable and unanswerable questions. Model
preloading is outside that timer. These numbers are not end-to-end latency and
do not include cold-start model loading. Retain the hardware/platform context.

Every run records dataset/corpus hashes, corpus source commit, code version,
model settings, chunk size/overlap, K, prompt when applicable, and date. The
pinned upstream corpus commit is recorded in data/CORPUS.md, whose content is
hashed in the run manifest. Index embedding revision provenance is still a
known limitation and must be addressed before controlled comparisons.

## Change policy

Version metric changes before viewing new scores. A change requires a new
contract version and rerunning all compared configurations. Do not call a number
"accuracy" without naming its metric. Preserve poor results and investigate them.
