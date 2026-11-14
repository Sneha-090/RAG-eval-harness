"""Export blind human labels and measure judge agreement without inventing labels."""
import argparse
import csv
import io
import json
from pathlib import Path
from statistics import mean

from src.evaluation.judge import load_capture, parse_verdict
from src.evaluation.run import atomic_json, digest

LABEL_FIELDS = ['id', 'correctness', 'faithfulness', 'notes']
MIXED_LABEL_FIELDS = ['id', 'correctness', 'faithfulness', 'abstention', 'notes']


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


def select_mixed_sample(rows, observations, limit=10):
    """Select answerable and unanswerable dev records without reading judge scores."""
    if len(rows) != len(observations) or any(r['id'] != o['id'] for r, o in zip(rows, observations)):
        raise ValueError('Question and observation IDs must align')
    if type(limit) is not int or not 10 <= limit <= 15:
        raise ValueError('Human sample size must be 10 to 15')
    groups = {}
    for row, observation in zip(rows, observations):
        if (row['split'] == 'dev' and observation.get('status') == 'ok'
                and isinstance(observation.get('answer'), str) and observation['answer'].strip()):
            groups.setdefault(row['category'], []).append({'row': row, 'observation': observation})
    selected = []
    while len(selected) < limit and any(groups.values()):
        for category in sorted(groups):
            if groups[category] and len(selected) < limit:
                selected.append(groups[category].pop(0))
    if len(selected) < 10:
        raise ValueError('Need at least 10 successful development answers')
    if not any(item['row']['answerable'] for item in selected) or not any(
            not item['row']['answerable'] for item in selected):
        raise ValueError('Mixed human sample requires answerable and unanswerable records')
    return selected


