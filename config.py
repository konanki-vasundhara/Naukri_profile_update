import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Path to store authenticated session state
SESSION_FILE = BASE_DIR / "session.json"

# Path to the resume file (PDF or DOCX) to upload
# Place your resume in the 'resumes/' directory, or specify an absolute path here.
RESUME_DIR = BASE_DIR / "resumes"
DEFAULT_RESUME_FILENAME = "resume.pdf"  # e.g., resume.pdf or resume.docx
RESUME_PATH = RESUME_DIR / DEFAULT_RESUME_FILENAME

# URLs
NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"

# Browser settings
HEADLESS = True  # Set to False if you want to watch the browser in action
BROWSER_TIMEOUT_MS = 60000  # 60 seconds

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "update.log"
