"""
Automated profile and resume updater for Naukri.
Performs:
1. Pre-flight internet connectivity check
2. Re-uploading resume file (resets 'Last updated' timestamp)
3. Toggling minor character (trailing period) in Resume Headline and saving
4. Automatic retry loop (up to 3 attempts) on network/timing issues
"""

import os
import sys
import time
import socket
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth.stealth import Stealth

import config

# Setup logging
config.LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("NaukriUpdater")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(sh)


def check_internet_connection(max_wait_seconds=60) -> bool:
    """Waits for active internet connection (crucial when waking from system sleep)."""
    logger.info("Checking internet connection...")
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        try:
            # Check connection to reliable DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            logger.info("Internet connection verified.")
            return True
        except OSError:
            logger.warning("No internet connection yet. Waiting 5 seconds for network...")
            time.sleep(5)

    logger.error("Network unavailable after waiting. Cannot proceed with update.")
    return False


def find_resume_file() -> Path | None:
    """Finds the resume file either from config or from resumes/ directory."""
    if config.RESUME_PATH.exists():
        return config.RESUME_PATH

    if config.RESUME_DIR.exists():
        files = list(config.RESUME_DIR.glob("*.pdf")) + list(config.RESUME_DIR.glob("*.docx"))
        if files:
            return files[0]

    return None


def update_resume_upload(page) -> bool:
    """Finds the resume file input and uploads the resume."""
    resume_file = find_resume_file()
    if not resume_file:
        logger.error(f"No resume file found at '{config.RESUME_PATH}' or in '{config.RESUME_DIR}'. Skipping resume upload.")
        return False

    logger.info(f"Attempting resume re-upload with: {resume_file.name}")
    try:
        file_input = page.locator("input#attachCV, input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(str(resume_file))
            logger.info("Resume file attached. Waiting for upload to process...")
            page.wait_for_timeout(5000)

            # Check status box or toast
            msg_box = page.locator("#attachCVMsgBox, .msg-box, [class*='success'], [class*='updateOn']")
            msg_text = msg_box.first.text_content().strip() if msg_box.count() > 0 else ""
            if msg_text:
                logger.info(f"Naukri status: {msg_text}")

            logger.info("✓ Resume re-upload completed successfully.")
            return True
        else:
            logger.warning("Could not find file input element (input#attachCV) for resume upload.")
            return False
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        return False


def update_resume_headline(page) -> bool:
    """Touches the Resume Headline by adding or removing a trailing period and saving."""
    logger.info("Attempting Resume Headline update...")
    try:
        headline_card = page.locator("#resumeHeadline")
        if headline_card.count() > 0:
            headline_card.first.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)

        # Locate the Resume headline edit button
        edit_btn = page.locator("#resumeHeadline [aria-label*='Edit'], #resumeHeadline [class*='edit-icon'], #resumeHeadline [class*='edit']")
        if edit_btn.count() == 0:
            edit_btn = page.locator("#resumeHeadline img[src*='edit']").locator("xpath=..")

        if edit_btn.count() == 0:
            logger.warning("Could not find edit button for Resume Headline.")
            return False

        edit_btn.first.click()
        page.wait_for_timeout(1500)

        # Locate the headline textarea
        textarea = page.locator("textarea.textAreaField__control, textarea#FIELD_GPT_TEXTAREA_EDIT, textarea#resumeHeadlineTxt, form textarea, textarea")
        if textarea.count() > 0:
            current_text = textarea.first.input_value().strip()
            logger.info(f"Current Resume Headline: '{current_text}'")

            # Toggle trailing period: if ends with '.', remove it; else append '.'
            if current_text.endswith("."):
                new_text = current_text[:-1].rstrip()
            else:
                new_text = current_text + "."

            logger.info(f"Updating Headline to: '{new_text}'")
            textarea.first.fill(new_text)
            page.wait_for_timeout(800)

            # Click Save button
            save_btn = page.locator("button:has-text('Save'), .ButtonWithLoader_button__E7yps, button.btn-dark-ot, input[type='submit'][value='Save']")
            if save_btn.count() > 0:
                save_btn.first.click()
                page.wait_for_timeout(3500)
                logger.info("✓ Resume headline updated and saved successfully.")
                return True
            else:
                logger.warning("Found textarea but could not locate Save button.")
                return False
        else:
            logger.warning("Could not find Resume Headline textarea.")
            return False

    except Exception as e:
        logger.error(f"Failed to update Resume Headline: {e}")
        return False


def execute_single_attempt() -> bool:
    """Performs one update attempt and returns True if successful."""
    stealth = Stealth()
    with stealth.use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        context = browser.new_context(
            storage_state=str(config.SESSION_FILE),
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (X-UA-Compatible; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            logger.info(f"Navigating to Naukri profile: {config.NAUKRI_PROFILE_URL}")
            page.goto(config.NAUKRI_PROFILE_URL, wait_until="domcontentloaded", timeout=config.BROWSER_TIMEOUT_MS)
            page.wait_for_timeout(2000)

            # Check if redirected to login page or access denied
            if "login" in page.url.lower():
                logger.error("Session has expired! Naukri redirected to the login page.")
                logger.error("Please re-run 'python auth_login.py' to generate a fresh session.")
                return False

            if "Access Denied" in page.title():
                logger.error("Access Denied by bot detection.")
                return False

            # Wait for profile cards to render (wait for DOM attachment, then scroll into view)
            logger.info("Waiting for profile cards to render...")
            page.wait_for_selector("#resumeHeadline", state="attached", timeout=30000)
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollTo(0, 600)")
            page.wait_for_timeout(1500)
            logger.info("Profile page successfully loaded.")

            # Action 1: Upload Resume
            resume_ok = update_resume_upload(page)

            # Action 2: Update Resume Headline
            headline_ok = update_resume_headline(page)

            # Refresh and save session state
            context.storage_state(path=str(config.SESSION_FILE))

            if resume_ok and headline_ok:
                logger.info("★ SUCCESS: Both Resume upload and Headline update completed successfully!")
                return True
            elif resume_ok or headline_ok:
                logger.info("Partial update succeeded.")
                return True
            else:
                logger.warning("Neither action succeeded.")
                return False

        except Exception as e:
            logger.error(f"Attempt encountered error: {e}")
            try:
                err_screenshot = config.LOG_DIR / "error_latest.png"
                page.screenshot(path=str(err_screenshot))
                logger.info(f"Saved diagnostic screenshot to {err_screenshot}")
            except Exception:
                pass
            return False
        finally:
            browser.close()


def run_update():
    logger.info("==========================================")
    logger.info("Starting Naukri Daily Profile Update Task")
    logger.info("==========================================")

    if not config.SESSION_FILE.exists():
        logger.error(f"Session file not found: {config.SESSION_FILE}")
        logger.error("Please run 'python auth_login.py' first to log in and save your session.")
        sys.exit(1)

    if not check_internet_connection(max_wait_seconds=60):
        logger.error("Exiting due to no network connectivity.")
        sys.exit(1)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        logger.info(f"--- Attempt {attempt} of {max_attempts} ---")
        if execute_single_attempt():
            logger.info("Update completed successfully.\n")
            return
        if attempt < max_attempts:
            wait_sec = 15 * attempt
            logger.warning(f"Attempt {attempt} failed. Retrying in {wait_sec} seconds...")
            time.sleep(wait_sec)

    logger.error("All update attempts failed.\n")
    sys.exit(1)


if __name__ == "__main__":
    run_update()
