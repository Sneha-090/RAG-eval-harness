"""Build the evidence-backed Django benchmark draft from pinned local sources."""
import argparse
import json
import re
from pathlib import Path

from src.corpora import get_corpus
from src.ingestion.loader import load_documents


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "eval" / "django-5.2" / "questions.draft.jsonl"


def item(identifier, category, question, answer, *evidence):
    return {
        "id": identifier,
        "category": category,
        "split": "test" if identifier in {"d005", "d010", "d015", "d020", "d025", "d030", "d035", "d040", "d045", "d050"} else "dev",
        "question": question,
        "answerable": True,
        "reference_answer": answer,
        "evidence_needles": evidence,
    }


DRAFT = [
    item("d001", "direct", "What normally tells Django which root URLconf module to use?",
         "Django normally uses the ROOT_URLCONF setting, unless the incoming HttpRequest supplies a urlconf override.",
         ("topics__http__urls.txt", "Django determines the root URLconf module to use.")),
    item("d002", "direct", "What must Django find inside a loaded URLconf module?",
         "It looks for urlpatterns, a sequence of django.urls.path and/or django.urls.re_path instances.",
         ("topics__http__urls.txt", "Django loads that Python module and looks for the variable")),
    item("d003", "similar_page", "Which built-in path converter accepts zero or a positive integer?",
         "The int path converter.",
         ("topics__http__urls.txt", "Matches zero or any positive integer.")),
    item("d004", "paraphrase", "What should I create when Django's built-in URL path converters cannot express a complex match?",
         "Define and register a custom path converter.",
         ("topics__http__urls.txt", "For more complex matching requirements, you can define your own path converters.")),
    item("d005", "similar_page", "What does including another URLconf do to its URLs?",
         "It roots that set of URLs below the including URL pattern.",
         ("topics__http__urls.txt", "can \"include\" other URLconf modules")),
    item("d006", "direct", "What does a Django view function receive and return?",
         "It receives a web request and returns a web response.",
         ("topics__http__views.txt", "A view function, or *view* for short")),
    item("d007", "multi_part", "How can a view return an uncommon HTTP status, and what shortcut handles a standard 404 page?",
         "Pass the status code to HttpResponse for an uncommon status; raise Http404 for Django's standard 404 handling.",
         ("topics__http__views.txt", "pass the HTTP status code into the constructor"),
         ("topics__http__views.txt", "Django provides an ``Http404`` exception")),
    item("d008", "paraphrase", "If a view raises Http404, who turns it into the application's 404 response?",
         "Django catches Http404 and returns the standard application error page with HTTP status 404.",
         ("topics__http__views.txt", "Django will catch it and return the")),
    item("d009", "direct", "Where should a view read raw or non-form POST data from?",
         "Read it from HttpRequest.body rather than HttpRequest.POST.",
         ("ref__request-response.txt", "If you need to access raw or")),
    item("d010", "similar_page", "Why are request.GET and request.POST QueryDict objects instead of ordinary dictionaries?",
         "QueryDict supports multiple values for one key, which is needed for inputs such as a multiple-select field.",
         ("ref__request-response.txt", "customized to deal with multiple values for the same")),
    item("d011", "direct", "How do I obtain a mutable version of request.GET or request.POST?",
         "Call QueryDict.copy().",
         ("ref__request-response.txt", "To get a mutable version you")),
    item("d012", "similar_page", "For a repeated QueryDict key, what do __getitem__ and getlist return?",
         "__getitem__ returns the last value, while getlist returns the values as a list.",
         ("ref__request-response.txt", "Returns the last value for the given key"),
         ("ref__request-response.txt", "Returns a list of the data with the requested key.")),
    item("d013", "paraphrase", "How can JsonResponse accept a list instead of a dictionary?",
         "Pass safe=False; otherwise a non-dict value raises TypeError.",
         ("ref__request-response.txt", "Without passing ``safe=False``")),
    item("d014", "multi_part", "When is StreamingHttpResponse useful under WSGI, and what extra capability does ASGI provide?",
         "Under WSGI it can stream content that is slow or memory-heavy to generate. Under ASGI it can wait for I/O without blocking other requests, enabling long-lived streaming patterns.",
         ("ref__request-response.txt", "An example usage of :class:`StreamingHttpResponse` under WSGI"),
         ("ref__request-response.txt", "When serving under ASGI, however")),
    item("d015", "similar_page", "What does HttpResponse.headers expose, and is lookup case-sensitive?",
         "It exposes a dict-like interface to response headers except Set-Cookie, and lookup is case-insensitive.",
         ("ref__request-response.txt", "A case insensitive, dict-like object that provides an interface")),
    item("d016", "direct", "Why must AuthenticationMiddleware come after SessionMiddleware?",
         "AuthenticationMiddleware stores the authenticated user in the session, so it depends on SessionMiddleware.",
         ("topics__http__middleware.txt", "AuthenticationMiddleware` stores the")),
    item("d017", "multi_part", "In Django's middleware onion, in what order do requests and responses travel, and what happens after a short-circuit response?",
         "Requests move top-down through MIDDLEWARE and responses return through those layers in reverse. If a layer returns without calling get_response, inner layers and the view are skipped.",
         ("topics__http__middleware.txt", "During the request phase, before calling the view"),
         ("topics__http__middleware.txt", "If one of the layers decides to short-circuit")),
    item("d018", "direct", "What can process_view() return, and how does each return type affect view execution?",
         "It can return None to continue to later middleware and the view, or HttpResponse to skip the view and begin response processing.",
         ("topics__http__middleware.txt", "It should return either ``None`` or an")),
    item("d019", "paraphrase", "What cost can occur when middleware cannot handle both synchronous and asynchronous requests?",
         "Django adapts the request to the middleware's requirements, but the conversion has a performance penalty.",
         ("topics__http__middleware.txt", "Django will adapt requests to fit the middleware's requirements")),
    item("d020", "multi_part", "What two things happen when Form.is_valid() succeeds?",
         "It returns True and places the validated data in the form's cleaned_data attribute.",
         ("topics__forms__index.txt", "A :class:`Form` instance has an :meth:`~Form.is_valid()` method")),
    item("d021", "similar_page", "How do bound and unbound Django forms differ?",
         "An unbound form has no submitted data; a bound form has submitted data and can be validated and display inline errors.",
         ("topics__forms__index.txt", "An unbound form has no data associated with it."),
         ("topics__forms__index.txt", "A bound form has submitted data")),
    item("d022", "direct", "Why can ModelForm reduce code when editing a model?",
         "It builds a form and appropriate fields and attributes from a Model class.",
         ("topics__forms__index.txt", "can save you a great")),
    item("d023", "paraphrase", "What template tag is required for a POST form when Django CSRF protection is enabled?",
         "Use the csrf_token template tag.",
         ("topics__forms__index.txt", "CSRF protection enabled you must use")),
    item("d024", "multi_part", "Which validation steps does Field.clean() run, and where does successful output go?",
         "It runs to_python(), validate(), and run_validators() in order; the cleaned result is inserted into the form's cleaned_data dictionary.",
         ("ref__forms__validation.txt", "The ``clean()`` method on a ``Field`` subclass")),
    item("d025", "similar_page", "When should validation use clean_<fieldname>() instead of Form.clean()?",
         "Use clean_<fieldname>() for one particular field and Form.clean() for validation that needs multiple fields.",
         ("ref__forms__validation.txt", "The ``clean_<fieldname>()`` method is called"),
         ("ref__forms__validation.txt", "can perform validation that requires")),
    item("d026", "direct", "Where are errors raised by Form.clean() stored when they are not tied to a field?",
         "They are stored under the special __all__ field and are available through non_field_errors().",
         ("ref__forms__validation.txt", "They go into a special")),
    item("d027", "paraphrase", "What is the order of field-level and form-level cleaning?",
         "For every field Django runs Field.clean() and then clean_<fieldname>(); after all fields, it runs Form.clean().",
         ("ref__forms__validation.txt", "the ``Field.clean()`` method (or its override) is run")),
    item("d028", "similar_page", "What happens if a Django model declares no field with primary_key=True?",
         "Django automatically adds a field to hold the primary key.",
         ("topics__db__models.txt", "Django will automatically add a field to hold")),
    item("d029", "direct", "What happens if I change an existing object's primary-key value and save it?",
         "Django creates a new object alongside the old one because the primary-key field is read-only.",
         ("topics__db__models.txt", "The primary key field is read-only.")),
    item("d030", "multi_part", "Which fields define many-to-one and many-to-many relationships, and what required positional argument do both take?",
         "Use ForeignKey for many-to-one and ManyToManyField for many-to-many; both require the related model class as a positional argument.",
         ("topics__db__models.txt", "To define a many-to-one relationship"),
         ("topics__db__models.txt", "To define a many-to-many relationship")),
    item("d031", "paraphrase", "How can a many-to-many relationship store extra facts such as the date a person joined a group?",
         "Use an intermediate model with extra fields and point ManyToManyField.through to it.",
         ("topics__db__models.txt", "You can then put extra fields on the")),
    item("d032", "direct", "Does an abstract base model create its own database table or support direct instantiation?",
         "No. It creates no table or manager and cannot be instantiated or saved directly.",
         ("topics__db__models.txt", "since it is an abstract base class.")),
    item("d033", "similar_page", "When does constructing and filtering a QuerySet actually hit the database?",
         "Not when it is created or filters are stacked; the query runs when the QuerySet is evaluated.",
         ("topics__db__queries.txt", "``QuerySet`` objects are lazy")),
    item("d034", "multi_part", "What does QuerySet.get() raise when zero rows match and when multiple rows match?",
         "It raises the model's DoesNotExist exception for zero matches and MultipleObjectsReturned for multiple matches.",
         ("topics__db__queries.txt", "If there are no results that match the query"),
         ("topics__db__queries.txt", "if more than one item matches")),
    item("d035", "paraphrase", "How can a Django query compare one model field with another field on the same row?",
         "Use an F() expression to reference a model field inside the query.",
         ("topics__db__queries.txt", "Instances of ``F()`` act as a reference")),
    item("d036", "direct", "What are makemigrations and migrate each responsible for?",
         "makemigrations packages model changes into migration files; migrate applies and unapplies migrations to the database.",
         ("topics__migrations.txt", "You should think of migrations as a version control system")),
    item("d037", "similar_page", "Why should RunPython migrations use historical models instead of importing current models directly?",
         "Migrations run against historical model versions; direct imports may work initially but fail when old migrations are rerun later.",
         ("topics__migrations.txt", "When you run migrations, Django is working from historical versions"),
         ("topics__migrations.txt", "If you import models directly rather than using the historical models")),
    item("d038", "paraphrase", "How do I make a RunPython data migration reversible?",
         "Pass a second callable containing the backward logic; without it, migrating backward raises an exception.",
         ("topics__migrations.txt", "You can pass a second callable")),
    item("d039", "multi_part", "What is migration squashing, and which command performs it?",
         "Squashing reduces many migrations to one or a few equivalent migrations; use squashmigrations with the app label and target migration name.",
         ("topics__migrations.txt", "Squashing is the act of reducing"),
         ("topics__migrations.txt", "The command that backs all this is")),
    item("d040", "direct", "What does django.contrib.auth.login() save in the session?",
         "It saves the user's ID using Django's session framework.",
         ("topics__auth__default.txt", "saves the user's ID in the session")),
    item("d041", "paraphrase", "What happens to current session data when django.contrib.auth.logout() is called?",
         "The current request's session data is completely cleared to prevent reuse by another browser user.",
         ("topics__auth__default.txt", "the session data for")),
    item("d042", "direct", "What does login_required do when the user is not logged in, and where is the destination stored?",
         "It redirects to settings.LOGIN_URL and stores the current absolute path in the next query-string parameter.",
         ("topics__auth__default.txt", "If the user isn't logged in, redirect to"),
         ("topics__auth__default.txt", "stored in a query string parameter called")),
    item("d043", "paraphrase", "How do Django's CSRF and SQL-injection protections work differently?",
         "CSRF protection checks a secret in each POST request; QuerySet SQL-injection protection separates parameterized query code from user-provided parameters.",
         ("topics__security.txt", "CSRF protection works"),
         ("topics__security.txt", "Django's querysets are protected from SQL injection")),
    item("d044", "paraphrase", "Which built-in Django middleware helps stop a site from being embedded in a frame?",
         "XFrameOptionsMiddleware provides clickjacking protection through the X-Frame-Options header mechanism.",
         ("topics__security.txt", "X-Frame-Options middleware")),
    item("d045", "direct", "Do Django model tests use the production database?",
         "No. Django creates separate blank test databases and destroys them after the tests finish.",
         ("topics__testing__overview.txt", "will not use your \"real\"")),
]


