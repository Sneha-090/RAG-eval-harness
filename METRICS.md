\# Evaluation Metrics



All metrics are defined here BEFORE any results are viewed.

The same definitions are used for every pipeline configuration.



\## Terms

\- K: number of text chunks the retriever returns for a question (default K = 5).

\- Gold source: the corpus page that contains the answer to a question,

&#x20; as recorded in the evaluation set.

\- Unanswerable question: a question whose answer is not in the corpus.



\## 1. Retrieval metrics (is the right source found?)



\### Hit@K

\- Question answered: did at least one of the top K retrieved chunks come from

&#x20; the gold source page?

\- Score per question: 1 if yes, 0 if no.

\- Final value: average over all answerable questions (reported as a percentage).



\### MRR (Mean Reciprocal Rank)

\- Question answered: how high is the first correct chunk in the ranking?

\- Score per question: 1 / rank of the first chunk from the gold source

&#x20; (1, 0.5, 0.33, ...), or 0 if none is in the top K.

\- Final value: average over all answerable questions.

\- Purpose: Hit@K cannot show whether a reranker improves the ORDER of results.

&#x20; MRR can.



\## 2. Answer metrics (is the generated answer good?)

These are scored by an LLM judge, which is validated against human labels

(see section 4).



\### Answer correctness

\- Question answered: does the generated answer agree with the reference answer?

\- Judge output: 1 (correct), 0.5 (partly correct), 0 (incorrect).

\- Final value: average over all answerable questions.



\### Faithfulness

\- Question answered: is every claim in the answer supported by the retrieved

&#x20; chunks, with nothing invented?

\- Judge output: 1 (fully supported), 0 (contains unsupported claims).

\- Final value: average over all answerable questions.



\### Abstention (unanswerable questions only)

\- Question answered: when the answer is not in the corpus, does the system say

&#x20; that it does not know?

\- Score per question: 1 if the system declines, 0 if it gives an invented answer.

\- Reported separately and never mixed into the other averages.



\## 3. System metrics



\### Latency

\- Measured per question, from receiving the question to returning the final answer.

\- Reported as average and P95 (95% of questions finish at or below this time).

\- Recorded together with the settings of the run, because it depends on the

&#x20; hardware and the provider.



\## 4. Judge validation

\- The author labels 10-15 answers by hand (correct / incorrect, faithful / not).

\- Agreement between the judge and the author is reported as a percentage.

\- If agreement is low, the judge prompt is revised BEFORE any comparison is made.



\## 5. Rules

\- The word "accuracy" is not used without naming the exact metric above.

\- Every run records: configuration name, model, chunk size, K, date and corpus commit.

\- Metric definitions are not changed after results have been viewed. A change

&#x20; requires a new version of this file and a re-run of all configurations.

