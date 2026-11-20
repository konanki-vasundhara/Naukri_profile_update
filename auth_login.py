"""
Interactive login script for Naukri.
Opens a browser window for you to log in (handling credentials, Google Login, or OTP).
Once logged in, it saves your authenticated session state to `session.json`.
"""

import sys
import time
from playwright.sync_api import sync_playwright
import config

def login_and_save_session():
    print("=" * 60)
    print("Naukri Interactive Login & Session Setup")
    print("=" * 60)
    print("A browser window will open shortly.")
    print("1. Log in to your Naukri account (using Password, OTP, or Google).")
    print("2. Navigate until you reach your Naukri homepage or profile.")
    print("3. Return to this terminal and press Enter to save your session.")
    print("=" * 60)

    with sync_playwright() as p:
        # Launch browser in visible (non-headless) mode with realistic viewport & user-agent
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (X-UA-Compatible; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("\nOpening Naukri Login page...")
        page.goto(config.NAUKRI_LOGIN_URL, wait_until="domcontentloaded")

        # Wait for user confirmation in terminal
        input("\n>>> Once you have completely logged in and see your profile/dashboard, press [ENTER] here to save session: ")

        print("\nVerifying session and saving storage state...")
        # Save storage state (cookies, local storage, tokens)
        context.storage_state(path=str(config.SESSION_FILE))
        print(f"[SUCCESS] Session saved successfully to: {config.SESSION_FILE}")
        print("Your automated daily updates can now run without requiring manual login!")

        browser.close()

if __name__ == "__main__":
    try:
        login_and_save_session()
    except KeyboardInterrupt:
        print("\nLogin cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        sys.exit(1)