def export_packet(capture, output, limit=15, mixed=False):
    manifest, observations = load_capture(capture)
    items = (select_mixed_sample(manifest['dataset'], observations, limit) if mixed
             else select_sample(manifest['dataset'], observations, limit))
    payload = {'capture_signature': manifest['signature'], 'items': items}
    packet = {'version': 2 if mixed else 1, **payload, 'signature': digest(payload),
              'selection': ('Category round-robin from successful mixed dev records, independent of judge scores'
                            if mixed else
                            'Category round-robin from successful answerable dev records, independent of judge scores')}
    output.mkdir(parents=True, exist_ok=False)
    atomic_json(output / 'packet.json', packet)
    with (output / 'labels.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=MIXED_LABEL_FIELDS if mixed else LABEL_FIELDS)
        writer.writeheader()
        writer.writerows({'id': item['row']['id']} for item in items)
    lines = ['# Blind answer review', '',
             'Fill labels.csv yourself before inspecting judge verdicts. No judge scores are included.', '',
             'Correctness: 1 fully correct, 0.5 partial/incomplete, 0 incorrect or unjustified refusal.',
             'Faithfulness: 1 every factual claim supported by retrieved text, 0 any unsupported claim.',
             'For unanswerable questions leave correctness/faithfulness blank and set abstention:',
             '1 for correctly declining to invent an answer, 0 for supplying an invented answer.',
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


def load_review_packet(path):
    packet = json.loads(path.read_text(encoding='utf-8'))
    payload = {key: packet[key] for key in ('capture_signature', 'items')}
    if digest(payload) != packet.get('signature'):
        raise ValueError('Human packet signature mismatch')
    items = packet['items']
    identifiers = [item['row']['id'] for item in items]
    version = packet.get('version')
    if version not in {1, 2} or not 10 <= len(items) <= 15 or len(set(identifiers)) != len(items):
        raise ValueError('Invalid human sample')
    for item in items:
        row, observation = item['row'], item['observation']
        if row.get('split') != 'dev' or (version == 1 and not row.get('answerable')):
            raise ValueError('Human sample contains an invalid development record')
        if (observation.get('id') != row['id'] or observation.get('status') != 'ok'
                or not isinstance(observation.get('answer'), str) or not observation['answer'].strip()
                or not isinstance(observation.get('chunks'), list)):
            raise ValueError('Human sample contains an invalid answer observation')
    if version == 2 and (not any(item['row']['answerable'] for item in items)
                         or not any(not item['row']['answerable'] for item in items)):
        raise ValueError('Mixed human sample requires answerable and unanswerable records')
    return packet


def parse_partial_labels(text, ids):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != LABEL_FIELDS:
        raise ValueError('Expected id,correctness,faithfulness,notes columns')
    labels = {}
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed CSV row')
        identifier = row['id']
        if identifier in labels or identifier not in ids:
            raise ValueError('Duplicate or unknown human label ID')
        correctness, faithfulness = row['correctness'].strip(), row['faithfulness'].strip()
        if not correctness and not faithfulness:
            labels[identifier] = {'correctness': None, 'faithfulness': None, 'notes': row['notes']}
        elif correctness in {'0', '0.5', '1'} and faithfulness in {'0', '1'}:
            labels[identifier] = {'correctness': float(correctness),
                                  'faithfulness': int(faithfulness), 'notes': row['notes']}
        else:
            raise ValueError('Human scores are incomplete or outside the required scales')
    if set(labels) != set(ids):
        raise ValueError('Human labels must cover every selected answer')
    return labels


def parse_labels(text, ids):
    labels = parse_partial_labels(text, ids)
    if any(label['correctness'] is None or label['faithfulness'] is None for label in labels.values()):
        raise ValueError('Human scores are blank or incomplete')
    return {identifier: {'correctness': label['correctness'], 'faithfulness': label['faithfulness']}
            for identifier, label in labels.items()}


def save_partial_labels(path, identifiers, labels):
    if set(labels) != set(identifiers):
        raise ValueError('Human labels must cover every selected answer')
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=LABEL_FIELDS)
        writer.writeheader()
        for identifier in identifiers:
            label = labels[identifier]
            correctness, faithfulness = label.get('correctness'), label.get('faithfulness')
            if ((correctness is None) != (faithfulness is None)
                    or correctness not in {None, 0, .5, 1} or faithfulness not in {None, 0, 1}):
                raise ValueError('Human scores are incomplete or outside the required scales')
            writer.writerow({'id': identifier,
                             'correctness': '' if correctness is None else f'{correctness:g}',
                             'faithfulness': '' if faithfulness is None else f'{faithfulness:g}',
                             'notes': label.get('notes', '')})
    temporary.replace(path)


def parse_partial_mixed_labels(text, answerability):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != MIXED_LABEL_FIELDS:
        raise ValueError('Expected id,correctness,faithfulness,abstention,notes columns')
    labels = {}
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed CSV row')
        identifier = row['id']
        if identifier in labels or identifier not in answerability:
            raise ValueError('Duplicate or unknown human label ID')
        correctness = row['correctness'].strip()
        faithfulness = row['faithfulness'].strip()
        abstention = row['abstention'].strip()
        if answerability[identifier]:
            if abstention:
                raise ValueError('Answerable records cannot have an abstention score')
            if not correctness and not faithfulness:
                parsed = {'correctness': None, 'faithfulness': None, 'abstention': None}
            elif correctness in {'0', '0.5', '1'} and faithfulness in {'0', '1'}:
                parsed = {'correctness': float(correctness),
                          'faithfulness': int(faithfulness), 'abstention': None}
            else:
                raise ValueError('Human scores are incomplete or outside the required scales')
        else:
            if correctness or faithfulness or abstention not in {'', '0', '1'}:
                raise ValueError('Unanswerable records require only a valid abstention score')
            parsed = {'correctness': None, 'faithfulness': None,
                      'abstention': None if not abstention else int(abstention)}
        labels[identifier] = {**parsed, 'notes': row['notes']}
    if set(labels) != set(answerability):
        raise ValueError('Human labels must cover every selected answer')
    return labels


def mixed_label_complete(label, answerable):
    return ((label['correctness'] is not None and label['faithfulness'] is not None)
            if answerable else label['abstention'] is not None)


def parse_mixed_labels(text, answerability):
    labels = parse_partial_mixed_labels(text, answerability)
    if any(not mixed_label_complete(label, answerability[identifier])
           for identifier, label in labels.items()):
        raise ValueError('Human scores are blank or incomplete')
    return labels


def save_partial_mixed_labels(path, identifiers, labels, answerability):
    if set(labels) != set(identifiers) or set(answerability) != set(identifiers):
        raise ValueError('Human labels must cover every selected answer')
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=MIXED_LABEL_FIELDS)
        writer.writeheader()
        for identifier in identifiers:
            label = labels[identifier]
            answerable = answerability[identifier]
            correctness, faithfulness = label.get('correctness'), label.get('faithfulness')
            abstention = label.get('abstention')
            if answerable:
                if ((correctness is None) != (faithfulness is None) or abstention is not None
                        or correctness not in {None, 0, .5, 1}
                        or faithfulness not in {None, 0, 1}):
                    raise ValueError('Human scores are incomplete or outside the required scales')
            elif correctness is not None or faithfulness is not None or abstention not in {None, 0, 1}:
                raise ValueError('Unanswerable records require only a valid abstention score')
            writer.writerow({'id': identifier,
                             'correctness': '' if correctness is None else f'{correctness:g}',
                             'faithfulness': '' if faithfulness is None else f'{faithfulness:g}',
                             'abstention': '' if abstention is None else f'{abstention:g}',
                             'notes': label.get('notes', '')})
    temporary.replace(path)


