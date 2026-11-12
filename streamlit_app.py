"""Guided blind human review for captured RAG answers."""
import json
import os
from pathlib import Path

import streamlit as st

from src.evaluation.human_review import load_review_packet, parse_partial_labels, save_partial_labels

ROOT = Path(__file__).resolve().parent
PACKET_PATH = Path(os.getenv('RAG_REVIEW_PACKET', ROOT / 'calibration/2026-10-26/packet.json'))
LABELS_PATH = Path(os.getenv('RAG_REVIEW_LABELS', ROOT / 'calibration/2026-10-26/labels.csv'))
CORRECTNESS_LABELS = {1.0: 'Correct', .5: 'Partly correct', 0.0: 'Wrong'}
FAITHFULNESS_LABELS = {1: 'Fully supported', 0: 'Has an unsupported claim'}


def save_review(identifier, identifiers):
    try:
        latest = parse_partial_labels(LABELS_PATH.read_text(encoding='utf-8-sig'), set(identifiers))
        correctness = st.session_state[f'correctness_{identifier}']
        faithfulness = st.session_state[f'faithfulness_{identifier}']
        if correctness not in CORRECTNESS_LABELS or faithfulness not in FAITHFULNESS_LABELS:
            raise ValueError('Choose one correctness option and one support option before saving.')
        latest[identifier] = {'correctness': correctness, 'faithfulness': faithfulness,
                              'notes': st.session_state[f'notes_{identifier}'].strip()}
        save_partial_labels(LABELS_PATH, identifiers, latest)
        remaining = [item_id for item_id in identifiers
                     if item_id != identifier and latest[item_id]['correctness'] is None]
        st.session_state['review_item'] = remaining[0] if remaining else identifier
        st.session_state['_review_flash'] = f'Saved {identifier}.'
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.session_state['_review_error'] = str(exc)


st.set_page_config(page_title='Blind RAG answer review', page_icon=':material/fact_check:', layout='wide')
st.title('Blind RAG answer review')
st.caption('Review saved answers without seeing the model judge scores. No API calls are made.')

try:
    packet = load_review_packet(PACKET_PATH)
    items = packet['items']
    identifiers = [item['row']['id'] for item in items]
    labels = parse_partial_labels(LABELS_PATH.read_text(encoding='utf-8-sig'), set(identifiers))
except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
    st.error(str(exc), title='Review packet could not be loaded')
    st.stop()

completed = sum(label['correctness'] is not None for label in labels.values())
first_open = next((identifier for identifier in identifiers if labels[identifier]['correctness'] is None), identifiers[0])
if st.session_state.get('review_item') not in identifiers:
    st.session_state['review_item'] = first_open

with st.sidebar:
    st.header('Review progress')
    st.progress(completed / len(identifiers), text=f'{completed} of {len(identifiers)} answers saved')
    current_id = st.selectbox(
        'Answer to review', identifiers, key='review_item',
        format_func=lambda identifier: f"{identifier} ({'done' if labels[identifier]['correctness'] is not None else 'pending'})",
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
    st.markdown('#### Your two decisions')
    correctness = st.segmented_control(
        '1. Is the generated answer correct compared with the reference?',
        options=list(CORRECTNESS_LABELS), default=saved['correctness'], required=True,
        format_func=lambda value: CORRECTNESS_LABELS[value],
        key=f'correctness_{current_id}', width='stretch', wrap=True,
    )
    st.caption('Correct = all requested facts are right. Partly correct = useful but incomplete. Wrong = incorrect or refuses without reason.')
    faithfulness = st.segmented_control(
        '2. Is every factual claim supported by the retrieved context?',
        options=list(FAITHFULNESS_LABELS), default=saved['faithfulness'], required=True,
        format_func=lambda value: FAITHFULNESS_LABELS[value],
        key=f'faithfulness_{current_id}', width='stretch', wrap=True,
    )
    st.caption('Even a plausible fact counts as unsupported when it does not appear in the retrieved text.')
    notes = st.text_area('Optional notes', value=saved['notes'], key=f'notes_{current_id}',
                         placeholder='Example: answer is correct, but its code example is not in the context.')
    st.form_submit_button('Save and continue', type='primary', icon=':material/save:', width='stretch',
                          on_click=save_review, args=(current_id, identifiers))

if completed == len(identifiers):
    st.success('All human labels are complete. You can now compare them with the hidden judge verdicts.',
               title='Review complete')
    st.code('python -m src.evaluation.human_review compare --packet calibration/2026-10-26/packet.json '
            '--labels calibration/2026-10-26/labels.csv --judge runs/judge-calibration-20261026 '
            '--output runs/agreement-calibration-20261026.json', language='bash', wrap_lines=True)
