"""Guided blind human review for captured RAG answers."""
import json
import os
from pathlib import Path

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


st.set_page_config(page_title='Blind RAG answer review', page_icon=':material/fact_check:', layout='wide')
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
    st.success('All human labels are complete. Keep them frozen before creating hidden judge verdicts.',
               title='Review complete')
    st.info('Stop here and tell me the review is complete. The judge will be run only after these labels are saved.')
