"""Build a deterministic answer-quality report from saved capture and judge outputs."""
import argparse
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean

from src.evaluation.human_review import compare_packet
from src.evaluation.judge import load_capture, parse_verdict
from src.evaluation.run import atomic_json, digest, file_digest


def latency_summary(values):
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) or value < 0 for value in values):
        raise ValueError('Invalid latency')
    return {'count': len(values), 'mean_s': mean(values) if values else None,
            'p95_s': sorted(values)[math.ceil(.95 * len(values)) - 1] if values else None}


def load_judge(directory, capture_manifest, observations):
    lock = directory / '.lock'
    with lock.open('x', encoding='utf-8') as handle:
        handle.write('answer-report-reader')
    try:
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        expected = digest({'rows': manifest['dataset'], 'observations': manifest['observations'],
                           'contract': manifest['contract']})
        if manifest.get('signature') != expected:
            raise ValueError('Judge manifest signature mismatch')
        if manifest['contract'].get('capture_signature') != capture_manifest['signature']:
            raise ValueError('Judge and capture signatures differ')
        if manifest['dataset'] != capture_manifest['dataset'] or manifest['observations'] != observations:
            raise ValueError('Judge and capture inputs differ')
        verdicts = []
        for index, row in enumerate(manifest['dataset']):
            result = json.loads((directory / f'verdict-{index:04}.json').read_text(encoding='utf-8'))
            if result.get('id') != row['id'] or result.get('status') != 'ok':
                raise ValueError('Judge verdict is missing or failed')
            result['verdict'] = parse_verdict(json.dumps(result['verdict']), row['answerable'])
            verdicts.append(result)
        return manifest, verdicts
    finally:
        lock.unlink()


def _score_summary(values, allowed):
    if any(value not in allowed for value in values):
        raise ValueError('Invalid answer-quality score')
    distribution = Counter(values)
    return {'count': len(values), 'score_sum': sum(values),
            'mean': mean(values) if values else None,
            'distribution': {str(value): distribution[value] for value in sorted(allowed)}}


def build_report(capture_manifest, observations, judge_manifest, verdicts, agreement):
    rows = capture_manifest['dataset']
    if capture_manifest['contract'].get('mode') != 'answers':
        raise ValueError('Answer report requires an answers-mode capture')
    if (len(rows) != len(observations) or len(rows) != len(verdicts)
            or len({row['id'] for row in rows}) != len(rows)):
        raise ValueError('Answer report inputs must align')
    if judge_manifest['contract'].get('capture_signature') != capture_manifest['signature']:
        raise ValueError('Judge and capture signatures differ')
    if agreement.get('judge_signature') != judge_manifest['signature'] or not agreement.get('agreement_measured'):
        raise ValueError('Human agreement does not match this judge run')

    correctness, faithfulness, abstention = [], [], []
    retrieval_times, generation_times, answer_times, judge_times = [], [], [], []
    questions = []
    for row, observation, judged in zip(rows, observations, verdicts):
        if row['id'] != observation.get('id') or row['id'] != judged.get('id'):
            raise ValueError('Answer report record IDs differ')
        if (observation.get('status') != 'ok' or not isinstance(observation.get('answer'), str)
                or not observation['answer'].strip() or not isinstance(observation.get('chunks'), list)):
            raise ValueError('Answer capture is incomplete')
        retrieval_s, generation_s, judge_s = (observation.get('retrieval_s'),
                                               observation.get('generation_s'), judged.get('judge_s'))
        latency_summary([retrieval_s, generation_s, judge_s])
        answer_s = retrieval_s + generation_s
        retrieval_times.append(retrieval_s)
        generation_times.append(generation_s)
        answer_times.append(answer_s)
        judge_times.append(judge_s)
        verdict = parse_verdict(json.dumps(judged['verdict']), row['answerable'])
        if row['answerable']:
            correctness.append(verdict['correctness'])
            faithfulness.append(verdict['faithfulness'])
        else:
            abstention.append(verdict['abstention'])
        questions.append({'id': row['id'], 'category': row['category'],
                          'answerable': row['answerable'], 'resumed': bool(observation.get('resumed')),
                          'scores': {key: verdict[key] for key in ('correctness', 'faithfulness', 'abstention')},
                          'latency_s': {'retrieval': retrieval_s, 'generation': generation_s,
                                        'answer_successful_stages': answer_s, 'judge': judge_s}})

    return {
        'report_version': 1,
        'status': 'provisional_development_result',
        'requested': len(rows),
        'completed': len(questions),
        'answerable_count': sum(row['answerable'] for row in rows),
        'unanswerable_count': sum(not row['answerable'] for row in rows),
        'capture': {'signature': capture_manifest['signature'],
                    'created_utc': capture_manifest.get('created_utc'),
                    'config': capture_manifest['contract'].get('config'),
                    'generator': capture_manifest['contract'].get('generator'),
                    'prompt_sha256': capture_manifest['contract'].get('prompt_sha256'),
                    'git_commit': capture_manifest['contract'].get('git_commit'),
                    'platform': capture_manifest['contract'].get('platform')},
        'judge': {'signature': judge_manifest['signature'],
                  'created_utc': judge_manifest.get('created_utc'),
                  **judge_manifest['contract']['judge'],
                  'prompt_sha256': judge_manifest['contract'].get('prompt_sha256')},
        'human_calibration': {'sample_size': agreement['sample_size'],
                              'exact_agreement': agreement['exact_agreement'],
                              'disagreement_count': len(agreement['disagreements']),
                              'abstention_human_validated': False},
        'answer_quality': {
            'correctness': _score_summary(correctness, {0, .5, 1}),
            'faithfulness': _score_summary(faithfulness, {0, 1}),
            'abstention': _score_summary(abstention, {0, 1})},
        'latency': {
            'retrieval': latency_summary(retrieval_times),
            'generation': latency_summary(generation_times),
            'answer_successful_stages': latency_summary(answer_times),
            'judge_excluded_from_answer_latency': latency_summary(judge_times),
            'resumed_question_count': sum(1 for observation in observations if observation.get('resumed'))},
        'questions': questions,
        'limitations': [
            'Draft development sample of 15 questions; the reserved test split was not used.',
            'Judge scores are provisional: correctness agreement was measured on 14 answers, '
            'faithfulness agreement was 78.6%, and abstention has no human calibration.',
            'The historical capture uses configuration A, not the selected configuration B.',
            'Successful-stage answer latency is retrieval plus successful generation; scheduling '
            'delays, judge time, model preload and failed-attempt time are excluded.',
            'Four resumed questions are identified, but total retry cost cannot be reconstructed '
            'from the saved historical checkpoints.']}


