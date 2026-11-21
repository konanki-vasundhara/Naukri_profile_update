"""
Background 24/7 scheduler for Docker and server environments.
Runs update_naukri at 08:00 AM and 05:00 PM IST daily.
"""

import time
import schedule
import logging
from datetime import datetime
from update_naukri import run_update

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("NaukriScheduler")

def job():
    logger.info("Scheduler triggered scheduled update job.")
    try:
        run_update()
    except Exception as e:
        logger.error(f"Error executing scheduled job: {e}")

# Schedule for 09:00 AM and 05:00 PM (17:00)
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("17:00").do(job)

if __name__ == "__main__":
    logger.info("==================================================")
    logger.info("Naukri Auto-Updater Scheduler started.")
    logger.info("Scheduled times: 09:00 AM and 05:00 PM (17:00) daily.")
    logger.info("Current system time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("==================================================")

    while True:
        schedule.run_pending()
        time.sleep(30)
