import os
import subprocess
from datetime import datetime

# 1. Paths and variables
repo_path = r"C:\Users\aparn\OneDrive\Documents\Job_monitoring"  # your local repo folder
today = datetime.today().strftime("%Y-%m-%d")
csv_name = f"clustered_jobs_{today}.csv"
csv_path = os.path.join(repo_path, csv_name)

# 2. Make sure the CSV file you want to push is already saved with the correct name in the repo folder
# For example, after scraping and clustering, save the CSV here:
# df.to_csv(csv_path, index=False)

# 3. Git commands to add, commit, and push changes
def run_git_command(command):
    result = subprocess.run(command, cwd=repo_path, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {' '.join(command)}:\n{result.stderr}")
    else:
        print(result.stdout)

# Stage the CSV file
run_git_command(f'git add {csv_name}')

# Commit changes with a message
commit_message = f'Update clustered jobs CSV for {today}'
run_git_command(f'git commit -m "{commit_message}"')

# Push to GitHub (assuming origin remote and main branch)
run_git_command('git push origin main')
