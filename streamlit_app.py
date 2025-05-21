import streamlit as st
import pandas as pd

# Replace this with the raw URL of your latest CSV
csv_url = "https://raw.githubusercontent.com/Aparna-analyst/Job_monitoring/main/clustered_jobs_2025-05-21.csv"

st.title("💼 Clustered Job Postings")
st.markdown("This app shows job postings scraped and clustered using NLP + ML.")

try:
    df = pd.read_csv(csv_url)
    st.success("CSV loaded successfully!")
    st.dataframe(df)
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
