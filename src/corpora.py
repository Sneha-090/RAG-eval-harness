"""Versioned corpus registry shared by ingestion, indexing and evaluation."""
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CorpusConfig:
    key: str
    label: str
    raw_dir: Path
    dataset: Path
    record: Path
    fixed_collection: str
    semantic_collection: str

    def collection_name(self, chunking: str) -> str:
        if chunking == "fixed":
            return self.fixed_collection
        if chunking == "semantic":
            return self.semantic_collection
        raise ValueError(f"Unknown chunking strategy: {chunking}")


CORPORA = {
    "fastapi-v1": CorpusConfig(
        key="fastapi-v1",
        label="FastAPI benchmark v1",
        raw_dir=ROOT / "data" / "raw",
        dataset=ROOT / "data" / "eval" / "questions.draft.jsonl",
        record=ROOT / "data" / "CORPUS.md",
        fixed_collection="fastapi_baseline",
        semantic_collection="fastapi_semantic",
    ),
    "django-5.2": CorpusConfig(
        key="django-5.2",
        label="Django 5.2 LTS benchmark v2",
        raw_dir=ROOT / "data" / "corpora" / "django-5.2" / "raw",
        dataset=ROOT / "data" / "eval" / "django-5.2" / "questions.draft.jsonl",
        record=ROOT / "data" / "corpora" / "django-5.2" / "CORPUS.md",
        fixed_collection="django52_baseline",
        semantic_collection="django52_semantic",
    ),
}


def get_corpus(key: str) -> CorpusConfig:
    try:
        return CORPORA[key]
    except KeyError as exc:
        raise ValueError(f"Unknown corpus {key!r}; choose one of {', '.join(CORPORA)}") from exc
