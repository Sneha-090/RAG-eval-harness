# Django 5.2 LTS benchmark corpus

- Corpus key: `django-5.2`
- Purpose: second-domain benchmark for testing whether the same RAG evaluation
  harness generalizes beyond FastAPI.
- Upstream: https://github.com/django/django
- Release: Django 5.2.19 (5.2 LTS series)
- Pinned Git commit: `a3510e06a7598039d0992dd00c736e25dbdc9aab`
- Upstream documentation root: `docs/`
- Local raw folder: `data/corpora/django-5.2/raw/`
- License: BSD 3-Clause (see the upstream repository's `LICENSE` file).
- Retrieval unit: normalized RST source text. No web page, API response, or
  generated summary is used as benchmark evidence.

## Selected files

The 12 files deliberately cover related concepts across request handling,
forms, models, authentication, security, migrations and testing. Similar pages
make this a useful retrieval benchmark instead of a collection of unrelated
facts.

| Local filename | Upstream path |
| --- | --- |
| `topics__http__urls.txt` | `docs/topics/http/urls.txt` |
| `topics__http__views.txt` | `docs/topics/http/views.txt` |
| `ref__request-response.txt` | `docs/ref/request-response.txt` |
| `topics__http__middleware.txt` | `docs/topics/http/middleware.txt` |
| `topics__forms__index.txt` | `docs/topics/forms/index.txt` |
| `ref__forms__validation.txt` | `docs/ref/forms/validation.txt` |
| `topics__db__models.txt` | `docs/topics/db/models.txt` |
| `topics__db__queries.txt` | `docs/topics/db/queries.txt` |
| `topics__migrations.txt` | `docs/topics/migrations.txt` |
| `topics__auth__default.txt` | `docs/topics/auth/default.txt` |
| `topics__security.txt` | `docs/topics/security.txt` |
| `topics__testing__overview.txt` | `docs/topics/testing/overview.txt` |

## Freeze rules

1. FastAPI v1 files, questions and final reports remain unchanged.
2. Django questions use a separate dataset and IDs beginning with `d`.
3. A fresh dev/test split must be frozen before the Django reserved test runs.
4. Reserved-test questions must not be used to choose chunking or retrieval.
5. Every answerable reference needs an exact quote from these local files;
   unanswerable items must have no gold source or evidence.
