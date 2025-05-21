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
WORKING_DIR = r"C:\Users\aparn\OneDrive\Documents\Job_monitoring"

# 🔧 Load your saved model & vectorizer with absolute path
model = joblib.load(os.path.join(WORKING_DIR, "job_cluster_model.pkl"))
vectorizer = joblib.load(os.path.join(WORKING_DIR, "tfidf_vectorizer.pkl"))

# ✉️ Email Config — 🔒 DO NOT share this info
sender_email = "aparnassunil23@gmail.com"
sender_password = "qsxp jbru ddwa favy"  # 16-char app password from Google
receiver_email = "aparnassunil22@gmail.com"

# 📝 Logging function with absolute path
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

def send_email_with_csv(csv_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"📊 Clustered Job Report - {datetime.today().strftime('%Y-%m-%d')}"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content("Attached is the latest clustered job listings CSV.")

        with open(csv_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=os.path.basename(csv_path))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        log("📩 Email sent successfully with attached CSV.")
    except Exception as e:
        log(f"🚨 Email sending failed: {e}")

def daily_scrape_and_cluster():
    log("⏳ Starting scrape and cluster")
    df_jobs = scrape_karkidi_jobs(pages=3)

    if df_jobs.empty:
        log("❗ No jobs found.")
        return

    df_clustered = preprocess_and_predict(df_jobs)
    filename = os.path.join(WORKING_DIR, f"clustered_jobs_{datetime.today().strftime('%Y-%m-%d')}.csv")
    df_clustered.to_csv(filename, index=False)
    log(f"✅ Scrape + cluster complete. Saved to {filename}")

    send_email_with_csv(filename)

if __name__ == "__main__":
    try:
        daily_scrape_and_cluster()
    except Exception as e:
        log(f"🚨 Unexpected error: {str(e)}")

