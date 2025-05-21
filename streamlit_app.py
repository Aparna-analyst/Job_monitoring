import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Clustered Job Postings", layout="wide")

st.title("💼 Clustered Job Postings")
st.markdown(
    "This app displays job postings scraped from Karkidi and clustered using NLP + ML models."
)

# 🗓️ Today's date
today = datetime.today().strftime("%Y-%m-%d")
csv_url = f"https://raw.githubusercontent.com/Aparna-analyst/Job_monitoring/main/clustered_jobs_{today}.csv"

# 🔁 Optional Refresh Button
if st.button("🔄 Refresh Job Listings"):
    st.experimental_rerun()

# 🚀 Try loading the CSV from GitHub
@st.cache_data(ttl=600)
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        return None, e

df, error = load_data(csv_url), None

# ✅ Success
if isinstance(df, pd.DataFrame) and not df.empty:
    st.success(f"✅ Successfully loaded job data for {today}")
    st.dataframe(df)

# ❌ Error fallback
else:
    st.error(f"❌ Failed to load data for {today} from GitHub.")
    st.info("Please check if today's file exists or push it to GitHub.")
    if isinstance(error, Exception):
        st.exception(error)
