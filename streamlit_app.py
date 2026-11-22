"""Guided blind human review for captured RAG answers."""
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.evaluation.human_review import (load_review_packet, mixed_label_complete,
                                         parse_partial_labels, parse_partial_mixed_labels,
                                         save_partial_labels, save_partial_mixed_labels)

ROOT = Path(__file__).resolve().parent
PACKET_PATH = Path(os.getenv('RAG_REVIEW_PACKET', ROOT / 'calibration/2026-11-14/packet.json'))
LABELS_PATH = Path(os.getenv('RAG_REVIEW_LABELS', ROOT / 'calibration/2026-11-14/labels.csv'))
CORRECTNESS_LABELS = {1.0: 'Correct', .5: 'Partly correct', 0.0: 'Wrong'}
FAITHFULNESS_LABELS = {1: 'Fully supported', 0: 'Has an unsupported claim'}
ABSTENTION_LABELS = {1: 'Correctly refused', 0: 'Invented an answer'}
FINAL_REPORT = ROOT / 'reports/final-test-v1-2026-11-22/evaluation.json'
FINAL_RETRIEVAL = ROOT / 'reports/final-test-v1-2026-11-22/retrieval.json'
CONFIG_COMPARISON = ROOT / 'reports/four-config-dev-2026-11-12/comparison.json'
DJANGO_COMPARISON = ROOT / 'reports/four-config-django-v2-dev-2026-11-22/comparison.json'
CALIBRATION_RESULT = ROOT / 'calibration/2026-11-14/agreement.json'


def save_review(identifier, identifiers, answerability, mixed):
    try:
        text = LABELS_PATH.read_text(encoding='utf-8-sig')
        latest = (parse_partial_mixed_labels(text, answerability) if mixed
                  else parse_partial_labels(text, set(identifiers)))
        notes = st.session_state[f'notes_{identifier}'].strip()
        if answerability[identifier]:
            correctness = st.session_state[f'correctness_{identifier}']
            faithfulness = st.session_state[f'faithfulness_{identifier}']
            if correctness not in CORRECTNESS_LABELS or faithfulness not in FAITHFULNESS_LABELS:
                raise ValueError('Choose one correctness option and one support option before saving.')
            latest[identifier] = {'correctness': correctness, 'faithfulness': faithfulness,
                                  'abstention': None, 'notes': notes}
        else:
            abstention = st.session_state[f'abstention_{identifier}']
            if abstention not in ABSTENTION_LABELS:
                raise ValueError('Choose whether the answer correctly refused or invented an answer.')
            latest[identifier] = {'correctness': None, 'faithfulness': None,
                                  'abstention': abstention, 'notes': notes}
        if mixed:
            save_partial_mixed_labels(LABELS_PATH, identifiers, latest, answerability)
        else:
            save_partial_labels(LABELS_PATH, identifiers, latest)
        remaining = [item_id for item_id in identifiers
                     if item_id != identifier and not mixed_label_complete(
                         latest[item_id], answerability[item_id])]
        st.session_state['review_item'] = remaining[0] if remaining else identifier
        st.session_state['_review_flash'] = f'Saved {identifier}.'
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.session_state['_review_error'] = str(exc)


