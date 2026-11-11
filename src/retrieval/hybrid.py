"""Rank the existing chunks with BM25 and fuse them with dense results."""
import math
import re
from collections import Counter

TOKEN = re.compile(r"\w+")
K1 = 1.2
B = 0.75
RRF_CONSTANT = 60
CANDIDATES = 20


def tokenize(text):
    return TOKEN.findall(text.casefold())


class BM25:
    def __init__(self, chunks):
        self.chunks = {chunk["chunk_id"]: chunk for chunk in chunks}
        self.frequencies = {key: Counter(tokenize(chunk["text"]))
                            for key, chunk in self.chunks.items()}
        self.lengths = {key: sum(counts.values()) for key, counts in self.frequencies.items()}
        self.average_length = sum(self.lengths.values()) / max(1, len(self.chunks)) or 1
        document_frequency = Counter(term for counts in self.frequencies.values() for term in counts)
        self.idf = {term: math.log1p((len(self.chunks) - count + 0.5) / (count + 0.5))
                    for term, count in document_frequency.items()}

    def search(self, question, k):
        terms = sorted(set(tokenize(question)) & self.idf.keys())
        ranked = []
        for key, counts in self.frequencies.items():
            length_penalty = K1 * (1 - B + B * self.lengths[key] / self.average_length)
            score = sum(self.idf[term] * counts[term] * (K1 + 1) /
                        (counts[term] + length_penalty) for term in terms if counts[term])
            if score:
                ranked.append((score, key))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [self.chunks[key] for _, key in ranked[:k]]


def fuse(dense, lexical, k):
    scores, chunks = {}, {}
    for ranking in (dense, lexical):
        for rank, chunk in enumerate(ranking, 1):
            key = chunk["chunk_id"]
            chunks.setdefault(key, chunk)
            scores[key] = scores.get(key, 0) + 1 / (RRF_CONSTANT + rank)
    ranked = sorted(scores, key=lambda key: (-scores[key], key))
    return [{**chunks[key], "rrf_score": scores[key]} for key in ranked[:k]]


class HybridRetriever:
    def __init__(self, chunks, dense_retrieve):
        self.bm25 = BM25(chunks)
        self.dense_retrieve = dense_retrieve

    def retrieve(self, question, k):
        count = min(max(k, CANDIDATES), len(self.bm25.chunks))
        if not count:
            return []
        return fuse(self.dense_retrieve(question, count), self.bm25.search(question, count), k)
