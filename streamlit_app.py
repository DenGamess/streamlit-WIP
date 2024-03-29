import streamlit as st
from google.cloud import bigquery
import os
from PIL import Image
import io

def authenticate_bigquery():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(current_dir, 'shaped-faculty-372218-840d45f07bdf.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

def connect_to_bigquery():
    authenticate_bigquery()
    return bigquery.Client()

def fetch_submissions():
    client = connect_to_bigquery()
    query = """
    SELECT *
    FROM `shaped-faculty-372218.streamer_data.streamlit_data`
    WHERE is_verified = FALSE
    """
    query_job = client.query(query)
    results = query_job.to_dataframe()
    for col in results.columns:
        if col != 'screenshot':
            results[col] = results[col].astype(str)
    return results

def display_submission(submission):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### Submission {submission['submission_id']}")
        details = submission.drop(['screenshot', 'submission_id'], errors='ignore')
        st.dataframe(details)
    with col2:
        if submission.get('screenshot') is not None:
            image_bytes = io.BytesIO(submission['screenshot'])
            image = Image.open(image_bytes)
            st.image(image, caption='Submission Screenshot', use_column_width=True)
        else:
            st.error("No screenshot available.")

def verify_submission(submission_id, verified):
    client = connect_to_bigquery()
    query = f"""
    UPDATE `shaped-faculty-372218.streamer_data.streamlit_data`
    SET is_verified = {'TRUE' if verified else 'FALSE'}
    WHERE submission_id = '{submission_id}'
    """
    query_job = client.query(query)
    query_job.result()
    if query_job.errors is None:
        st.success(f'Submission {"verified" if verified else "rejected"} successfully!')
    else:
        st.error(f'Error verifying submission: {query_job.errors}')

def main():
    st.title('Submission Verification')

    if st.button('Refresh Submissions'):
        st.experimental_rerun()

    submissions = fetch_submissions()

    for index, submission in submissions.iterrows():
        with st.expander(f"Submission {index + 1}", expanded=True):
            display_submission(submission)
            if st.button('Verify', key=f'verify_{index}'):
                verify_submission(submission['submission_id'], verified=True)
                st.experimental_rerun()  # Refresh submissions after a change
            if st.button('Reject', key=f'reject_{index}'):
                verify_submission(submission['submission_id'], verified=False)
                st.experimental_rerun()  # Refresh submissions after a change

if __name__ == "__main__":
    main()
