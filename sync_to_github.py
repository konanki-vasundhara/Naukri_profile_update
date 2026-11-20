"""
Syncs the local authenticated session and encrypted resume to GitHub Actions secrets
so daily updates run automatically in the cloud even when your laptop is turned off.
"""

import os
import re
import sys
import base64
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from nacl import encoding, public

def get_git_credentials():
    """Extracts repo name and token from git remote URL or environment."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = None

    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            text=True
        ).strip()

        # Match https://<token>@github.com/<owner>/<repo>.git or https://github.com/<owner>/<repo>.git
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?", remote_url)
        if m:
            repo = m.group(1)

        if not token:
            tok_match = re.search(r"https://([^@:]+)@", remote_url)
            if tok_match and tok_match.group(1).startswith("ghp_"):
                token = tok_match.group(1)
    except Exception:
        pass

    if not repo:
        repo = "konanki-vasundhara/Naukri_profile_update"

    return repo, token

REPO, TOKEN = get_git_credentials()

def get_headers():
    if not TOKEN:
        raise ValueError("GitHub Token not found in git remote URL or GITHUB_TOKEN environment variable.")
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Naukri-Cloud-Sync"
    }

def encrypt_value(public_key_b64: str, secret_value: str) -> str:
    pub_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(pub_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def get_repo_public_key():
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
    req = urllib.request.Request(url, headers=get_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def set_github_secret(secret_name: str, secret_value: str, key_id: str, public_key_b64: str):
    enc_val = encrypt_value(public_key_b64, secret_value)
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}"
    payload = json.dumps({"encrypted_value": enc_val, "key_id": key_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=get_headers(), method="PUT")
    with urllib.request.urlopen(req) as resp:
        if resp.status in (201, 204):
            print(f"  ✓ Secret '{secret_name}' successfully updated on GitHub.")

def sync_session_and_resume():
    print("=" * 60)
    print("Syncing Login Session & Resume to GitHub Cloud...")
    print("=" * 60)

    if not TOKEN:
        print("[!] Note: No GitHub token detected in git remote URL. Skipping cloud sync.")
        return False

    session_file = Path("session.json")
    if not session_file.exists():
        print("Error: session.json does not exist.")
        return False

    # 1. Fetch public key
    key_info = get_repo_public_key()
    key_id = key_info["key_id"]
    pub_key = key_info["key"]

    # 2. Sync session.json to NAUKRI_SESSION_B64
    session_b64 = base64.b64encode(session_file.read_bytes()).decode("utf-8")
    set_github_secret("NAUKRI_SESSION_B64", session_b64, key_id, pub_key)

    # 3. Encrypt resume if present
    resume_files = list(Path("resumes").glob("*.pdf")) + list(Path("resumes").glob("*.docx"))
    if resume_files:
        resume_file = resume_files[0]
        import secrets
        enc_pass = secrets.token_hex(16)
        enc_output = Path("resumes/resume.enc")

        subprocess.run([
            "openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
            "-in", str(resume_file), "-out", str(enc_output),
            "-pass", f"pass:{enc_pass}"
        ], check=True)

        set_github_secret("RESUME_PASSWORD", enc_pass, key_id, pub_key)

        subprocess.run(["git", "add", "resumes/resume.enc"], check=True)
        res = subprocess.run(["git", "diff", "--staged", "--quiet"])
        if res.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update encrypted resume"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("  ✓ Encrypted resume pushed to GitHub repository.")

    print("\n✓ SUCCESS: Your login session is synced with GitHub Actions!")
    print("GitHub will automatically run your profile updates twice daily (8 AM & 5 PM IST)")
    print("even when your laptop is completely turned off.")
    return True

if __name__ == "__main__":
    sync_session_and_resume()
