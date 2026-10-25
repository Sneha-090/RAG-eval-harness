"""Deterministic retrieval metrics defined in METRICS.md version 2."""
import math
from statistics import mean

METRIC_NAMES = ('hit_at_k', 'mrr_at_k', 'source_recall_at_k',
                'evidence_coverage_at_k', 'evidence_complete_at_k')


def occurrences(text, substring):
    start = text.find(substring)
    while start >= 0:
        yield start
        start = text.find(substring, start + 1)


def score_retrieval(row, chunks, documents, k):
    if type(k) is not int or k <= 0:
        raise ValueError('k must be a positive integer')
    if not row['answerable']:
        return None
    ranked = chunks[:k]
    sources = set(row['gold_sources'])
    if not sources or not row['evidence']:
        raise ValueError('Answerable record needs gold sources and evidence')
    covered = {}
    seen_ids = set()
    for chunk in ranked:
        source, text = chunk['doc_id'], chunk['text']
        if chunk['chunk_id'] in seen_ids:
            raise ValueError('Duplicate retrieved chunk ID')
        seen_ids.add(chunk['chunk_id'])
        if source not in documents or not text:
            raise ValueError('Retrieved chunk has unknown source or empty text')
        positions = list(occurrences(documents[source], text))
        if not positions:
            raise ValueError('Retrieved text is absent from the source document')
        target = covered.setdefault(source, set())
        for start in positions:
            target.update(range(start, start + len(text)))
    evidence_scores = []
    for item in row['evidence']:
        source, quote = item['source'], item['quote']
        starts = list(occurrences(documents[source], quote))
        meaningful = [i for i, char in enumerate(quote) if not char.isspace()]
        if not starts or not meaningful:
            raise ValueError('Evidence is absent or empty')
        evidence_scores.append(max(
            sum(start + i in covered.get(source, set()) for i in meaningful) / len(meaningful)
            for start in starts))
    first = next((rank for rank, chunk in enumerate(ranked, 1) if chunk['doc_id'] in sources), None)
    return {'hit_at_k': int(first is not None), 'mrr_at_k': 1 / first if first else 0,
            'source_recall_at_k': len(sources & {c['doc_id'] for c in ranked}) / len(sources),
            'evidence_coverage_at_k': mean(evidence_scores),
            'evidence_complete_at_k': int(all(value == 1 for value in evidence_scores))}


def summarize(rows, observations, documents, k):
    by_id = {r['id']: r for r in observations}
    if len(by_id) != len(observations) or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate question IDs')
    if set(by_id) - {r['id'] for r in rows}:
        raise ValueError('Observation does not belong to this dataset')
    details, scores, categories, latencies = [], [], {}, []
    missing = 0
    for row in rows:
        observation = by_id.get(row['id'], {})
        retrieved = 'chunks' in observation
        score = score_retrieval(row, observation['chunks'], documents, k) if retrieved else None
        if row['answerable']:
            if score is None:
                missing += 1
            else:
                scores.append(score)
                categories.setdefault(row['category'], []).append(score)
        if retrieved and 'retrieval_s' in observation:
            value = observation['retrieval_s']
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError('Invalid retrieval latency')
            latencies.append(value)
        details.append({'id': row['id'], 'category': row['category'],
                        'status': observation.get('status', 'missing'), 'scores': score})

    def aggregate(items):
        return {'count': len(items), **{name: mean(s[name] for s in items) if items else None
                                      for name in METRIC_NAMES}}

    latency = {'count': len(latencies), 'mean_s': mean(latencies) if latencies else None,
               'p95_s': sorted(latencies)[math.ceil(.95 * len(latencies)) - 1] if latencies else None}
    return {'metrics_version': 2, 'k': k, 'requested': len(rows),
            'answerable_requested': sum(r['answerable'] for r in rows),
            'answerable_missing_retrieval': missing,
            'unanswerable_requested': sum(not r['answerable'] for r in rows),
            'retrieval_complete': all('chunks' in by_id.get(r['id'], {}) for r in rows),
            'overall': aggregate(scores), 'by_category': {c: aggregate(v) for c, v in sorted(categories.items())},
            'retrieval_latency': latency, 'questions': details,
            'answer_quality': None,
            'limitations': ['Draft benchmark; human review and freezing are pending.',
                            'Averages include available retrievals only; missing counts must be reported.',
                            'Evidence scores measure exact text coverage, not semantic sufficiency.',
                            'Retrieval latency excludes model preloading; it is not end-to-end answer latency.',
                            'No correctness, faithfulness, abstention, or judge-agreement scores exist.']}
