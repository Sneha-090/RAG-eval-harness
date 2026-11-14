"""Capture resumable baseline observations; no quality scores are inferred."""
import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.validate import ROOT, validate
from src.ingestion.loader import load_documents


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_digest(path):
    """Hash UTF-8 project text with platform line endings normalized to LF."""
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def load_dataset(path):
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    errors = validate(rows, {d.doc_id: d.text for d in load_documents(ROOT / 'data/raw')})
    if not rows or errors:
        raise ValueError('Invalid dataset: ' + '; '.join(errors or ['empty dataset']))
    return rows


def select_rows(rows, split, limit=None, identifiers=None):
    """Select one split, optionally restricted to exact IDs in dataset order."""
    selected = [row for row in rows if row['split'] == split]
    if identifiers is not None:
        if limit is not None:
            raise ValueError('--limit and --ids cannot be used together')
        if len(set(identifiers)) != len(identifiers):
            raise ValueError('--ids contains duplicates')
        available = {row['id'] for row in selected}
        missing = [identifier for identifier in identifiers if identifier not in available]
        if missing:
            raise ValueError('Unknown IDs for selected split: ' + ', '.join(missing))
        requested = set(identifiers)
        selected = [row for row in selected if row['id'] in requested]
    elif limit:
        selected = selected[:limit]
    if not selected:
        raise ValueError('No questions selected')
    return selected


def snapshot(root=ROOT):
    """Hash actual source/corpus/settings, including uncommitted changes, never .env."""
    paths = list((root / 'src').rglob('*.py')) + list((root / 'data/raw').glob('*.md'))
    paths += [root / 'requirements.txt', root / 'METRICS.md', root / 'data/CORPUS.md']
    return {p.relative_to(root).as_posix(): file_digest(p)
            for p in sorted(paths)}


