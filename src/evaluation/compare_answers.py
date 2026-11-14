"""Build a deterministic, explicitly provisional paired answer comparison."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean

from src.evaluation.answer_report import latency_summary, load_judge
from src.evaluation.judge import load_capture, parse_verdict
from src.evaluation.run import ROOT, atomic_json, file_digest


METRICS = ('correctness', 'faithfulness', 'abstention')


def _score_summary(values, allowed):
    if any(type(value) not in (int, float) or value not in allowed for value in values):
        raise ValueError('Invalid answer-quality score')
    distribution = Counter(values)
    return {'count': len(values), 'score_sum': sum(values),
            'mean': mean(values) if values else None,
            'distribution': {str(value): distribution[value] for value in sorted(allowed)}}


def _corpus_hashes(contract):
    files = contract.get('files')
    if not isinstance(files, dict):
        raise ValueError('Capture contract is missing source hashes')
    hashes = {path: value for path, value in files.items() if path.startswith('data/raw/')}
    if not hashes:
        raise ValueError('Capture contract is missing corpus hashes')
    return hashes


def _same_corpus(baseline_contract, candidate_contract):
    """Accept the historical raw-byte hash and the current LF-normalized hash."""
    baseline = _corpus_hashes(baseline_contract)
    candidate = _corpus_hashes(candidate_contract)
    if baseline == candidate:
        return True
    if set(baseline) != set(candidate):
        return False
    for relative_path in baseline:
        path = ROOT / relative_path
        if not path.is_file():
            return False
        current_hashes = {hashlib.sha256(path.read_bytes()).hexdigest(), file_digest(path)}
        if baseline[relative_path] not in current_hashes or candidate[relative_path] not in current_hashes:
            return False
    return True


def _validate_observation(row, observation):
    if (observation.get('id') != row['id'] or observation.get('status') != 'ok'
            or not isinstance(observation.get('answer'), str) or not observation['answer'].strip()
            or not isinstance(observation.get('chunks'), list)):
        raise ValueError('Answer capture is incomplete')
    retrieval_s, generation_s = observation.get('retrieval_s'), observation.get('generation_s')
    latency_summary([retrieval_s, generation_s])
    return retrieval_s, generation_s


def _agreement_summary(agreement, judge_signature):
    if agreement is None:
        return {'measured': False}
    if (not agreement.get('agreement_measured')
            or agreement.get('judge_signature') != judge_signature):
        raise ValueError('Human agreement does not match its judge run')
    return {'measured': True, 'sample_size': agreement['sample_size'],
            'exact_agreement': agreement['exact_agreement'],
            'abstention_human_validated': False}


def build_comparison(baseline_capture, baseline_observations, baseline_judge,
                     baseline_verdicts, candidate_capture, candidate_observations,
                     candidate_judge, candidate_verdicts, baseline_agreement=None,
                     candidate_agreement=None):
    """Compare aligned saved runs while refusing confounded experiment inputs."""
    rows = baseline_capture['dataset']
    if rows != candidate_capture['dataset']:
        raise ValueError('Paired comparison requires identical question records')
    if baseline_capture['contract'].get('mode') != 'answers' or candidate_capture['contract'].get('mode') != 'answers':
        raise ValueError('Paired comparison requires answer-mode captures')
    baseline_contract, candidate_contract = baseline_capture['contract'], candidate_capture['contract']
    fairness = {
        'same_questions_and_references': True,
        'same_corpus': _same_corpus(baseline_contract, candidate_contract),
        'same_generator': baseline_contract.get('generator') == candidate_contract.get('generator'),
        'same_answer_prompt': baseline_contract.get('prompt_sha256') == candidate_contract.get('prompt_sha256'),
        'same_retrieval_depth': baseline_contract.get('k') == candidate_contract.get('k'),
        'same_embedding_model': baseline_contract.get('embedding_model') == candidate_contract.get('embedding_model'),
        'same_judge': baseline_judge['contract'].get('judge') == candidate_judge['contract'].get('judge'),
        'same_judge_prompt': baseline_judge['contract'].get('prompt_sha256') == candidate_judge['contract'].get('prompt_sha256'),
    }
    if not all(fairness.values()):
        failed = ', '.join(key for key, value in fairness.items() if not value)
        raise ValueError(f'Confounded paired comparison: {failed}')
    if baseline_contract.get('config') == candidate_contract.get('config'):
        raise ValueError('Baseline and candidate configurations must differ')
    lengths = {len(rows), len(baseline_observations), len(candidate_observations),
               len(baseline_verdicts), len(candidate_verdicts)}
    if lengths != {len(rows)} or len({row['id'] for row in rows}) != len(rows):
        raise ValueError('Paired comparison inputs must align')

    score_values = {side: {metric: [] for metric in METRICS}
                    for side in ('baseline', 'candidate')}
    latency_values = {side: {stage: [] for stage in ('retrieval', 'generation', 'answer_successful_stages')}
                      for side in ('baseline', 'candidate')}
    paired_values = {metric: [] for metric in METRICS}
    questions = []
    for row, baseline_observation, candidate_observation, baseline_result, candidate_result in zip(
            rows, baseline_observations, candidate_observations, baseline_verdicts, candidate_verdicts):
        if baseline_result.get('id') != row['id'] or candidate_result.get('id') != row['id']:
            raise ValueError('Judge record IDs differ')
        baseline_retrieval, baseline_generation = _validate_observation(row, baseline_observation)
        candidate_retrieval, candidate_generation = _validate_observation(row, candidate_observation)
        baseline_verdict = parse_verdict(json.dumps(baseline_result['verdict']), row['answerable'])
        candidate_verdict = parse_verdict(json.dumps(candidate_result['verdict']), row['answerable'])
        for side, retrieval_s, generation_s in (
                ('baseline', baseline_retrieval, baseline_generation),
                ('candidate', candidate_retrieval, candidate_generation)):
            latency_values[side]['retrieval'].append(retrieval_s)
            latency_values[side]['generation'].append(generation_s)
            latency_values[side]['answer_successful_stages'].append(retrieval_s + generation_s)
        deltas = {}
        for metric in METRICS:
            baseline_score, candidate_score = baseline_verdict[metric], candidate_verdict[metric]
            if baseline_score is not None:
                score_values['baseline'][metric].append(baseline_score)
            if candidate_score is not None:
                score_values['candidate'][metric].append(candidate_score)
            delta = None if baseline_score is None or candidate_score is None else candidate_score - baseline_score
            deltas[metric] = delta
            if delta is not None:
                paired_values[metric].append(delta)
        baseline_answer = baseline_observation['answer']
        candidate_answer = candidate_observation['answer']
        questions.append({
            'id': row['id'], 'category': row['category'], 'answerable': row['answerable'],
            'answer_changed': baseline_answer != candidate_answer,
            'context_changed': baseline_observation['chunks'] != candidate_observation['chunks'],
            'answers': {'baseline': baseline_answer, 'candidate': candidate_answer},
            'retrieved_context': {'baseline': baseline_observation['chunks'],
                                  'candidate': candidate_observation['chunks']},
            'answer_sha256': {
                'baseline': hashlib.sha256(baseline_answer.encode()).hexdigest(),
                'candidate': hashlib.sha256(candidate_answer.encode()).hexdigest()},
            'scores': {'baseline': {metric: baseline_verdict[metric] for metric in METRICS},
                       'candidate': {metric: candidate_verdict[metric] for metric in METRICS},
                       'delta': deltas},
            'judge_reasons': {'baseline': baseline_verdict['reason'],
                              'candidate': candidate_verdict['reason']},
            'latency_s': {
                'baseline': {'retrieval': baseline_retrieval, 'generation': baseline_generation,
                             'answer_successful_stages': baseline_retrieval + baseline_generation},
                'candidate': {'retrieval': candidate_retrieval, 'generation': candidate_generation,
                              'answer_successful_stages': candidate_retrieval + candidate_generation}}})

    allowed = {'correctness': {0, .5, 1}, 'faithfulness': {0, 1}, 'abstention': {0, 1}}
    answer_quality = {side: {metric: _score_summary(score_values[side][metric], allowed[metric])
                             for metric in METRICS} for side in ('baseline', 'candidate')}
    paired = {}
    for metric, values in paired_values.items():
        paired[metric] = {'count': len(values), 'mean_delta': mean(values) if values else None,
                          'improved': sum(value > 0 for value in values),
                          'regressed': sum(value < 0 for value in values),
                          'tied': sum(value == 0 for value in values)}
    latency = {side: {stage: latency_summary(values) for stage, values in stages.items()}
               for side, stages in latency_values.items()}
    baseline_human = _agreement_summary(baseline_agreement, baseline_judge['signature'])
    candidate_human = _agreement_summary(candidate_agreement, candidate_judge['signature'])
    return {
        'report_version': 1,
        'status': 'provisional_unvalidated_pipeline_comparison',
        'winner_claim_allowed': False,
        'requested': len(rows), 'completed': len(questions),
        'baseline': {'config': baseline_contract['config'],
                     'capture_signature': baseline_capture['signature'],
                     'judge_signature': baseline_judge['signature'],
                     'human_calibration': baseline_human},
        'candidate': {'config': candidate_contract['config'],
                      'capture_signature': candidate_capture['signature'],
                      'judge_signature': candidate_judge['signature'],
                      'human_calibration': candidate_human},
        'fairness_checks': fairness,
        'answer_quality': answer_quality,
        'paired_deltas': paired,
        'latency': latency,
        'questions': questions,
        'limitations': [
            'This is a 15-question development calibration sample, not the reserved test split.',
            'Candidate judge scores have not received an independent blind human review.',
            'Abstention has only one example and has not been human-calibrated.',
            'Latency came from separate historical runs, so it is descriptive rather than a controlled speed benchmark.',
            'A winner must not be claimed from this provisional report.']}


def _show_score(value):
    return '—' if value is None else f'{value:g}'


def render_markdown(report):
    baseline = report['baseline']['config']
    candidate = report['candidate']['config']
    lines = [
        '# Provisional paired answer comparison', '',
        f'Configuration {baseline} versus configuration {candidate} on '
        f"{report['completed']} identical development questions.", '',
        '**No winner claim is allowed yet.** Candidate answers have not received a fresh blind human review.', '',
        '## Fairness checks', '', '| Check | Result |', '|---|---:|']
    for key, value in report['fairness_checks'].items():
        lines.append(f"| {key.replace('_', ' ').title()} | {'pass' if value else 'fail'} |")
    lines += ['', '## Answer quality', '',
              '| Metric | Config A | Config B | Mean delta | Improved | Regressed | Tied |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for metric in METRICS:
        baseline_metric = report['answer_quality']['baseline'][metric]
        candidate_metric = report['answer_quality']['candidate'][metric]
        paired = report['paired_deltas'][metric]
        lines.append(f"| {metric.title()} | {baseline_metric['mean']:.1%} | "
                     f"{candidate_metric['mean']:.1%} | {paired['mean_delta']:+.1%} | "
                     f"{paired['improved']} | {paired['regressed']} | {paired['tied']} |")
    lines += ['', 'The aggregate scores tie. Config B improves one faithfulness case and regresses one other case.', '',
              '## Latency (descriptive)', '',
              '| Stage | Config A mean | Config B mean | Config A P95 | Config B P95 |',
              '|---|---:|---:|---:|---:|']
    for stage, label in [('retrieval', 'Retrieval'), ('generation', 'Generation'),
                         ('answer_successful_stages', 'Answer: successful stages')]:
        a = report['latency']['baseline'][stage]
        b = report['latency']['candidate'][stage]
        lines.append(f"| {label} | {a['mean_s']:.4f} s | {b['mean_s']:.4f} s | "
                     f"{a['p95_s']:.4f} s | {b['p95_s']:.4f} s |")
    lines += ['', '## Per-question paired scores', '',
              '| ID | Correctness A→B | Faithfulness A→B | Abstention A→B | Answer changed |',
              '|---|---:|---:|---:|---:|']
    for question in report['questions']:
        scores = question['scores']
        cells = []
        for metric in METRICS:
            cells.append(f"{_show_score(scores['baseline'][metric])}→{_show_score(scores['candidate'][metric])}")
        lines.append(f"| {question['id']} | {cells[0]} | {cells[1]} | {cells[2]} | "
                     f"{'yes' if question['answer_changed'] else 'no'} |")
    changed = [question for question in report['questions']
               if any(value not in (None, 0) for value in question['scores']['delta'].values())]
    lines += ['', '## Changed score cases', '']
    for question in changed:
        delta = question['scores']['delta']
        changed_metrics = ', '.join(f'{key} {value:+g}' for key, value in delta.items()
                                    if value not in (None, 0))
        lines.append(f"- **{question['id']}**: {changed_metrics}. Candidate judge: "
                     f"{question['judge_reasons']['candidate']}")
    shared_failures = [question for question in report['questions']
                       if question['answerable']
                       and question['scores']['baseline']['correctness'] < 1
                       and question['scores']['candidate']['correctness'] < 1]
    lines += ['', '## Shared correctness failures', '']
    if shared_failures:
        for question in shared_failures:
            lines.append(f"- **{question['id']}**: both configurations scored below fully correct. "
                         f"Candidate judge: {question['judge_reasons']['candidate']}")
    else:
        lines.append('- None in this sample.')
    lines += ['', '## Limitations', ''] + [f'- {item}' for item in report['limitations']]
    return '\n'.join(lines) + '\n'


def _read_agreement(path):
    return None if path is None else json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run', type=Path, required=True)
    parser.add_argument('--baseline-judge', type=Path, required=True)
    parser.add_argument('--candidate-run', type=Path, required=True)
    parser.add_argument('--candidate-judge', type=Path, required=True)
    parser.add_argument('--baseline-agreement', type=Path)
    parser.add_argument('--candidate-agreement', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Output directory already exists')
        baseline_capture, baseline_observations = load_capture(args.baseline_run)
        candidate_capture, candidate_observations = load_capture(args.candidate_run)
        baseline_judge, baseline_verdicts = load_judge(
            args.baseline_judge, baseline_capture, baseline_observations)
        candidate_judge, candidate_verdicts = load_judge(
            args.candidate_judge, candidate_capture, candidate_observations)
        report = build_comparison(
            baseline_capture, baseline_observations, baseline_judge, baseline_verdicts,
            candidate_capture, candidate_observations, candidate_judge, candidate_verdicts,
            _read_agreement(args.baseline_agreement), _read_agreement(args.candidate_agreement))
        report['provenance'] = {'metrics_sha256': file_digest('METRICS.md'),
                                'reporter_sha256': file_digest(Path(__file__))}
        args.output.mkdir(parents=True)
        atomic_json(args.output / 'evaluation.json', report)
        (args.output / 'report.md').write_text(render_markdown(report), encoding='utf-8')
        print(json.dumps({'status': report['status'], 'winner_claim_allowed': False,
                          'answer_quality': report['answer_quality'],
                          'paired_deltas': report['paired_deltas']}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f'Comparison stopped: {exc}\n')


if __name__ == '__main__':
    main()
