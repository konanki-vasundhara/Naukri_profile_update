# Naukri Daily Profile & Resume Auto-Updater

An automated tool built with Python and Playwright to keep your Naukri profile fresh and ranking at the top of recruiter search results.

It performs **two actions** automatically:
1. **Re-uploads your resume file** (PDF or DOCX).
2. **Toggles your Resume Headline** (adds or removes a trailing dot/period and saves), resetting the "Last updated" timestamp on your profile.

Scheduled to run daily at **8:00 AM** and **5:00 PM (17:00)**.

---

## Quick Setup Steps

### 1. Place Your Resume File
Place your latest resume (`.pdf` or `.docx`) inside the `resumes/` folder:
```bash
cp /path/to/your/resume.pdf resumes/resume.pdf
```
*(If your filename is different, either rename it to `resume.pdf` or update `DEFAULT_RESUME_FILENAME` in `config.py`)*

### 2. Install Dependencies
Activate the virtual environment and install Playwright along with its browser binaries:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install playwright
playwright install chromium
```

### 3. One-Time Login (Session Setup)
Run the interactive login script once:
```bash
python3 auth_login.py
```
- A Chromium window will open with the Naukri login page.
- Log in with your credentials, OTP, or Google account.
- Once you are on your Naukri profile/dashboard, press **[ENTER]** in your terminal.
- Your session is securely stored in `session.json` so you never need to enter credentials or OTP again.

### 4. Test Run
Test the updater manually once:
```bash
./run.sh
```
Check `logs/update.log` to confirm that the resume was uploaded and the headline was updated.

### 5. Schedule Daily at 8:00 AM and 5:00 PM
Run the included cron setup script:
```bash
./setup_cron.sh
```
This automatically registers the crontab entries:
- `0 8 * * *` (8:00 AM every day)
- `0 17 * * *` (5:00 PM every day)

---

## File Overview
- `config.py`: Configuration settings (file paths, headless mode, timeouts).
- `auth_login.py`: Opens a visible browser to log in once and save session cookies.
- `update_naukri.py`: Main headless worker that performs the resume re-upload and headline edit.
- `run.sh`: Shell wrapper that activates the virtual environment and runs the update task.
- `setup_cron.sh`: Installs the 8 AM & 5 PM schedule into Linux `cron`.
- `logs/update.log`: Complete audit log of every update run.
>>>>>>> 061ff33 (version-1 naukri profile updater)
