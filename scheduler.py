import schedule
import time
from main import main  # import the entry function
import subprocess

def run_script():
    print("Running LinkedIn scraper...")
    subprocess.run(["python3", "main.py"], check=True)

schedule.every().day.at("15:30").do(run_script)

while True:
    schedule.run_pending()
    time.sleep(60)  # check every minute
