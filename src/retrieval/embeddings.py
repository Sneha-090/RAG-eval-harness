"""Create embeddings (vectors) for text with a local sentence-transformers model."""
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.chunking.fixed import chunk_documents
from src.ingestion.loader import load_documents

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    """Load the model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str], batch_size: int = 32):
    """Return one normalized vector per text (a numpy array)."""
    return get_model().encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,  # length 1, so cosine similarity = dot product
        show_progress_bar=False,
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    chunks = chunk_documents(load_documents(raw_dir))
    texts = [c.text for c in chunks]

    model = get_model()
    vectors = embed_texts(texts)

    print(f"Model: {MODEL_NAME}")
    print(f"Maximum input length: {model.max_seq_length} tokens")
    print(f"Vectors shape: {vectors.shape}  (chunks, numbers per chunk)")
    print(f"First 8 numbers of {chunks[0].chunk_id}: {vectors[0][:8].round(3)}")

    token_counts = [len(ids) for ids in model.tokenizer(texts)["input_ids"]]
    too_long = sum(1 for t in token_counts if t > model.max_seq_length)
    print(f"Longest chunk: {max(token_counts)} tokens")
    print(f"Chunks above the token limit: {too_long} of {len(texts)}")

    # A first look at "meaning": how close is a question to three different chunks?
    question = "How do I declare a request body?"
    q = embed_texts([question])[0]
    print(f"\nQuestion: {question}")
    wanted = {"body.md::0", "cookie-params.md::0", "security__first-steps.md::0"}
    for chunk, vec in zip(chunks, vectors):
        if chunk.chunk_id in wanted:
            print(f"  similarity with {chunk.chunk_id:30}{float(q @ vec):.3f}")