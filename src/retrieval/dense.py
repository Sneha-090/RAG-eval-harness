"""Dense retrieval: find the top K chunks for a question (Configuration A)."""
import sys

import chromadb

from src.retrieval.embeddings import embed_texts
from src.retrieval.index import COLLECTION_NAME, DB_PATH

TOP_K = 5  # as defined in METRICS.md


def retrieve(question: str, k: int = TOP_K, collection_name: str = COLLECTION_NAME):
    """Return the k most similar chunks as a list of dictionaries."""
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_collection(collection_name)
    query_vector = embed_texts([question])[0].tolist()
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "chunk_id": chunk_id,
            "doc_id": meta["doc_id"],
            "similarity": 1 - dist,  # cosine similarity = 1 - cosine distance
            "text": text,
        }
        for chunk_id, meta, dist, text in zip(
            result["ids"][0], result["metadatas"][0],
            result["distances"][0], result["documents"][0],
        )
    ]


def show(question: str, k: int = TOP_K) -> None:
    print(f"\nQUESTION: {question}")
    for rank, r in enumerate(retrieve(question, k), start=1):
        preview = " ".join(r["text"].split())[:140]
        print(f"  {rank}. {r['similarity']:.3f}  {r['chunk_id']}")
        print(f"       {preview}...")


QUESTIONS = [
    "What is the difference between a path parameter and a query parameter?",
    "How do I read a header value in FastAPI?",
    "How can I declare a cookie parameter?",
    "What does the response_model parameter do?",
    "How do I return an error to the client with HTTPException?",
    "What is the OAuth2 password flow?",
    "How do I deploy FastAPI with Docker?",  # NOT covered by the corpus on purpose
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:
        show(" ".join(sys.argv[1:]))  # your own question from the command line
    else:
        for q in QUESTIONS:
            show(q)