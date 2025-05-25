import streamlit as st
import pandas as pd
from datetime import datetime

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

# 🚀 Load CSV from GitHub with caching
@st.cache_data(ttl=600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception:
        return None

df = load_data(csv_url)

if df is not None and not df.empty:
    st.success(f"✅ Successfully loaded job data for {today}")
    st.dataframe(df)
else:
    st.error(f"❌ Failed to load data for {today} from GitHub.")
    st.info("Please check if today's file exists or push it to GitHub.")

