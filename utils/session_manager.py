import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any

class SessionManager:
    """Manages session state persistence across page navigation."""
    
    # Key constants for session state
    CLEANED_DF_KEY = 'cleaned_df'
    SELECTED_CHARTS_KEY = 'selected_charts'
    KPI_SUGGESTIONS_KEY = 'kpi_suggestions'
    UPLOADED_FILE_INFO_KEY = 'uploaded_file_info'
    
    @staticmethod
    def initialize_session():
        """Initialize session state with default values."""
        if SessionManager.CLEANED_DF_KEY not in st.session_state:
            st.session_state[SessionManager.CLEANED_DF_KEY] = None
        if SessionManager.SELECTED_CHARTS_KEY not in st.session_state:
            st.session_state[SessionManager.SELECTED_CHARTS_KEY] = []
        if SessionManager.KPI_SUGGESTIONS_KEY not in st.session_state:
            st.session_state[SessionManager.KPI_SUGGESTIONS_KEY] = None
        if SessionManager.UPLOADED_FILE_INFO_KEY not in st.session_state:
            st.session_state[SessionManager.UPLOADED_FILE_INFO_KEY] = None
    
    @staticmethod
    def store_data(cleaned_df: pd.DataFrame, file_info: Dict[str, Any] = None):
        """Store cleaned data and file info in session state."""
        st.session_state[SessionManager.CLEANED_DF_KEY] = cleaned_df
        if file_info:
            st.session_state[SessionManager.UPLOADED_FILE_INFO_KEY] = file_info
    
    @staticmethod
    def get_cleaned_data() -> Optional[pd.DataFrame]:
        """Retrieve cleaned data from session state."""
        return st.session_state.get(SessionManager.CLEANED_DF_KEY)
    
    @staticmethod
    def store_selected_charts(charts: List[Dict[str, Any]]):
        """Store selected charts configuration."""
        st.session_state[SessionManager.SELECTED_CHARTS_KEY] = charts
    
    @staticmethod
    def get_selected_charts() -> List[Dict[str, Any]]:
        """Retrieve selected charts configuration."""
        return st.session_state.get(SessionManager.SELECTED_CHARTS_KEY, [])
    
    @staticmethod
    def has_data() -> bool:
        """Check if cleaned data exists in session."""
        return SessionManager.CLEANED_DF_KEY in st.session_state and st.session_state[SessionManager.CLEANED_DF_KEY] is not None
    
    @staticmethod
    def clear_session():
        """Clear all session state data."""
        keys_to_clear = [
            SessionManager.CLEANED_DF_KEY,
            SessionManager.SELECTED_CHARTS_KEY,
            SessionManager.KPI_SUGGESTIONS_KEY,
            SessionManager.UPLOADED_FILE_INFO_KEY
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def get_file_info() -> Optional[Dict[str, Any]]:
        """Get uploaded file information."""
        return st.session_state.get(SessionManager.UPLOADED_FILE_INFO_KEY)
