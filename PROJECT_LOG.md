# RAG Eval Harness: Project Log

**Status as of 10 October 2026:** Milestones 1 and 2 complete in code. Milestone 3 (evaluation set) not started.

This file records what was done, why it was done, how it was done, and what was learned. It is updated after every milestone. It must never contain API keys.

---

## 1. Project summary

**Goal:** Build a document-based RAG system and an automated evaluation harness that measures its quality, compares four pipeline configurations, and detects quality regressions in CI.

**Benchmark corpus:** 12 pages of the FastAPI tutorial documentation, frozen at one Git commit. FastAPI is only the first test corpus. The RAG core contains no FastAPI-specific logic.

**Stack:** Python 3.13, sentence-transformers (local embeddings), ChromaDB, Groq (answer generator), Google Gemini (judge), GitHub Actions (planned).

**Roadmap (frozen in `ROADMAP.md`):**

| Milestone | Content | Status |
|---|---|---|
| 1 | Setup and metrics contract | Complete |
| 2 | Baseline RAG (Configuration A) | Complete |
| 3 | Evaluation set and harness, judge validation | Next |
| 4 | Four-configuration comparison | Not started |
| 5 | Regression gate and CI | Not started |
| Extras | Generic ingestion, demo UI | Only after Milestone 5 |

---

## 2. Key decisions and reasons

| Decision | Reason |
|---|---|
| FastAPI docs as benchmark corpus, not as the product domain | Public, structured, and the answers can be verified by the author. A second fintech project would look narrow next to RecoverAI. |
| Pin the corpus to a Git commit | Results stay reproducible even if the documentation changes. |
| Keep the corpus prose-only (code placeholders not expanded) | Simpler for the first version. Evaluation questions are about concepts. Documented in `data/CORPUS.md`. |
| Define metrics before any result is seen | Prevents adjusting the metrics to make the numbers look good. |
| Separate retrieval metrics from answer metrics | When an answer is wrong, we must know whether search or generation failed. |
| No LangChain or LlamaIndex | Each step is written by hand, so each step can be explained in an interview. |
| Judge from a different model family than the generator | Reduces the risk that a model favours its own style. |
| CI will run only fast, deterministic checks | LLM calls are slow, flaky and rate-limited. |
| Small, regular commits and milestone tags | The commit history shows steady progress over time. |

---

## 3. Milestone 1: Setup and metrics contract

**What was done**
1. Created the repository `rag-eval-harness`, a virtual environment (`.venv`), `.gitignore`, and pushed to GitHub.
2. Cloned the FastAPI source repository outside the project folder (`D:\fastapi-source`) and recorded the commit hash `3e33a03bdaa3a89f27d5e0c390c4ba9032f14b5e`.
3. Selected 12 tutorial pages, including similar pages on purpose (path, query, header and cookie parameters, and two different `first-steps` pages), because similar pages make retrieval harder and make differences between methods visible.
4. Copied the pages to `data/raw/`. Pages from subfolders were prefixed with the folder name (`dependencies__index.md`, `security__first-steps.md`) so that equal file names do not overwrite each other.
5. Wrote `scripts/inspect_corpus.py` to count files, bytes, words, headings, code fences and placeholders.
6. Wrote `data/CORPUS.md` (source, pinned commit, known limitation) and `METRICS.md` (exact metric definitions).

**Selected pages:** `first-steps`, `path-params`, `query-params`, `body`, `query-params-str-validations`, `path-params-numeric-validations`, `header-params`, `cookie-params`, `response-model`, `handling-errors`, `dependencies/index`, `security/first-steps`.

**Results**
- 12 files, 107,828 bytes, 15,069 words.
- About 95 `{* ... *}` placeholders. They point to code files that are not in the corpus, so the corpus contains explanations but not code examples.

**Metrics defined in `METRICS.md`:** Hit@K, MRR, answer correctness, faithfulness, abstention (for unanswerable questions), and latency (average and P95). K = 5.

---

## 4. Milestone 2: Baseline RAG (Configuration A)

```
Documents -> Loader -> Chunker -> Embeddings -> Chroma -> Retrieve top 5 -> Prompt -> LLM -> Answer
```

### Step 1: Setup
Folders `src/ingestion`, `src/chunking`, `src/retrieval`, `src/generation`, each with an empty `__init__.py` so that Python treats them as packages. Installed `sentence-transformers` and `chromadb`. `requirements.txt` records the exact versions (`chromadb 1.5.9`, `sentence-transformers 6.1.0`).

### Step 2: Loader (`src/ingestion/loader.py`)
- Reads every `.md` and `.txt` file in a folder.
- Normalization (in memory only, the raw files are never changed): unify line endings, remove `{* ... *}` placeholder lines, remove trailing spaces and runs of blank lines.
- Result: 12 documents, no placeholders left.

### Step 3: Chunker (`src/chunking/fixed.py`)
- Fixed-size chunks with overlap. The cut moves back to the nearest space or line break so that words are not split.
- The overlap keeps an idea that falls on a boundary from being lost completely.
- Known weakness: it does not know where sentences or topics end, so chunks can end in the middle of a sentence. Semantic chunking (Configuration B) is meant to improve this.

