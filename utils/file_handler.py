import pandas as pd 
import io
import streamlit as st

def read_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded")
    
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file type. Please upload a CSV or Excel file.") 
        if df.empty:
            raise ValueError('Uploaded file contains no data')
        return df
    except Exception as e:
        raise ValueError(f"Failed to read the file: {str(e)}")