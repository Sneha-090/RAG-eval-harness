"""Fixed-size chunking with overlap (Configuration A baseline)."""
import sys
from dataclasses import dataclass
from pathlib import Path

from src.ingestion.loader import Document, load_documents

CHUNK_SIZE = 550 # max charcaters per chunk
OVERLAP = 80   # characters repeated from the end of the previous chunk


@dataclass
class Chunk:
    chunk_id: str    # for example "body.md::3"
    doc_id: str      # the source file, used later to check retrieval (Hit@K)
    index: int       # position of the chunk inside its document
    start_char: int  # where the chunk starts in the normalized text
    text: str


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    """Return a list of (start_char, chunk_text) pairs."""
    pieces = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # Move the cut back to a space or line break, but keep the
            # chunk at least half full.
            snap = max(text.rfind(" ", start, end), text.rfind("\n", start, end))
            if snap > start + chunk_size // 2:
                end = snap
        piece = text[start:end].strip()
        if piece:
            pieces.append((start, piece))
        if end >= n:
            break
        start = end - overlap  # always moves forward, because overlap < chunk_size / 2
    return pieces


def chunk_documents(docs: list[Document], chunk_size: int = CHUNK_SIZE,
                    overlap: int = OVERLAP) -> list[Chunk]:
    chunks = []
    for doc in docs:
        for i, (start, piece) in enumerate(chunk_text(doc.text, chunk_size, overlap)):
            chunks.append(Chunk(f"{doc.doc_id}::{i}", doc.doc_id, i, start, piece))
    return chunks


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    docs = load_documents(raw_dir)
    chunks = chunk_documents(docs)

    print(f"Settings: chunk_size={CHUNK_SIZE}, overlap={OVERLAP}")
    print(f"Total chunks: {len(chunks)}\n")

    for d in docs:
        count = sum(1 for c in chunks if c.doc_id == d.doc_id)
        print(f"{d.doc_id:42}{count:>5} chunks")

    sizes = [len(c.text) for c in chunks]
    print(f"\nChunk length: min={min(sizes)}, average={sum(sizes) // len(sizes)}, max={max(sizes)}")

    first_doc = docs[0].doc_id
    sample = [c for c in chunks if c.doc_id == first_doc][:2]
    for c in sample:
        print(f"\n--- {c.chunk_id} (starts at character {c.start_char}) ---")
        print(c.text)