def run_records(rows, output, contract, retrieve_fn, generate_fn=None, retry_errors=False, delay=0):
    """Atomic per-question checkpoints; successful retrieval survives generator failure."""
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate record IDs')
    output.mkdir(parents=True, exist_ok=True)
    # Exclusive process lock prevents duplicate paid calls by concurrent invocations.
    lock = output / '.lock'
    with lock.open('x', encoding='utf-8') as handle:
        handle.write(str(os.getpid()))
    try:
        manifest = output / 'manifest.json'
        signature = digest({'rows': rows, 'contract': contract})
        if manifest.exists():
            if json.loads(manifest.read_text(encoding='utf-8'))['signature'] != signature:
                raise ValueError('Run inputs changed. Use a new output directory.')
        else:
            if list(output.glob('record-*.json')):
                raise ValueError('Checkpoints exist without a manifest; use a new directory.')
            atomic_json(manifest, {'signature': signature, 'created_utc': datetime.now(timezone.utc).isoformat(),
                                   'contract': contract, 'dataset': rows})
        results = []
        for index, row in enumerate(rows):
            path = output / f'record-{index:04}.json'
            result = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'id': row['id']}
            if result.get('status') == 'ok' or (result.get('status') == 'error' and not retry_errors):
                results.append(result)
                continue
            start = time.perf_counter()
            previous_elapsed = result.get('elapsed_s', 0)
            result.pop('error_type', None)
            try:
                if 'chunks' not in result:
                    t0 = time.perf_counter()
                    result['chunks'] = retrieve_fn(row['question'], contract['k'])
                    result['retrieval_s'] = time.perf_counter() - t0
                    result['status'] = 'retrieved'
                    result['elapsed_s'] = previous_elapsed + time.perf_counter() - start
                    atomic_json(path, result)
                if generate_fn is not None:
                    # Pacing is excluded from observed request latency.
                    time.sleep(delay)
                    t0 = time.perf_counter()
                    answer = generate_fn(row['question'], result['chunks'])
                    result['generation_s'] = time.perf_counter() - t0
                    if not isinstance(answer, str) or not answer.strip():
                        raise ValueError('Empty generated answer')
                    result['answer'] = answer
                result['status'] = 'ok'
            except Exception as exc:
                result.update(status='error', error_type=type(exc).__name__)
                # Provider exception text can contain credentials or response bodies.
            result['elapsed_s'] = previous_elapsed + time.perf_counter() - start
            result['resumed'] = previous_elapsed > 0
            atomic_json(path, result)
            results.append(result)
        summary = {'requested': len(rows), 'completed': sum(r['status'] == 'ok' for r in results),
                   'failed': sum(r['status'] == 'error' for r in results),
                   'quality_scores': None,
                   'note': 'Capture complete. Use src.evaluation.report for retrieval scores; answer judging is pending.'}
        atomic_json(output / 'summary.json', summary)
        return summary
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'data/eval/questions.draft.jsonl')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['retrieval', 'answers'], default='retrieval')
    parser.add_argument('--split', choices=['dev', 'test'], default='dev')
    parser.add_argument('--config', choices=['A', 'B', 'C', 'D'], default='A',
                        help='A: fixed+dense; B: semantic+dense; C: fixed+hybrid; D: hybrid+reranker')
    parser.add_argument('--k', type=int, default=5)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--ids', nargs='+', help='Exact question IDs; preserves dataset order')
    parser.add_argument('--delay', type=float, default=15, help='Seconds before each generation call')
    parser.add_argument('--retry-errors', action='store_true')
    args = parser.parse_args()
    if args.k <= 0 or (args.limit is not None and args.limit <= 0) or not math.isfinite(args.delay) or args.delay < 0:
        parser.error('k/limit must be positive; delay must be finite and nonnegative')
    try:
        rows = load_dataset(args.dataset)
        selected = select_rows(rows, args.split, args.limit, args.ids)
        from src.retrieval.dense import retrieve as dense_retrieve
        from src.retrieval.embeddings import MODEL_NAME, MODEL_REVISION, embed_texts, get_model
        from src.retrieval.index import COLLECTION_NAME, SEMANTIC_COLLECTION_NAME
        model = get_model()
        if args.config == 'B':
            from src.chunking.semantic import (BREAKPOINT_PERCENTILE, MAX_CHUNK_CHARS,
                                               MIN_BREAKPOINT_DISTANCE, MIN_CHUNK_CHARS, UNIT_MAX_CHARS,
                                               semantic_chunk_documents)
            expected_chunks = semantic_chunk_documents(load_documents(ROOT / 'data/raw'), embed_texts)
            collection_name = SEMANTIC_COLLECTION_NAME
            chunking = {'strategy': 'semantic', 'min_chars': MIN_CHUNK_CHARS,
                        'max_chars': MAX_CHUNK_CHARS, 'unit_max_chars': UNIT_MAX_CHARS,
                        'breakpoint_percentile': BREAKPOINT_PERCENTILE,
                        'minimum_breakpoint_distance': MIN_BREAKPOINT_DISTANCE}
        else:
            from src.chunking.fixed import CHUNK_SIZE, OVERLAP, chunk_documents
            expected_chunks = chunk_documents(load_documents(ROOT / 'data/raw'))
            collection_name = COLLECTION_NAME
            chunking = {'strategy': 'fixed', 'chunk_size': CHUNK_SIZE, 'overlap': OVERLAP}
        contract = {'version': 1, 'config': args.config, 'mode': args.mode, 'k': args.k,
                    'embedding_model': MODEL_NAME, 'collection': collection_name,
                    'embedding_revision': MODEL_REVISION,
                    'chunking': chunking,
                    'dataset_sha256': file_digest(args.dataset),
                    'files': snapshot(), 'python': platform.python_version(), 'platform': platform.platform()}
        contract['selection'] = {'split': args.split, 'limit': args.limit,
                                 'ids': args.ids}
        generation = None
        if args.mode == 'answers':
            from src.generation.answer import SYSTEM_PROMPT, build_prompt
            from src.generation.llm import GENERATOR, generate
            if not os.getenv('GROQ_API_KEY'):
                raise ValueError('GROQ_API_KEY is missing')
            contract['generator'] = dict(GENERATOR)
            contract['prompt_sha256'] = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()
            generation = lambda question, chunks: generate(GENERATOR, build_prompt(question, chunks), SYSTEM_PROMPT)['text']
        # Verify actual stored chunks match the current corpus/chunking before reuse.
        import chromadb
        from src.retrieval.index import DB_PATH
        collection = chromadb.PersistentClient(path=str(DB_PATH)).get_collection(collection_name)
        stored = collection.get(include=['documents', 'metadatas'])
        documents, metadatas = stored['documents'], stored['metadatas']
        if documents is None or metadatas is None:
            raise ValueError('Stored index omitted documents or metadata')
        actual = {i: (text, meta['doc_id'])
                  for i, text, meta in zip(stored['ids'], documents, metadatas)}
        expected = {c.chunk_id: (c.text, c.doc_id) for c in expected_chunks}
        if actual != expected:
            raise ValueError(f'Index differs from corpus/chunking; rebuild configuration {args.config}')
        contract['index_content_sha256'] = digest(actual)
        contract['index_metadata'] = collection.metadata
        retrieve = lambda question, k: dense_retrieve(question, k, collection_name)
        if args.config in {'C', 'D'}:
            from src.retrieval.hybrid import B, CANDIDATES, K1, RRF_CONSTANT, HybridRetriever
            chunks = [{'chunk_id': key, 'text': value[0], 'doc_id': value[1]}
                      for key, value in actual.items()]
            retrieve = HybridRetriever(chunks, retrieve).retrieve
            contract['hybrid'] = {'k1': K1, 'b': B, 'rrf_constant': RRF_CONSTANT,
                                  'candidates_per_ranker': max(args.k, CANDIDATES)}
        if args.config == 'D':
            from src.retrieval.rerank import (RERANK_BATCH_SIZE, RERANK_CANDIDATES,
                                              RERANKER_MODEL_NAME, RERANKER_MODEL_REVISION,
                                              RerankedRetriever,
                                              get_reranker, predict_scores)
            reranker = get_reranker()
            retrieve = RerankedRetriever(retrieve, predict_scores, RERANK_CANDIDATES).retrieve
            contract['reranker'] = {'model': RERANKER_MODEL_NAME,
                                    'revision': RERANKER_MODEL_REVISION,
                                    'candidate_count': RERANK_CANDIDATES,
                                    'batch_size': RERANK_BATCH_SIZE,
                                    'max_length': reranker.max_seq_length}
        # Fail once on a missing model instead of marking every question failed.
        contract['embedding_max_length'] = model.max_seq_length
        try:
            contract['git_commit'] = subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            contract['git_commit'] = None
        summary = run_records(selected, args.output, contract, retrieve, generation, args.retry_errors, args.delay)
        print(json.dumps(summary, indent=2))
        if summary['failed']:
            raise SystemExit(1)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Run stopped: {exc}\n')


if __name__ == '__main__':
    main()