### Step 4: Embeddings (`src/retrieval/embeddings.py`)
- Model: `sentence-transformers/all-MiniLM-L6-v2`, local and free. Each chunk becomes a vector of 384 numbers.
- Vectors are normalized, so cosine similarity equals the dot product.
- The model reads at most 256 tokens. Text beyond that is silently ignored.

### Step 5: Chroma index (`src/retrieval/index.py`)
- Persistent database in `chroma_db/` (ignored by Git). The collection `fastapi_baseline` uses cosine similarity.
- Each chunk is stored with its ID (`body.md::3`), vector, text and metadata (`doc_id`, `index`).
- The collection is deleted and rebuilt on every run, so the index is always clean.

### Step 6: Retrieval (`src/retrieval/dense.py`)
- Converts the question to a vector and asks Chroma for the 5 closest chunks. Chroma returns a distance, and similarity = 1 - distance.
- Checked by hand on 7 questions before any language model was involved.

### Step 7: LLM client and generator
- `src/generation/llm.py`: provider-replaceable client using plain HTTP requests, with retry on rate limits (HTTP 429) and timing of each call. The models are set in one place.
  - Generator: Groq, `openai/gpt-oss-120b`.
  - Judge: Gemini, `gemini-3.5-flash`.
- `src/generation/answer.py`: **prompt v1 (frozen).** The model must use only the supplied context, must reply with the fixed sentence `I cannot find this in the provided documentation.` when the answer is missing, must not guess, and must answer in at most four sentences and name source IDs.
- `src/generation/check_keys.py` and `latency_probe.py`: helper scripts that list the available models and measure latency. API keys are stored in `.env`, which Git ignores.

---

## 5. Key numbers

| Item | Value |
|---|---|
| Corpus | 12 pages, 107,828 bytes, 15,069 words |
| Chunk settings (final) | 550 characters, 80 overlap, **215 chunks** |
| Chunk settings (first attempt) | 800 characters, 100 overlap, 144 chunks |
| Longest chunk, first attempt | 344 tokens, **19 of 144 above the 256-token limit** |
| Longest chunk, final | 243 tokens, 0 of 215 above the limit |
| Embedding size | 384 numbers per chunk |
| Retrieval K | 5 |
| Similarity for "How do I declare a request body?" | 0.663 with the right chunk at 800 characters, 0.778 at 550 characters, 0.287 to 0.307 for unrelated chunks |

**Model latency probe (two calls each, tiny prompt)**

| Model | Call 1 | Call 2 | Decision |
|---|---|---|---|
| `gemini-3.8-flash` | 30.2 s | 28.6 s (88 s in the first test) | Rejected, too slow |
| `gemini-3.5-flash` | 2.1 s | 4.2 s | **Chosen as judge** |
| `gemini-3.1-flash-lite` | 3.1 s | 18.5 s | Inconsistent |
| Groq `gpt-oss-20b` | 0.9 s | 0.8 s | Kept as fallback |

**Groq free tier (from response headers):** 1000 requests and 8000 tokens as limits. The reset times suggest 1000 requests per day and 8000 tokens per minute (inferred, to be confirmed in the Groq console). Roughly 4 to 5 RAG questions per minute.

**Answer timing:** retrieval about 0.02 to 0.03 s when warm (6.83 s on the first call because the embedding model was loading); generation about 0.8 to 1.3 s.

---

## 6. Findings

1. **Chunk size had a hidden technical limit.** At 800 characters, 13% of chunks exceeded the embedding model's 256-token window, so their ends were invisible to search. Technical text uses more tokens per character than prose. Reducing to 550 fixed it and also made the match with the right chunk stronger. The change was made before any evaluation result existed.
2. **Similarity scores cannot detect unanswerable questions.** The Docker question (not in the corpus) scored 0.706, higher than three answerable questions. A threshold such as "below 0.6, refuse" would not work. The refusal has to come from the model, and the abstention metric measures it. (I had predicted the opposite, and the data corrected me.)
3. **The model refused correctly on the Docker question.** Related content (deployment) existed, but not Docker.
4. **The model added code that is not in the corpus.** Three strings from its answers (`my_cookie`, `item_not_found`, `token: str`) were searched with `findstr` and appear nowhere in the raw documents. This breaks the "use only the context" rule and is exactly what the faithfulness metric must catch. Correctness may be high while faithfulness is low.
5. **Page-level Hit@K is too generous.** Any chunk of the right page counts as a hit, even if it is not the chunk with the answer. The evaluation set will store exact evidence sentences, and a stricter chunk-level metric will be added in a new version of `METRICS.md`.
6. **Citations are unreliable as a signal.** One answer used different bracket characters, and some answers cited chunks that did not contain every claim. The evaluation does not depend on parsing citations.
7. **A model that appears in a list may not be usable.** `gemini-2.5-flash` was listed but returned 404 ("no longer available to new users"). Therefore every run records the exact model name.
8. **Weak spots seen in retrieval (hypotheses for Milestone 4, not conclusions):** `path-params.md` did not appear for the path-versus-query question, and the introduction chunk of `header-params.md` was missing for the header question.

