"""Generate an answer from retrieved chunks (Configuration A)."""
import sys
import time

from src.generation.llm import GENERATOR, generate
from src.retrieval.dense import TOP_K, retrieve

ABSTAIN_PHRASE = "I cannot find this in the provided documentation."

SYSTEM_PROMPT = f"""You answer questions using ONLY the context provided by the user.
Rules:
1. Use only facts that appear in the context. Do not use outside knowledge.
2. If the context does not contain the answer, reply exactly: {ABSTAIN_PHRASE}
3. Do not guess, and do not fill gaps with general knowledge.
4. Answer in at most four sentences. After the facts you use, name their source IDs in square brackets, for example [body.md::0]."""


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(f"[{c['chunk_id']}]\n{c['text']}" for c in chunks)
    return f"Context:\n{context}\n\nQuestion: {question}"


def answer_question(question: str, k: int = TOP_K) -> dict:
    t0 = time.perf_counter()
    chunks = retrieve(question, k)
    t1 = time.perf_counter()
    out = generate(GENERATOR, build_prompt(question, chunks), SYSTEM_PROMPT)
    t2 = time.perf_counter()
    return {
        "question": question,
        "answer": out["text"],
        "sources": [c["chunk_id"] for c in chunks],
        "retrieval_s": t1 - t0,
        "generation_s": t2 - t1,
    }


QUESTIONS = [
    "What is the difference between a path parameter and a query parameter?",
    "How do I read a header value in FastAPI?",
    "How can I declare a cookie parameter?",
    "How do I return an error to the client with HTTPException?",
    "What is the OAuth2 password flow?",
    "How do I deploy FastAPI with Docker?",  # NOT covered: the correct reply is a refusal
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else QUESTIONS
    for q in questions:
        r = answer_question(q)
        print(f"\nQUESTION: {r['question']}")
        print(f"ANSWER: {r['answer']}")
        print(f"SOURCES RETRIEVED: {', '.join(r['sources'])}")
        print(f"TIME: retrieval {r['retrieval_s']:.2f} s, generation {r['generation_s']:.2f} s")