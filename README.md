# Naukri Daily Profile & Resume Auto-Updater

An automated tool built with Python and Playwright to keep your Naukri profile fresh and ranking at the top of recruiter search results.

It performs **two actions** automatically:
1. **Re-uploads your resume file** (PDF or DOCX).
2. **Toggles your Resume Headline** (adds or removes a trailing dot/period and saves), resetting the "Last updated" timestamp on your profile.

Scheduled to run daily at **8:00 AM** and **5:00 PM (17:00)** IST.

---

## Quick Setup Steps (Local Machine)

### 1. Place Your Resume File
Place your latest resume (`.pdf` or `.docx`) inside the `resumes/` folder:
```bash
cp /path/to/your/resume.pdf resumes/resume.pdf
```
*(If your filename is different, either rename it to `resume.pdf` or update `DEFAULT_RESUME_FILENAME` in `config.py`)*

### 2. Install Dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
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
- Your session is securely stored in `session.json`.

### 4. Test Run
Test the updater manually:
```bash
./run.sh
```
Check `logs/update.log` to confirm success.

---

## Scheduling Options

### Option A: Systemd User Timer (Best for Laptops)
On laptops, `cron` fails if the laptop lid was closed at 5:00 PM. Systemd timers support `Persistent=true`, which automatically catches up and runs as soon as you open your laptop:
```bash
./setup_systemd_timer.sh
```

### Option B: Linux Cron
```bash
./setup_cron.sh
```

---

## Running 24/7 with Docker (Best for Cloud / VPS / Server)

If you have a 24/7 cloud server (AWS, DigitalOcean, Hetzner, GCP) or home server, you can run the bot inside Docker so it runs even when your laptop is turned off:

1. Clone this repository onto your server.
2. Copy your authenticated `session.json` and `resumes/resume.pdf` onto the server.
3. Start the container:
```bash
docker compose up -d
```
The container runs in the background and automatically triggers updates daily at 8:00 AM and 5:00 PM IST.