---

## 7. Problems met and how they were solved

| Problem | Cause | Solution and lesson |
|---|---|---|
| `Test-Path` not recognised | Using Command Prompt, not PowerShell | Use `if exist` in `cmd` |
| Could not reach `D:\fastapi-source` | `cd` does not change drives in `cmd` | `cd /d D:\...` |
| Files `dict` and `None` appeared | Python code pasted into the terminal | Code goes into files, commands go into the terminal. Deleted the files. |
| `numpy` build error on Python 3.13 | No ready-made package for the old version pip tried | `pip install --only-binary=:all: ...` |
| `SyntaxError` in `fixed.py` | The `#` before the comments was lost during editing | `#` starts a comment in Python |
| `.gitignore` entries merged into one line | The last line had no line break | `echo.>> .gitignore` first, then add the entry |
| Git pager showed `(END)` | `git log` opened a viewer | Press `q`, or use `git --no-pager log` |
| Judge model still the slow one | The edit was not saved | Verify with `findstr JUDGE src\generation\llm.py` |
| `scratch` folder missing | `mkdir` was skipped | Create folders before writing files into them |

---

## 8. Repository structure (expected)

```
rag-eval-harness/
  ROADMAP.md
  METRICS.md
  requirements.txt
  .gitignore            (.venv, __pycache__, .env, chroma_db, scratch and working files)
  data/
    CORPUS.md
    raw/                (12 frozen documentation pages)
  scripts/
    inspect_corpus.py
  src/
    ingestion/loader.py
    chunking/fixed.py
    retrieval/embeddings.py, index.py, dense.py
    generation/llm.py, answer.py, check_keys.py, latency_probe.py
```

**To verify with Git:** `git ls-files` should list all of these (and not `.env`, `chroma_db`, `scratch`). `git tag` should show `v0.1-milestone-1` and `v0.2-milestone-2`.

---

## 9. Open items

- Google AI Studio free limits for `gemini-3.5-flash` (requests per minute and per day) are not yet known. The harness will pace its calls and save every result so that no call is repeated.
- Confirm Groq limits in the Groq console.
- Milestone 3: write the 50-question evaluation set (15 direct, 10 similar-page, 8 multi-part, 12 paraphrase, 5 unanswerable), with `reference_answer`, `gold_sources` and exact `evidence` sentences. A validator script checks the format and that every evidence sentence exists in the gold pages.

---

## 10. Interview preparation

**Q: What does this project do?**
It measures the quality of a RAG system like software testing. A fixed corpus and a hand-written question set are run through the pipeline, retrieval and answer quality are scored separately, four pipeline designs are compared, and a regression gate is designed to fail the build when quality drops.

**Q: Why did you choose 550-character chunks?**
My first setting was 800 characters, but 19 of 144 chunks were longer than the embedding model's 256-token window, so the ends of those chunks were ignored. I measured the token counts, reduced the size to 550, and then no chunk exceeded the limit. I made this change before I had any evaluation results.

**Q: Why do you measure retrieval and generation separately?**
When an answer is wrong, I need to know whether the search failed or the model failed. Hit@K and MRR measure search. Correctness and faithfulness measure the answer.

**Q: What is faithfulness, and did you find a failure?**
Faithfulness means that every claim in the answer is supported by the retrieved text. In my baseline, the model added code examples that exist nowhere in my corpus, which I proved by searching the raw files.

**Q: How do you handle questions that the documents cannot answer?**
Similarity scores cannot detect them, because an unrelated question scored 0.706. I use a prompt with a fixed refusal sentence, and an abstention metric on a separate group of unanswerable questions.

**Q: Why use a different model as the judge?**
A model may favour its own style. I also validate the judge against my own hand labels before using its scores.

**Q: What are the limits of your project?**
The corpus is small (12 pages) and prose-only, the questions are written by one person, and a free-tier LLM judge has its own errors. The results describe this benchmark, not RAG in general.

---

## 11. What may be claimed on a resume today

- Building a RAG system with an automated evaluation harness to benchmark 4 pipeline configurations on retrieval quality, answer quality and latency.
- Built a baseline pipeline (local sentence embeddings, ChromaDB, LLM answering with a context-only prompt) over a version-pinned corpus of 12 FastAPI documentation pages (about 15,000 words, 215 chunks).
- Defined retrieval and answer-quality metrics before experimentation, and diagnosed an embedding-window limit (19 of 144 chunks exceeded 256 tokens) by measuring token counts.

**Not yet allowed:** any comparison result, judge-agreement number, or CI gate. Add them only after they exist.

---

## 12. How to update this log

After every milestone, add a section with: what was done, why, how (the files and the settings), the real numbers, what went wrong, and what was learned. Record every setting that affects a result (model names, chunk size, K, prompt version, date). Never paste API keys, and never replace real results with example numbers.