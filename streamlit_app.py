import streamlit as st
from google.cloud import bigquery
import os
import base64

VALID_CREDENTIALS = {
    'elidenslow': {'password': '3jL5sdc1', 'tiktok_handle': 'elidenslow_tiktok', 'paypal_email': 'emdenslow@example.com'},
    'colm': {'password': 'password', 'tiktok_handle': 'colm_tiktok', 'paypal_email': 'colm@example.com'},
    'trevorkreiling': {'password': 'password', 'tiktok_handle': 'Triumph.trev', 'paypal_email': 'Trevorkreiling830@gmail.com'}
}

def authenticate_bigquery():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(current_dir, 'shaped-faculty-372218-840d45f07bdf.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
    
def connect_to_bigquery():
    authenticate_bigquery()
    return bigquery.Client()

def stream_to_bigquery(data):
    client = connect_to_bigquery()
    table_id = 'shaped-faculty-372218.streamer_data.streamlit_wip'

    data['stream_datetime'] = data['stream_datetime'].strftime('%Y-%m-%d')

    screenshot_bytes = data.pop('screenshot')
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
    data['screenshot'] = screenshot_base64

    errors = client.insert_rows_json(table_id, [data])

    if errors == []:
        st.success('Data successfully streamed to BigQuery!')
    else:
        st.error(f'Error streaming data to BigQuery: {errors}')

def login():
    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        if username in VALID_CREDENTIALS and password == VALID_CREDENTIALS[username]['password']:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.show_login = False
            st.success('Login successful!')
            form()
        else:
            st.error('Invalid username or password')

def form():
    st.title('Stream Submissions')

    name_placeholder = 'e.g., John Doe'
    num_views_placeholder = 'e.g., 5000'
    stream_time_placeholder = 'e.g., 60'
    date_placeholder = 'Select date'

    if st.session_state.username in VALID_CREDENTIALS:
        # Check if the user is an admin
        is_admin = st.session_state.username in ['elidenslow']
        
        if is_admin:
            # Display data from BigQuery
            display_data_from_bigquery()
        else:
            # Display regular form for non-admin users
            st.text_input('Full Name', value=st.session_state.username, placeholder=name_placeholder, key='name', disabled=True)
            st.text_input('TikTok Handle', value=VALID_CREDENTIALS[st.session_state.username]['tiktok_handle'], disabled=True)
            st.text_input('PayPal Email Address', value=VALID_CREDENTIALS[st.session_state.username]['paypal_email'], disabled=True)
            
            num_views = st.number_input('Number of Views', min_value=0, value=0, step=1, format='%d', help=num_views_placeholder)
            stream_time = st.number_input('Stream Length (Mins)', min_value=0, value=0, step=1, format='%d', help=stream_time_placeholder)
            date_time = st.date_input('Date', value=None, help=date_placeholder)
            
            st.write('Upload Screenshot of TikTok Live Analytics:')
            screenshot = st.file_uploader('Upload Image', type=['png', 'jpg'])
            
            if st.button('Submit'):
                if num_views and stream_time and date_time and screenshot:
                    screenshot_bytes = screenshot.read()

                    data = {
                        'name': st.session_state.username,
                        'tiktok_handle': VALID_CREDENTIALS[st.session_state.username]['tiktok_handle'],
                        'paypal_email': VALID_CREDENTIALS[st.session_state.username]['paypal_email'],
                        'num_views': num_views,
                        'stream_length': stream_time,
                        'stream_datetime': date_time,
                        'screenshot': screenshot_bytes
                    }

                    stream_to_bigquery(data)
                else:
                    st.warning('Please fill out all fields and upload a screenshot')

def display_data_from_bigquery():
    # Connect to BigQuery
    client = connect_to_bigquery()

    # Query data from BigQuery
    query_job = client.query("""
        SELECT *
        FROM `shaped-faculty-372218.streamer_data.streamlit_data`
    """)

    # Display data in a table
    df = query_job.to_dataframe()
    st.write(df)

def main():
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True

    if st.session_state.show_login:
        login()
    elif not st.session_state.logged_in:
        login()
    else:
        form()

if __name__ == "__main__":
    main()
