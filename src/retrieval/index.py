"""Build a Chroma vector index from chunks (Configuration A: fixed-size chunks)."""
import sys
from pathlib import Path

import chromadb

from src.chunking.fixed import CHUNK_SIZE, OVERLAP, chunk_documents
from src.ingestion.loader import load_documents
from src.retrieval.embeddings import MODEL_NAME, embed_texts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "fastapi_baseline"


def build_index(chunks, collection_name: str = COLLECTION_NAME):
    """Create (or recreate) a collection and store all chunks with their vectors."""
    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        client.delete_collection(collection_name)  # start clean
    except Exception:
        pass  # the collection did not exist yet

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # measure similarity with cosine
    )
    vectors = embed_texts([c.text for c in chunks])
    collection.add(
        ids=[c.chunk_id for c in chunks],
        embeddings=vectors.tolist(),
        documents=[c.text for c in chunks],
        metadatas=[{"doc_id": c.doc_id, "index": c.index} for c in chunks],
    )
    return collection


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    docs = load_documents(PROJECT_ROOT / "data" / "raw")
    chunks = chunk_documents(docs)
    collection = build_index(chunks)

    print(f"Embedding model: {MODEL_NAME}")
    print(f"Chunk settings: chunk_size={CHUNK_SIZE}, overlap={OVERLAP}")
    print(f"Chunks given to Chroma: {len(chunks)}")
    print(f"Chunks stored in collection '{COLLECTION_NAME}': {collection.count()}")

    stored = collection.get(ids=["body.md::0"], include=["documents", "metadatas"])
    print(f"\nStored record body.md::0 has metadata: {stored['metadatas'][0]}")
    print(f"First 120 characters of its text: {stored['documents'][0][:120]!r}")