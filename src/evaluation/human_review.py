"""Export blind human labels and measure judge agreement without inventing labels."""
import argparse
import csv
import io
import json
from pathlib import Path
from statistics import mean

from src.evaluation.judge import load_capture, parse_verdict
from src.evaluation.run import atomic_json, digest


def select_sample(rows, observations, limit=15):
    if len(rows) != len(observations) or any(r['id'] != o['id'] for r, o in zip(rows, observations)):
        raise ValueError('Question and observation IDs must align')
    if type(limit) is not int or not 10 <= limit <= 15:
        raise ValueError('Human sample size must be 10 to 15')
    groups = {}
    for row, observation in zip(rows, observations):
        if (row['answerable'] and row['split'] == 'dev' and observation.get('status') == 'ok'
                and isinstance(observation.get('answer'), str) and observation['answer'].strip()):
            groups.setdefault(row['category'], []).append({'row': row, 'observation': observation})
    selected = []
    # Deterministic category round-robin chosen without access to judge scores.
    while len(selected) < limit and any(groups.values()):
        for category in sorted(groups):
            if groups[category] and len(selected) < limit:
                selected.append(groups[category].pop(0))
    if len(selected) < 10:
        raise ValueError('Need at least 10 successful answerable development answers')
    return selected


def export_packet(capture, output, limit=15):
    manifest, observations = load_capture(capture)
    items = select_sample(manifest['dataset'], observations, limit)
    payload = {'capture_signature': manifest['signature'], 'items': items}
    packet = {'version': 1, **payload, 'signature': digest(payload),
              'selection': 'Category round-robin from successful answerable dev records, independent of judge scores'}
    output.mkdir(parents=True, exist_ok=False)
    atomic_json(output / 'packet.json', packet)
    with (output / 'labels.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'correctness', 'faithfulness', 'notes'])
        writer.writeheader()
        writer.writerows({'id': item['row']['id']} for item in items)
    lines = ['# Blind answer review', '',
             'Fill labels.csv yourself before inspecting judge verdicts. No judge scores are included.', '',
             'Correctness: 1 fully correct, 0.5 partial/incomplete, 0 incorrect or unjustified refusal.',
             'Faithfulness: 1 every factual claim supported by retrieved text, 0 any unsupported claim.',
             'Plausible outside knowledge or invented examples still count as unsupported.',
             'A simple refusal contains no unsupported factual claims, but may be incorrect.', '',
             'Compare the generated answer with the reference for correctness and with the retrieved',
             'context for faithfulness. If a reference itself is flawed, record that in notes and',
             'resolve the benchmark issue before interpreting judge agreement. Do not fabricate labels.', '']
    for item in items:
        row, observation = item['row'], item['observation']
        lines += [f"## {row['id']} ({row['category']})", '', f"Question: {row['question']}", '',
                  f"Reference: {row['reference_answer']}", '', f"Generated answer: {observation['answer']}", '',
                  'Retrieved context:', '']
        for chunk in observation['chunks']:
            lines += [f"### {chunk['chunk_id']}", '', chunk['text'], '']
    (output / 'review.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()) + '\n', encoding='utf-8')
    return len(items)


def parse_labels(text, ids):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ['id', 'correctness', 'faithfulness', 'notes']:
        raise ValueError('Expected id,correctness,faithfulness,notes columns')
    labels = {}
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed CSV row')
        identifier = row['id']
        if identifier in labels or identifier not in ids:
            raise ValueError('Duplicate or unknown human label ID')
        if row['correctness'] not in {'0', '0.5', '1'} or row['faithfulness'] not in {'0', '1'}:
            raise ValueError('Human scores are blank or outside the required scales')
        labels[identifier] = {'correctness': float(row['correctness']), 'faithfulness': int(row['faithfulness'])}
    if set(labels) != set(ids):
        raise ValueError('Human labels must cover every selected answer')
    return labels


def compare_packet(packet_path, labels_path, judge_path):
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    payload = {key: packet[key] for key in ('capture_signature', 'items')}
    if digest(payload) != packet['signature']:
        raise ValueError('Human packet signature mismatch')
    items = packet['items']
    if not 10 <= len(items) <= 15 or len({i['row']['id'] for i in items}) != len(items):
        raise ValueError('Invalid human sample')
    labels = parse_labels(labels_path.read_text(encoding='utf-8-sig'), {i['row']['id'] for i in items})
    lock = judge_path / '.lock'
    with lock.open('x', encoding='utf-8') as handle:
        handle.write('agreement-reader')
    try:
        manifest = json.loads((judge_path / 'manifest.json').read_text(encoding='utf-8'))
        expected = digest({'rows': manifest['dataset'], 'observations': manifest['observations'], 'contract': manifest['contract']})
        if manifest['signature'] != expected or manifest['contract']['capture_signature'] != packet['capture_signature']:
            raise ValueError('Judge and human packet inputs differ')
        positions = {r['id']: index for index, r in enumerate(manifest['dataset'])}
        details = []
        for item in items:
            identifier = item['row']['id']
            if identifier not in positions:
                raise ValueError('Selected answer has no matching judge record')
            index = positions[identifier]
            if manifest['dataset'][index] != item['row'] or manifest['observations'][index] != item['observation']:
                raise ValueError('Human and judge answers differ')
            if not item['row']['answerable'] or item['row']['split'] != 'dev':
                raise ValueError('Agreement sample must contain answerable development records')
            result = json.loads((judge_path / f'verdict-{index:04}.json').read_text(encoding='utf-8'))
            if result['id'] != identifier or result['status'] != 'ok':
                raise ValueError('Judge verdict is missing or failed')
            verdict = parse_verdict(json.dumps(result['verdict']), True)
            details.append({'id': identifier, 'human': labels[identifier],
                            'judge': {key: verdict[key] for key in ('correctness', 'faithfulness')}})
        return {'sample_size': len(details), 'agreement_measured': True,
                'packet_signature': packet['signature'], 'judge_signature': manifest['signature'],
                'exact_agreement': {key: mean(d['human'][key] == d['judge'][key] for d in details)
                                    for key in ('correctness', 'faithfulness')},
                'disagreements': [d for d in details if d['human'] != d['judge']],
                'note': 'Small development calibration sample. Inspect disagreements before accepting the judge; no automatic approval threshold is inferred.'}
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    export = commands.add_parser('export')
    export.add_argument('--run', type=Path, required=True)
    export.add_argument('--output', type=Path, required=True)
    export.add_argument('--limit', type=int, default=15)
    compare = commands.add_parser('compare')
    compare.add_argument('--packet', type=Path, required=True)
    compare.add_argument('--labels', type=Path, required=True)
    compare.add_argument('--judge', type=Path, required=True)
    compare.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'export':
            count = export_packet(args.run, args.output, args.limit)
            print(f'Exported {count} blind review items. Human labels are intentionally blank.')
        else:
            if args.output.exists():
                raise ValueError('Output already exists')
            report = compare_packet(args.packet, args.labels, args.judge)
            atomic_json(args.output, report)
            print(json.dumps(report, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Human review stopped: {exc}\n')


if __name__ == '__main__':
    main()
