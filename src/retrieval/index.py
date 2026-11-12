"""Build Chroma indexes for fixed or semantic chunks."""
import argparse
import sys
from pathlib import Path

import chromadb

from src.chunking.fixed import CHUNK_SIZE, OVERLAP, chunk_documents
from src.ingestion.loader import load_documents
from src.retrieval.embeddings import MODEL_NAME, embed_texts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "fastapi_baseline"
SEMANTIC_COLLECTION_NAME = "fastapi_semantic"


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=["A", "B"], default="A",
                        help="A: fixed-size chunks; B: semantic chunks")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    docs = load_documents(PROJECT_ROOT / "data" / "raw")
    if args.config == "A":
        chunks = chunk_documents(docs)
        collection_name = COLLECTION_NAME
        settings = f"fixed chunk_size={CHUNK_SIZE}, overlap={OVERLAP}"
    else:
        from src.chunking.semantic import (BREAKPOINT_PERCENTILE, MAX_CHUNK_CHARS,
                                           MIN_BREAKPOINT_DISTANCE, MIN_CHUNK_CHARS, UNIT_MAX_CHARS,
                                           semantic_chunk_documents)
        chunks = semantic_chunk_documents(docs, embed_texts)
        collection_name = SEMANTIC_COLLECTION_NAME
        settings = (f"semantic min={MIN_CHUNK_CHARS}, max={MAX_CHUNK_CHARS}, "
                    f"unit_max={UNIT_MAX_CHARS}, breakpoint_percentile={BREAKPOINT_PERCENTILE}, "
                    f"minimum_distance={MIN_BREAKPOINT_DISTANCE}")
    collection = build_index(chunks, collection_name)

    print(f"Embedding model: {MODEL_NAME}")
    print(f"Chunk settings: {settings}")
    print(f"Chunks given to Chroma: {len(chunks)}")
    print(f"Chunks stored in collection '{collection_name}': {collection.count()}")

    sample_id = chunks[0].chunk_id
    stored = collection.get(ids=[sample_id], include=["documents", "metadatas"])
    print(f"\nStored record {sample_id} has metadata: {stored['metadatas'][0]}")
    print(f"First 120 characters of its text: {stored['documents'][0][:120]!r}")


if __name__ == "__main__":
    main()
