import streamlit as st
from datetime import datetime
from utils.file_handler import read_file
from utils.data_cleaner import clean_data
from utils.gemini_client import infer_kpis_from_Dataframe
from utils.session_manager import SessionManager

# PAGE SETUP
st.set_page_config(page_title='Interactive Analytical Dashboard', layout='centered')
st.title('Interactive Analytical Dashboard')

# INIT SESSION
SessionManager.initialize_session()

# WELCOME TEXT
st.markdown("""
Welcome! This is a powerful platform where you can:

- Upload your data  
- Automatically analyze key performance metrics  
- Optionally get AI-powered insights  
- Export everything as a polished report 
""")
st.subheader("Upload your data to begin analysis")


# KPI GENERATION
def kpi_suggestions_block(df):
    if SessionManager.KPI_SUGGESTIONS_KEY not in st.session_state:
        st.session_state[SessionManager.KPI_SUGGESTIONS_KEY] = None

    if st.button('Generate KPIs'):
        with st.spinner('Generating KPI suggestions...'):
            kpi_suggestions = infer_kpis_from_Dataframe(df=df)
            st.session_state[SessionManager.KPI_SUGGESTIONS_KEY] = kpi_suggestions

    if st.session_state[SessionManager.KPI_SUGGESTIONS_KEY]:
        st.markdown('### KPI suggestions')
        st.markdown('---')
        st.markdown(st.session_state[SessionManager.KPI_SUGGESTIONS_KEY])


# IF DATA ALREADY LOADED
if SessionManager.has_data():
    st.success("Data loaded successfully.")

    file_info = SessionManager.get_file_info()
    if file_info:
        st.write(f"**File:** `{file_info['name']}`")
        st.write(f"**Type:** `{file_info['type']}`")
        st.write(f"**Size:** {round(file_info['size'] / 1024, 2)} KB")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cleaned_df = SessionManager.get_cleaned_data()

    # Show preview
    st.markdown('---')
    st.subheader("Cleaned Data Preview")
    st.dataframe(cleaned_df.head())

    # KPI block
    kpi_suggestions_block(cleaned_df)

    # Navigation buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("Dashboard Config", type="primary", use_container_width=True):
            st.switch_page("pages/dashboard_config.py")
    with col2:
        if st.button("Dashboard View (DIS)", use_container_width=True):
            st.switch_page("pages/dis_view.py")
    with col3:
        if st.button("Reset Data", use_container_width=True):
            SessionManager.clear_session()
            st.rerun()


# IF NO DATA YET
else:
    file_uploader = st.file_uploader(
        label="**Upload your data (CSV or Excel)**",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=False,
        help="Drag and drop your file here or click to select it."
    )

    if file_uploader is not None:
        st.write(f"**File Uploaded:** `{file_uploader.name}`")
        st.write(f"**Type:** `{file_uploader.type}`")
        st.write(f"**Size:** {round(len(file_uploader.getvalue()) / 1024, 2)} KB")

        with st.spinner('Reading file...'):
            try:
                df = read_file(file_uploader)
                if df is None:
                    st.error("No data found in the uploaded file.")
                    st.stop()
                st.markdown('---')
                st.subheader("Raw Data Preview")
                st.dataframe(df.head())
            except ValueError as e:
                st.error(f"Error reading file: {e}")
                st.stop()

        with st.spinner('Cleaning data...'):
            try:
                cleaned_df = clean_data(df)
                st.markdown('---')
                st.subheader("Cleaned Data Preview")
                st.dataframe(cleaned_df.head())

                SessionManager.store_data(cleaned_df, {
                    'name': file_uploader.name,
                    'type': file_uploader.type,
                    'size': len(file_uploader.getvalue())
                })

            except ValueError as e:
                st.error(f"Error cleaning data: {e}")
                st.stop()

        # KPI block for new upload
        kpi_suggestions_block(cleaned_df)

        # Navigation buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("Dashboard Config", type="primary", use_container_width=True):
                st.switch_page("pages/dashboard_config.py")
        with col2:
            if st.button("Dashboard View (DIS)", use_container_width=True):
                st.switch_page("pages/dis_view.py")
        with col3:
            if st.button("Reset Data", use_container_width=True):
                SessionManager.clear_session()
                st.rerun()