def render_markdown(report):
    quality, latency, calibration = report['answer_quality'], report['latency'], report['human_calibration']
    lines = [
        '# Provisional answer-quality report', '',
        f"Configuration {report['capture']['config']}; {report['completed']}/{report['requested']} saved answers scored.",
        f"Generator: `{report['capture']['generator']['provider']} / {report['capture']['generator']['model']}`.",
        f"Judge: `{report['judge']['provider']} / {report['judge']['model']}`.", '',
        '## Answer quality', '',
        '| Metric | Result |', '|---|---:|',
        f"| Correctness | {quality['correctness']['score_sum']:g}/{quality['correctness']['count']} "
        f"({quality['correctness']['mean']:.1%}) |",
        f"| Faithfulness | {quality['faithfulness']['score_sum']:g}/{quality['faithfulness']['count']} "
        f"({quality['faithfulness']['mean']:.1%}) |",
        f"| Abstention | {quality['abstention']['score_sum']:g}/{quality['abstention']['count']} "
        f"({quality['abstention']['mean']:.1%}) |", '',
        'These are provisional judge scores, not general RAG accuracy.', '',
        '## Human calibration', '',
        f"Blind exact agreement on {calibration['sample_size']} answerable outputs: correctness "
        f"{calibration['exact_agreement']['correctness']:.1%}; faithfulness "
        f"{calibration['exact_agreement']['faithfulness']:.1%}. Abstention was not human-calibrated.", '',
        '## Latency', '',
        '| Stage | Count | Mean | Nearest-rank P95 |', '|---|---:|---:|---:|']
    for label, key in [('Retrieval', 'retrieval'), ('Generation', 'generation'),
                       ('Answer: successful stages', 'answer_successful_stages'),
                       ('Judge (excluded)', 'judge_excluded_from_answer_latency')]:
        item = latency[key]
        lines.append(f"| {label} | {item['count']} | {item['mean_s']:.4f} s | {item['p95_s']:.4f} s |")
    lines += ['', f"Resumed questions: {latency['resumed_question_count']}.", '',
              '## Per-question scores', '',
              '| ID | Category | Answerable | Correctness | Faithfulness | Abstention | Resumed |',
              '|---|---|---:|---:|---:|---:|---:|']
    for question in report['questions']:
        scores = question['scores']
        show = lambda value: '—' if value is None else f'{value:g}'
        lines.append(f"| {question['id']} | {question['category']} | "
                     f"{'yes' if question['answerable'] else 'no'} | "
                     f"{show(scores['correctness'])} | {show(scores['faithfulness'])} | "
                     f"{show(scores['abstention'])} | {'yes' if question['resumed'] else 'no'} |")
    lines += ['', '## Limitations', ''] + [f'- {item}' for item in report['limitations']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--judge', type=Path, required=True)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--agreement', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Output directory already exists')
        capture, observations = load_capture(args.run)
        judge, verdicts = load_judge(args.judge, capture, observations)
        agreement = compare_packet(args.packet, args.labels, args.judge)
        saved_agreement = json.loads(args.agreement.read_text(encoding='utf-8'))
        if saved_agreement != agreement:
            raise ValueError('Versioned agreement differs from recomputed agreement')
        report = build_report(capture, observations, judge, verdicts, agreement)
        report['provenance'] = {'metrics_sha256': file_digest('METRICS.md'),
                                'reporter_sha256': file_digest(Path(__file__))}
        args.output.mkdir(parents=True)
        atomic_json(args.output / 'evaluation.json', report)
        (args.output / 'report.md').write_text(render_markdown(report), encoding='utf-8')
        print(json.dumps({'answer_quality': report['answer_quality'],
                          'human_calibration': report['human_calibration'],
                          'latency': report['latency']}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'Answer report stopped: {exc}\n')


if __name__ == '__main__':
    main()
