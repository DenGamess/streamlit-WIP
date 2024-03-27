import streamlit as st
from google.cloud import bigquery
import os
from PIL import Image
import io
import uuid

def main():
    st.title('Submission Verification')

    # Initialize a session state variable to keep track of verified submissions
    if 'verified_submissions' not in st.session_state:
        st.session_state.verified_submissions = []

    submissions = fetch_submissions()

    for index, submission in submissions.iterrows():
        # Check if the current submission is marked as verified in the session state
        is_verified = submission['submission_id'] in st.session_state.verified_submissions

        with st.expander(f"Submission {index + 1}", expanded=True):
            display_submission(submission, is_verified)
            if st.button('Verify', key=f'verify_{index}'):
                # Mark the submission as verified locally without rerunning the app
                st.session_state.verified_submissions.append(submission['submission_id'])
                verify_submission(submission['submission_id'], verified=True)
            if st.button('Reject', key=f'reject_{index}'):
                verify_submission(submission['submission_id'], verified=False)

def display_submission(submission, is_verified):
    col1, col2 = st.columns([2, 1])
    with col1:
        if is_verified:
            st.markdown(f"### ✅ Verified Submission {submission['submission_id']}")
        else:
            st.markdown(f"### Submission {submission['submission_id']}")
        details = submission.drop(['screenshot', 'submission_id'])
        st.dataframe(details)
    with col2:
        if submission['screenshot'] is not None:
            image_bytes = submission['screenshot']
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption='Submission Screenshot', use_column_width=True)
        else:
            st.error("No screenshot available.")

# Other functions (authenticate_bigquery, connect_to_bigquery, fetch_submissions, verify_submission) remain unchanged
