"""Score saved retrieval observations without model or API calls."""
import argparse
import hashlib
import json
from pathlib import Path

from src.evaluation.run import ROOT, atomic_json
from src.evaluation.metrics import METRIC_NAMES, summarize
from src.ingestion.loader import load_documents


def render_markdown(report):
    lines = ['# Draft baseline retrieval report', '',
             f"K = {report['k']}; metric contract v2; draft development benchmark.", '',
             f"Questions: {report['requested']}; answerable: {report['answerable_requested']}; "
             f"missing answerable retrievals: {report['answerable_missing_retrieval']}.", '',
             'Scores are fractions from 0 to 1. Answer quality has not been evaluated.', '',
             '| Group | N | Hit@K | MRR@K | Source recall@K | Evidence coverage@K | Complete evidence@K |',
             '|---|---:|---:|---:|---:|---:|---:|']
    groups = {'Overall': report['overall'], **report['by_category']}
    for name, group in groups.items():
        values = ['n/a' if group[key] is None else f'{group[key]:.4f}' for key in METRIC_NAMES]
        lines.append('| ' + ' | '.join([name, str(group['count']), *values]) + ' |')
    latency = report['retrieval_latency']
    lines.extend(['', f"Retrieval timing samples: {latency['count']}.", '', '## Limitations', ''])
    lines.extend('- ' + text for text in report['limitations'])
    lines.extend(['', '## Questions needing evidence investigation', ''])
    for row in report['questions']:
        scores = row['scores']
        if scores is not None and scores['evidence_complete_at_k'] == 0:
            lines.append(f"- {row['id']}: evidence coverage {scores['evidence_coverage_at_k']:.4f}")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    lock = args.run / '.lock'
    acquired = False
    try:
        with lock.open('x', encoding='utf-8') as handle:
            handle.write('report')
        acquired = True
        manifest = json.loads((args.run / 'manifest.json').read_text(encoding='utf-8'))
        files = manifest['contract']['files']
        current_paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/raw').glob('*.md')}
        expected_paths = {p for p in files if p.startswith('data/raw/')}
        if current_paths != expected_paths:
            raise ValueError('Corpus file list changed; start a new run')
        for path in [*sorted(expected_paths), 'METRICS.md']:
            actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            if files.get(path) != actual:
                raise ValueError(f'{path} changed since this run; start a new run')
        rows = manifest['dataset']
        observations = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(args.run.glob('record-*.json'))]
        documents = {d.doc_id: d.text for d in load_documents(ROOT / 'data/raw')}
        report = summarize(rows, observations, documents, manifest['contract']['k'])
        report['run_signature'] = manifest['signature']
        report['metrics_sha256'] = files['METRICS.md']
        report['scorer_sha256'] = hashlib.sha256((ROOT / 'src/evaluation/metrics.py').read_bytes()).hexdigest()
        atomic_json(args.run / 'evaluation.json', report)
        (args.run / 'report.md').write_text(render_markdown(report), encoding='utf-8')
        print(json.dumps({k: report[k] for k in ('requested', 'answerable_missing_retrieval', 'overall')}, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Report stopped: {exc}\n')
    finally:
        if acquired:
            lock.unlink()


if __name__ == '__main__':
    main()