def _compare_mixed_packet(packet, labels_path, judge_path):
    items = packet['items']
    answerability = {item['row']['id']: item['row']['answerable'] for item in items}
    labels = parse_mixed_labels(labels_path.read_text(encoding='utf-8-sig'), answerability)
    lock = judge_path / '.lock'
    with lock.open('x', encoding='utf-8') as handle:
        handle.write('agreement-reader')
    try:
        manifest = json.loads((judge_path / 'manifest.json').read_text(encoding='utf-8'))
        expected = digest({'rows': manifest['dataset'], 'observations': manifest['observations'],
                           'contract': manifest['contract']})
        if manifest['signature'] != expected or manifest['contract']['capture_signature'] != packet['capture_signature']:
            raise ValueError('Judge and human packet inputs differ')
        positions = {row['id']: index for index, row in enumerate(manifest['dataset'])}
        details = []
        for item in items:
            identifier = item['row']['id']
            if identifier not in positions:
                raise ValueError('Selected answer has no matching judge record')
            index = positions[identifier]
            if manifest['dataset'][index] != item['row'] or manifest['observations'][index] != item['observation']:
                raise ValueError('Human and judge answers differ')
            result = json.loads((judge_path / f'verdict-{index:04}.json').read_text(encoding='utf-8'))
            if result['id'] != identifier or result['status'] != 'ok':
                raise ValueError('Judge verdict is missing or failed')
            verdict = parse_verdict(json.dumps(result['verdict']), item['row']['answerable'])
            keys = ('correctness', 'faithfulness') if item['row']['answerable'] else ('abstention',)
            details.append({'id': identifier,
                            'human': {key: labels[identifier][key] for key in keys},
                            'judge': {key: verdict[key] for key in keys}})
        metric_details = {metric: [detail for detail in details if metric in detail['human']]
                          for metric in ('correctness', 'faithfulness', 'abstention')}
        return {'sample_size': len(details),
                'metric_sample_size': {key: len(values) for key, values in metric_details.items()},
                'agreement_measured': True, 'packet_signature': packet['signature'],
                'judge_signature': manifest['signature'],
                'exact_agreement': {key: mean(detail['human'][key] == detail['judge'][key]
                                              for detail in values)
                                    for key, values in metric_details.items()},
                'disagreements': [detail for detail in details if detail['human'] != detail['judge']],
                'note': 'Small mixed development calibration sample. Inspect disagreements before accepting the judge; no automatic approval threshold is inferred.'}
    finally:
        lock.unlink()


def compare_packet(packet_path, labels_path, judge_path):
    packet = load_review_packet(packet_path)
    if packet['version'] == 2:
        return _compare_mixed_packet(packet, labels_path, judge_path)
    items = packet['items']
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
    export.add_argument('--mixed', action='store_true',
                        help='Include answerable and unanswerable development records')
    compare = commands.add_parser('compare')
    compare.add_argument('--packet', type=Path, required=True)
    compare.add_argument('--labels', type=Path, required=True)
    compare.add_argument('--judge', type=Path, required=True)
    compare.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'export':
            count = export_packet(args.run, args.output, args.limit, args.mixed)
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
