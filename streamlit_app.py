import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Clustered Job Postings", layout="wide")

st.title("💼 Clustered Job Postings")
st.markdown(
    "This app displays job postings scraped from Karkidi and clustered using NLP + ML models."
)

# 🗓️ Get today's date for dynamic CSV loading
today = datetime.today().strftime("%Y-%m-%d")
csv_url = f"https://raw.githubusercontent.com/Aparna-analyst/Job_monitoring/main/clustered_jobs_{today}.csv"

# 🚀 Try loading the CSV from GitHub
try:
    df = pd.read_csv(csv_url)
    st.success(f"✅ Successfully loaded data for {today}")
    st.dataframe(df)
except Exception as e:
    st.error("❌ Failed to load today's CSV.")
    st.info("Please check if the file exists on GitHub or try again later.")
    st.exception(e)