@st.cache_data
def load_json(path):
    """Load one versioned report without repeating disk work on reruns."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def percent(value):
    return f'{value:.1%}'


def question_rows(answer_report, retrieval_report):
    retrieval_by_id = {item['id']: item for item in retrieval_report['questions']}
    rows = []
    for item in answer_report['questions']:
        retrieval = retrieval_by_id[item['id']]
        scores = item['scores']
        retrieval_scores = retrieval['scores'] or {}
        if not item['answerable']:
            outcome = 'Correct abstention' if scores['abstention'] == 1 else 'Invented answer'
        elif scores['correctness'] != 1:
            outcome = 'Over-abstained / incorrect'
        elif scores['faithfulness'] != 1:
            outcome = 'Unsupported detail'
        else:
            outcome = 'Pass'
        rows.append({
            'ID': item['id'],
            'Category': item['category'].replace('_', ' '),
            'Outcome': outcome,
            'Correctness': scores['correctness'],
            'Faithfulness': scores['faithfulness'],
            'Abstention': scores['abstention'],
            'Page hit': retrieval_scores.get('hit_at_k'),
            'Evidence coverage': retrieval_scores.get('evidence_coverage_at_k'),
        })
    return pd.DataFrame(rows)


def render_dashboard():
    try:
        answer_report = load_json(str(FINAL_REPORT))
        retrieval_report = load_json(str(FINAL_RETRIEVAL))
        comparison = load_json(str(CONFIG_COMPARISON))
        django_comparison = load_json(str(DJANGO_COMPARISON))
        calibration = load_json(str(CALIBRATION_RESULT))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        st.error(str(exc), title='Versioned results could not be loaded')
        st.stop()

    quality = answer_report['answer_quality']
    retrieval = retrieval_report['overall']

    st.title('RAG evaluation harness')
    st.caption('A reproducible RAG benchmark that separates retrieval, grounding and answer quality across two documentation domains.')
    st.success(
        'Benchmark v1 was frozen before the reserved test. These are saved results—opening this dashboard makes no API calls.',
        title='Frozen final evaluation',
    )

    with st.container(horizontal=True):
        st.metric('Page Hit@5', percent(retrieval['hit_at_k']), border=True,
                  help='A gold source appeared in the top five chunks for all answerable test questions.')
        st.metric('Answer correctness', percent(quality['correctness']['mean']), border=True,
                  help='Calibrated judge score on nine answerable reserved questions.')
        st.metric('Faithfulness', percent(quality['faithfulness']['mean']), border=True,
                  help='Every answer claim must be supported by the retrieved context.')
        st.metric('Abstention', percent(quality['abstention']['mean']), border=True,
                  help='The unsupported reserved question was correctly refused.')

    st.subheader('What this project evaluates')
    st.mermaid_chart(
        '''flowchart LR
        A[12 pinned docs] --> B[Chunking]
        B --> C[Retrieval top 5]
        C --> D[Context-only answer]
        D --> E[Correctness]
        D --> F[Faithfulness]
        D --> G[Abstention]
        C --> H[Hit, MRR, source recall, evidence coverage]''',
        alt='RAG evaluation flow from pinned documents through retrieval and answer-quality metrics',
    )

    st.subheader('Why configuration B was selected')
    config_rows = []
    for name, item in comparison['configurations'].items():
        config_rows.append({
            'Configuration': name,
            'Pipeline': item['pipeline'],
            'Complete evidence (%)': item['complete_evidence_at_5'] * 100,
            'Evidence coverage (%)': item['evidence_coverage_at_5'] * 100,
            'Mean retrieval (ms)': item['retrieval_mean_s'] * 1000,
        })
    config_frame = pd.DataFrame(config_rows)
    chart_column, table_column = st.columns(2, gap='large')
    with chart_column.container(border=True, height='stretch'):
        st.markdown('**Development complete evidence at top 5**')
        st.bar_chart(
            config_frame,
            x='Configuration',
            y='Complete evidence (%)',
            y_label='Complete evidence (%)',
            alt='Configuration B has the highest development complete-evidence rate',
        )
    with table_column.container(border=True, height='stretch'):
        st.markdown('**Four controlled retrieval configurations**')
        st.dataframe(
            config_frame,
            hide_index=True,
            height=285,
            alt='Development retrieval comparison for configurations A through D',
            column_config={
                'Complete evidence (%)': st.column_config.NumberColumn(format='%.1f%%'),
                'Evidence coverage (%)': st.column_config.NumberColumn(format='%.1f%%'),
                'Mean retrieval (ms)': st.column_config.NumberColumn(format='%.1f ms'),
            },
        )
    st.caption('B = semantic chunking + dense retrieval. It recovered the most complete evidence without the reranker latency of D.')

    st.subheader('Final reserved-test details')
    category_rows = []
    for name, item in retrieval_report['by_category'].items():
        category_rows.append({
            'Category': name.replace('_', ' '),
            'Evidence coverage': item['evidence_coverage_at_k'],
            'Complete evidence': item['evidence_complete_at_k'],
        })
    category_frame = pd.DataFrame(category_rows)
    st.bar_chart(
        category_frame,
        x='Category',
        y=['Evidence coverage', 'Complete evidence'],
        y_label='Rate',
        alt='Final evidence coverage is strongest for similar-page questions and weakest for direct questions',
    )

    st.dataframe(
        question_rows(answer_report, retrieval_report),
        hide_index=True,
        alt='Per-question final retrieval and answer outcomes',
        column_config={
            'Correctness': st.column_config.NumberColumn(format='%.1f'),
            'Faithfulness': st.column_config.NumberColumn(format='%.1f'),
            'Abstention': st.column_config.NumberColumn(format='%.1f'),
            'Page hit': st.column_config.ProgressColumn(min_value=0, max_value=1, format='percent'),
            'Evidence coverage': st.column_config.ProgressColumn(min_value=0, max_value=1, format='percent'),
        },
    )

    st.subheader('Failure analysis')
    left, right = st.columns(2, gap='large')
    with left.container(border=True, height='stretch'):
        st.markdown('**Over-abstention: q021 and q045**')
        st.markdown('The retriever supplied useful context, but the generator refused answerable questions. These reduce correctness.')
    with right.container(border=True, height='stretch'):
        st.markdown('**Unsupported details: q036 and q046**')
        st.markdown('The answers matched the references, but one requested fact was absent from the retrieved chunks. These reduce faithfulness.')

    counts = calibration['metric_sample_size']
    st.info(
        f"Human–judge exact agreement was 100% on {counts['correctness']} correctness, "
        f"{counts['faithfulness']} faithfulness and {counts['abstention']} abstention labels. "
        'The sample is small and has one reviewer.',
        title='Judge calibration',
    )
    st.warning(
        'The benchmark uses one FastAPI domain and only ten reserved questions. All references were AI-assisted cross-checked, but the full 50-item author checklist is incomplete.',
        title='Read the result honestly',
    )

    st.subheader('Cross-domain development check')
    st.caption(
        'The same four retrieval configurations were also run on 40 Django 5.2 LTS development questions. '
        'The ten Django reserved-test questions remain untouched.'
    )
    django_b = django_comparison['configurations']['B']
    with st.container(horizontal=True):
        st.metric('Django page Hit@5', percent(django_b['hit_at_5']), border=True)
        st.metric('Django complete evidence',
                  f"{django_b['complete_evidence_count']}/36 ({percent(django_b['complete_evidence_at_5'])})",
                  border=True)
        st.metric('Django evidence coverage', percent(django_b['evidence_coverage_at_5']), border=True)
        st.metric('Django mean retrieval', f"{django_b['retrieval_mean_s'] * 1000:.1f} ms", border=True)

    cross_domain_rows = []
    django_rows = []
    for name in comparison['configurations']:
        fastapi_item = comparison['configurations'][name]
        django_item = django_comparison['configurations'][name]
        cross_domain_rows.append({
            'Configuration': name,
            'FastAPI complete evidence (%)': fastapi_item['complete_evidence_at_5'] * 100,
            'Django complete evidence (%)': django_item['complete_evidence_at_5'] * 100,
        })
        django_rows.append({
            'Configuration': name,
            'Pipeline': django_item['pipeline'],
            'Complete evidence': django_item['complete_evidence_at_5'],
            'Evidence coverage': django_item['evidence_coverage_at_5'],
            'MRR@5': django_item['mrr_at_5'],
            'Mean retrieval (ms)': django_item['retrieval_mean_s'] * 1000,
        })
    st.bar_chart(
        pd.DataFrame(cross_domain_rows),
        x='Configuration',
        y=['FastAPI complete evidence (%)', 'Django complete evidence (%)'],
        y_label='Complete evidence (%)',
        alt='Configuration B has the highest complete-evidence rate on both development corpora',
    )
    st.dataframe(
        pd.DataFrame(django_rows),
        hide_index=True,
        alt='Django development retrieval comparison for configurations A through D',
        column_config={
            'Complete evidence': st.column_config.ProgressColumn(min_value=0, max_value=1, format='percent'),
            'Evidence coverage': st.column_config.ProgressColumn(min_value=0, max_value=1, format='percent'),
            'MRR@5': st.column_config.NumberColumn(format='%.4f'),
            'Mean retrieval (ms)': st.column_config.NumberColumn(format='%.1f ms'),
        },
    )
    st.warning(
        'Django v2 is a transparent development result, not a final benchmark claim. '
        'Its AI-assisted references passed exact-evidence validation, but semantic author review and the reserved test are pending.',
        title='Django v2 status',
    )


st.set_page_config(page_title='RAG evaluation harness', page_icon=':material/analytics:', layout='wide')
with st.sidebar:
    st.header('RAG evaluation harness')
    app_view = st.segmented_control(
        'View', ['Results dashboard', 'Blind review'], default='Results dashboard',
        key='app_view', width='stretch',
    )
    st.caption('The dashboard reads versioned reports. Review mode edits only the selected labels file.')

if app_view == 'Results dashboard':
    render_dashboard()
    st.stop()

st.title('Blind RAG answer review')
st.caption('Review saved answers without seeing the model judge scores. No API calls are made.')

try:
    packet = load_review_packet(PACKET_PATH)
    items = packet['items']
    identifiers = [item['row']['id'] for item in items]
    answerability = {item['row']['id']: item['row']['answerable'] for item in items}
    mixed = packet['version'] == 2
    label_text = LABELS_PATH.read_text(encoding='utf-8-sig')
    labels = (parse_partial_mixed_labels(label_text, answerability) if mixed
              else parse_partial_labels(label_text, set(identifiers)))
except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
    st.error(str(exc), title='Review packet could not be loaded')
    st.stop()

completed = sum(mixed_label_complete(labels[identifier], answerability[identifier])
                for identifier in identifiers)
first_open = next((identifier for identifier in identifiers
                   if not mixed_label_complete(labels[identifier], answerability[identifier])), identifiers[0])
if st.session_state.get('review_item') not in identifiers:
    st.session_state['review_item'] = first_open

with st.sidebar:
    st.header('Review progress')
    st.progress(completed / len(identifiers), text=f'{completed} of {len(identifiers)} answers saved')
    current_id = st.selectbox(
        'Answer to review', identifiers, key='review_item',
        format_func=lambda identifier: f"{identifier} ({'done' if mixed_label_complete(labels[identifier], answerability[identifier]) else 'pending'})",
    )
    st.info('The independent judge verdicts are intentionally hidden until every human label is saved.')

flash = st.session_state.pop('_review_flash', None)
if flash:
    st.success(flash)
review_error = st.session_state.pop('_review_error', None)
if review_error:
    st.error(review_error)

item = next(item for item in items if item['row']['id'] == current_id)
row, observation = item['row'], item['observation']
st.subheader(f"{current_id}: {row['question']}")
st.caption(f"Category: {row['category'].replace('_', ' ')}")

reference_column, answer_column = st.columns(2, gap='large')
with reference_column.container(border=True, height='stretch'):
    st.markdown('#### Reference answer')
    st.markdown(row['reference_answer'])
with answer_column.container(border=True, height='stretch'):
    st.markdown('#### Generated answer')
    st.markdown(observation['answer'])

context = st.expander('Retrieved context — use this to check support', expanded=True)
with context:
    for chunk in observation['chunks']:
        st.markdown(f"**{chunk['chunk_id']}**")
        st.code(chunk['text'], language=None, wrap_lines=True)

saved = labels[current_id]
with st.form(f'review_form_{current_id}'):
    if row['answerable']:
        st.markdown('#### Your two decisions')
        st.segmented_control(
            '1. Is the generated answer correct compared with the reference?',
            options=list(CORRECTNESS_LABELS), default=saved['correctness'], required=True,
            format_func=lambda value: CORRECTNESS_LABELS[value],
            key=f'correctness_{current_id}', width='stretch', wrap=True,
        )
        st.caption('Correct = all requested facts are right. Partly correct = useful but incomplete. Wrong = incorrect or refuses without reason.')
        st.segmented_control(
            '2. Is every factual claim supported by the retrieved context?',
            options=list(FAITHFULNESS_LABELS), default=saved['faithfulness'], required=True,
            format_func=lambda value: FAITHFULNESS_LABELS[value],
            key=f'faithfulness_{current_id}', width='stretch', wrap=True,
        )
        st.caption('Even a plausible fact counts as unsupported when it does not appear in the retrieved text.')
    else:
        st.markdown('#### Your decision')
        st.info('This question is intentionally unanswerable from the provided documentation.')
        st.segmented_control(
            'Did the generated answer refuse instead of inventing missing information?',
            options=list(ABSTENTION_LABELS), default=saved['abstention'], required=True,
            format_func=lambda value: ABSTENTION_LABELS[value],
            key=f'abstention_{current_id}', width='stretch', wrap=True,
        )
        st.caption('Correctly refused = it says the documentation does not contain the answer. Invented = it supplies unsupported details.')
    notes = st.text_area('Optional notes', value=saved['notes'], key=f'notes_{current_id}',
                         placeholder='Example: answer is correct, but its code example is not in the context.')
    st.form_submit_button('Save and continue', type='primary', icon=':material/save:', width='stretch',
                          on_click=save_review, args=(current_id, identifiers, answerability, mixed))

if completed == len(identifiers):
    default_packet = ROOT / 'calibration/2026-11-14/packet.json'
    if PACKET_PATH.resolve() == default_packet.resolve() and CALIBRATION_RESULT.exists():
        st.success('All human labels are complete and the calibrated agreement result is versioned.',
                   title='Calibration complete')
        st.info('Switch to Results dashboard to see the frozen final evaluation.')
    else:
        st.success('All human labels are complete. Keep them frozen before creating hidden judge verdicts.',
                   title='Review complete')
        st.info('Stop here. The judge should run only after these labels are saved and frozen.')