UNANSWERABLE = [
    ("d046", "dev", "How should Django's Redis cache backend and cache timeout be configured?"),
    ("d047", "dev", "Which email backend settings configure SMTP with TLS and authentication?"),
    ("d048", "dev", "What production commands collect and serve Django static files?"),
    ("d049", "dev", "How do I write a custom django-admin management command with arguments?"),
    ("d050", "test", "What code creates a Django Channels WebSocket consumer and routes it with ASGI?"),
]


def paragraph_containing(text: str, needle: str) -> str:
    normalized_needle = " ".join(needle.split())
    matches = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text)
               if normalized_needle in " ".join(paragraph.split())]
    if len(matches) != 1:
        raise ValueError(f"Expected one paragraph containing {needle!r}; found {len(matches)}")
    return matches[0]


def build_records():
    corpus = get_corpus("django-5.2")
    documents = {document.doc_id: document.text for document in load_documents(corpus.raw_dir)}
    records = []
    for draft in DRAFT:
        evidence = []
        sources = []
        for source, needle in draft["evidence_needles"]:
            if source not in sources:
                sources.append(source)
            evidence.append({"source": source, "quote": paragraph_containing(documents[source], needle)})
        row = {key: value for key, value in draft.items() if key != "evidence_needles"}
        records.append({**row, "gold_sources": sources, "evidence": evidence})
    for identifier, split, question in UNANSWERABLE:
        records.append({
            "id": identifier,
            "category": "unanswerable",
            "split": split,
            "question": question,
            "answerable": False,
            "reference_answer": "I cannot find this in the provided documentation.",
            "gold_sources": [],
            "evidence": [],
        })
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace an existing draft")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.force:
        parser.error(f"{OUTPUT} already exists; pass --force to rebuild it")
    records = build_records()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    print(f"Wrote {len(records)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
