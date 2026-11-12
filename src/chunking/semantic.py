"""Embedding-based semantic chunking (Configuration B)."""
from __future__ import annotations

import re

from src.chunking.fixed import Chunk
from src.ingestion.loader import Document

MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 900
UNIT_MAX_CHARS = 450
BREAKPOINT_PERCENTILE = 75
MIN_BREAKPOINT_DISTANCE = 0.25

PARAGRAPH = re.compile(r"\S(?:.*?\S)?(?=\n[ \t]*\n|\Z)", re.DOTALL)


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("A percentile needs at least one value")
    position = (len(ordered) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _split_long_span(text: str, start: int, end: int,
                     max_chars: int) -> list[tuple[int, int]]:
    spans = []
    cursor = start
    while end - cursor > max_chars:
        limit = cursor + max_chars
        minimum = cursor + max_chars // 2
        candidates = [text.rfind(mark, minimum, limit) for mark in ("\n", ". ", "? ", "! ", "; ", " ")]
        boundary = max(candidates)
        if boundary < minimum:
            boundary = limit
        elif text[boundary:boundary + 2] in {". ", "? ", "! ", "; "}:
            boundary += 1
        piece_end = boundary
        while piece_end > cursor and text[piece_end - 1].isspace():
            piece_end -= 1
        if piece_end > cursor:
            spans.append((cursor, piece_end))
        cursor = boundary
        while cursor < end and text[cursor].isspace():
            cursor += 1
    if cursor < end:
        spans.append((cursor, end))
    return spans


def semantic_units(text: str, max_chars: int = UNIT_MAX_CHARS) -> list[tuple[int, int]]:
    """Return exact source spans for Markdown paragraphs and long sub-parts."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    spans = []
    for match in PARAGRAPH.finditer(text):
        spans.extend(_split_long_span(text, match.start(), match.end(), max_chars))
    return spans


def _merge_short_spans(spans: list[tuple[int, int]], min_chars: int,
                       max_chars: int) -> list[tuple[int, int]]:
    """Merge undersized edge/remainder spans when a neighbor has room."""
    merged = list(spans)
    while len(merged) > 1:
        changed = False
        for index, (start, end) in enumerate(merged):
            if end - start >= min_chars:
                continue
            candidates = []
            if index:
                previous = (merged[index - 1][0], end)
                if previous[1] - previous[0] <= max_chars:
                    candidates.append((previous[1] - previous[0], index - 1, index, previous))
            if index + 1 < len(merged):
                following = (start, merged[index + 1][1])
                if following[1] - following[0] <= max_chars:
                    candidates.append((following[1] - following[0], index, index + 1, following))
            if not candidates:
                continue
            _, left, right, replacement = min(candidates)
            merged[left:right + 1] = [replacement]
            changed = True
            break
        if not changed:
            break
    return merged


def semantic_chunk_text(text: str, embed_fn, min_chars: int = MIN_CHUNK_CHARS,
                        max_chars: int = MAX_CHUNK_CHARS,
                        breakpoint_percentile: float = BREAKPOINT_PERCENTILE,
                        unit_max_chars: int = UNIT_MAX_CHARS) -> list[tuple[int, str]]:
    """Split at large meaning changes while keeping every chunk source-contiguous.

    Adjacent paragraph/sentence units are embedded. A boundary is eligible when
    its cosine distance is in the highest quarter for that document and the
    current chunk has reached ``min_chars``. ``max_chars`` is a hard bound.
    """
    if min_chars <= 0 or max_chars < min_chars or unit_max_chars <= 0:
        raise ValueError("Require 0 < min_chars <= max_chars and unit_max_chars > 0")
    if not 0 <= breakpoint_percentile <= 100:
        raise ValueError("breakpoint_percentile must be between 0 and 100")
    spans = semantic_units(text, min(unit_max_chars, max_chars))
    if not spans:
        return []
    if len(spans) == 1:
        start, end = spans[0]
        return [(start, text[start:end])]

    vectors = embed_fn([text[start:end] for start, end in spans])
    if len(vectors) != len(spans):
        raise ValueError("embed_fn returned the wrong number of vectors")
    distances = [1 - float(vectors[i] @ vectors[i + 1]) for i in range(len(spans) - 1)]
    threshold = _percentile(distances, breakpoint_percentile)

    chunks = []
    chunk_start = spans[0][0]
    for index, (_, unit_end) in enumerate(spans[:-1]):
        next_start, next_end = spans[index + 1]
        current_length = unit_end - chunk_start
        forced_boundary = next_end - chunk_start > max_chars
        relative_outlier = len(distances) == 1 or distances[index] > threshold
        semantic_boundary = (current_length >= min_chars and relative_outlier
                             and distances[index] >= MIN_BREAKPOINT_DISTANCE)
        if forced_boundary or semantic_boundary:
            chunks.append((chunk_start, unit_end))
            chunk_start = next_start
    chunks.append((chunk_start, spans[-1][1]))
    return [(start, text[start:end])
            for start, end in _merge_short_spans(chunks, min_chars, max_chars)]


def semantic_chunk_documents(docs: list[Document], embed_fn,
                             min_chars: int = MIN_CHUNK_CHARS,
                             max_chars: int = MAX_CHUNK_CHARS,
                             breakpoint_percentile: float = BREAKPOINT_PERCENTILE,
                             unit_max_chars: int = UNIT_MAX_CHARS) -> list[Chunk]:
    chunks = []
    for doc in docs:
        pieces = semantic_chunk_text(doc.text, embed_fn, min_chars, max_chars,
                                     breakpoint_percentile, unit_max_chars)
        for index, (start, piece) in enumerate(pieces):
            chunks.append(Chunk(f"{doc.doc_id}::s{index}", doc.doc_id, index, start, piece))
    return chunks


if __name__ == "__main__":
    import sys
    from pathlib import Path

    from src.ingestion.loader import load_documents
    from src.retrieval.embeddings import embed_texts

    sys.stdout.reconfigure(encoding="utf-8")
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    documents = load_documents(raw_dir)
    result = semantic_chunk_documents(documents, embed_texts)
    sizes = [len(chunk.text) for chunk in result]
    print(f"Semantic settings: min={MIN_CHUNK_CHARS}, max={MAX_CHUNK_CHARS}, "
          f"breakpoint percentile={BREAKPOINT_PERCENTILE}, "
          f"minimum distance={MIN_BREAKPOINT_DISTANCE}")
    print(f"Total chunks: {len(result)}")
    print(f"Chunk length: min={min(sizes)}, average={sum(sizes) // len(sizes)}, max={max(sizes)}")
