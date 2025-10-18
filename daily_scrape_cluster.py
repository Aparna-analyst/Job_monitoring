import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import joblib
from sklearn.preprocessing import normalize
import os
import smtplib
from email.message import EmailMessage

# Set your working folder path here:
WORKING_DIR = r"C:\Users\aparn\Downloads\Job_monitoring"

# Load your saved model & vectorizer
model = joblib.load(os.path.join(WORKING_DIR, "job_cluster_model.pkl"))
vectorizer = joblib.load(os.path.join(WORKING_DIR, "tfidf_vectorizer.pkl"))

# Email Config — keep this secure!
sender_email = "aparnassunil23@gmail.com"
sender_password = "qsxp jbru ddwa favy"  # app password
receiver_email = "aparnassunil22@gmail.com"

# Set user preferred clusters for alerts (e.g., 0 and 4 are Data Science clusters)
USER_PREFERRED_CLUSTERS = [0, 4]

# File to keep track of job titles already emailed
SENT_JOBS_FILE = os.path.join(WORKING_DIR, "sent_jobs.txt")

def log(message):
    log_file = os.path.join(WORKING_DIR, "log.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def scrape_karkidi_jobs(pages=3):
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = "https://www.karkidi.com/Find-Jobs/{page}/all/India"
    jobs_list = []

    for page in range(1, pages + 1):
        url = base_url.format(page=page)
        log(f"Scraping page {page}: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            job_blocks = soup.find_all("div", class_="ads-details")
            for job in job_blocks:
                try:
                    title = job.find("h4").get_text(strip=True)
                    company = job.find("a", href=lambda x: x and "Employer-Profile" in x).get_text(strip=True)
                    location = job.find("p").get_text(strip=True)
                    experience = job.find("p", class_="emp-exp").get_text(strip=True)
                    key_skills_tag = job.find("span", string="Key Skills")
                    skills = key_skills_tag.find_next("p").get_text(strip=True) if key_skills_tag else ""
                    summary_tag = job.find("span", string="Summary")
                    summary = summary_tag.find_next("p").get_text(strip=True) if summary_tag else ""

                    jobs_list.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,
                        "Experience": experience,
                        "Summary": summary,
                        "Skills": skills
                    })
                except Exception as e:
                    log(f"⚠️ Error parsing job block: {e}")
                    continue

            time.sleep(1)
        except Exception as e:
            log(f"❌ Error fetching page {page}: {e}")
            continue

    return pd.DataFrame(jobs_list)

def preprocess_and_predict(df):
    df = df.copy()
    df["Skills"] = df["Skills"].fillna("").str.lower()
    X = vectorizer.transform(df["Skills"])
    X = normalize(X)
    df["Cluster"] = model.predict(X)
    return df

def load_sent_jobs():
    if not os.path.exists(SENT_JOBS_FILE):
        return set()
    with open(SENT_JOBS_FILE, "r", encoding="utf-8") as f:
        sent = f.read().splitlines()
    return set(sent)

def save_sent_jobs(sent_jobs):
    with open(SENT_JOBS_FILE, "w", encoding="utf-8") as f:
        for job in sent_jobs:
            f.write(job + "\n")

def send_email(new_jobs_df):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"📢 New Jobs Alert - {datetime.today().strftime('%Y-%m-%d')}"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        content = "New job listings matching your preferred category:\n\n"
        for idx, row in new_jobs_df.iterrows():
            content += (
                f"Title: {row['Title']}\n"
                f"Company: {row['Company']}\n"
                f"Location: {row['Location']}\n"
                f"Experience: {row['Experience']}\n"
                f"Skills: {row['Skills']}\n"
                f"Summary: {row['Summary']}\n\n"
            )

        msg.set_content(content)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        log(f"📩 Email sent successfully with {len(new_jobs_df)} new jobs.")
    except Exception as e:
        log(f"🚨 Email sending failed: {e}")

def daily_scrape_and_alert():
    log("⏳ Starting scrape and alert")
    df_jobs = scrape_karkidi_jobs(pages=3)

    if df_jobs.empty:
        log("❗ No jobs found.")
        return

    df_clustered = preprocess_and_predict(df_jobs)
    
    # Save the full clustered jobs CSV for monitoring/debugging
    clustered_csv_path = os.path.join(WORKING_DIR, f"clustered_jobs_{datetime.today().strftime('%Y-%m-%d')}.csv")
    df_clustered.to_csv(clustered_csv_path, index=False)
    log(f"✅ Clustered jobs saved to {clustered_csv_path}")
    
    # Load previously sent jobs
    sent_jobs = load_sent_jobs()

    # Filter jobs matching user's preferred clusters
    preferred_jobs = df_clustered[df_clustered["Cluster"].isin(USER_PREFERRED_CLUSTERS)]

    # Filter only new jobs (by title)
    new_jobs = preferred_jobs[~preferred_jobs["Title"].isin(sent_jobs)]

    if new_jobs.empty:
        log("ℹ️ No new jobs in preferred category today. No email sent.")
        return

    # Send email with new jobs
    send_email(new_jobs)

    # Update sent jobs list and save
    updated_sent_jobs = sent_jobs.union(set(new_jobs["Title"].tolist()))
    save_sent_jobs(updated_sent_jobs)

if __name__ == "__main__":
    try:
        daily_scrape_and_alert()
    except Exception as e:
        log(f"🚨 Unexpected error: {str(e)}")
