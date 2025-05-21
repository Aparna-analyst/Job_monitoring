import subprocess
import os

# Set working directory
os.chdir(r"C:\Users\aparn\OneDrive\Documents\Job_monitoring")

# Step 1: Run the scraper
subprocess.run(["python", "daily_scrape_cluster.py"])

# Step 2: Push the new file to GitHub
subprocess.run(["python", "auto_push.py"])
