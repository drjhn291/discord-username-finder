import os
import random
import string
import time
from dotenv import load_dotenv
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)


def clean_env(value: str | None) -> str:
    if not value:
        return ""
    cleaned = value.strip().strip('"').strip("'")
    if cleaned.lower().startswith("authorization:"):
        cleaned = cleaned.split(":", 1)[1].strip()
    if "YOUR_" in cleaned:
        return ""
    return cleaned


AVAILABLE_WEBHOOK_URL = clean_env(os.getenv("AVAILABLE_WEBHOOK_URL"))
TAKEN_WEBHOOK_URL = clean_env(os.getenv("TAKEN_WEBHOOK_URL"))
TOKEN = clean_env(
    os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or os.getenv("AUTH_TOKEN")
)

# Configuration
LENGTHS = [3, 4, 5]
CHARSET = string.ascii_lowercase + string.digits
DELAY = 2.1
TIMEOUT = 10

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}
if TOKEN:
    HEADERS["Authorization"] = TOKEN


def generate_random_name() -> str:
    length = random.choice(LENGTHS)
    return "".join(random.choices(CHARSET, k=length))


def check_username(name: str) -> bool | None:
    global TOKEN
    url = (
        "https://discord.com/api/v9/users/@me/pomelo-attempt"
        if TOKEN
        else "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
    )

    while True:
        try:
            resp = requests.post(
                url, json={"username": name}, headers=HEADERS, timeout=TIMEOUT
            )

            if resp.status_code == 200:
                return not resp.json().get("taken", True)

            if resp.status_code == 429:
                wait = float(resp.json().get("retry_after", 5)) + 0.5
                print(f"[429 API] Rate limited — waiting {wait:.1f}s...")
                time.sleep(wait)
                continue

            if resp.status_code in (401, 404) and TOKEN:
                reason = (
                    "Invalid or expired token"
                    if resp.status_code == 401
                    else "Authed endpoint unavailable (404)"
                )
                print(f"[!] {reason} — switching to unauthed mode...")
                TOKEN = ""
                HEADERS.pop("Authorization", None)
                url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
                continue

            if resp.status_code == 400:
                data = resp.json() if resp.content else {}
                if "captcha_key" in data:
                    print("[400 API] Discord requested a CAPTCHA — waiting 15s...")
                    time.sleep(15)
                    return None
                return False

            if resp.status_code == 403:
                data = (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                msg = data.get(
                    "message",
                    "Blocked by Cloudflare or account verification required",
                )
                print(f"[403 API] {msg} — waiting 15s...")
                time.sleep(15)
                return None

            print(f"[{resp.status_code} API] Unexpected response — waiting 10s...")
            time.sleep(10)
            return None
        except requests.RequestException as e:
            print(f"[Network Error] {e} — retrying in 5s...")
            time.sleep(5)


def send_to_webhook(name: str, available: bool):
    webhook_url = AVAILABLE_WEBHOOK_URL if available else TAKEN_WEBHOOK_URL
    if not webhook_url:
        return

    length = len(name)
    content = None
    description = None

    if available:
        if length == 3:
            title = "🔥 ULTRA RARE 3-CHAR AVAILABLE! 🔥"
            color = 0xFFD700  # Gold
            rarity = "Ultra Rare (3 chars)"
            content = f"@everyone 🚨 **3-character username found:** `{name}`"
            description = "Claim this immediately before someone else takes it!"
        elif length == 4:
            title = "💎 RARE 4-CHAR AVAILABLE! 💎"
            color = 0xF1C40F  # Amber Gold
            rarity = "Rare (4 chars)"
            content = f"@everyone ✨ **4-character username found:** `{name}`"
            description = "Short 4-character username ready to claim!"
        else:
            title = "✅ AVAILABLE"
            color = 0x57F287  # Green
            rarity = "Standard (5+ chars)"
    else:
        title = "❌ TAKEN"
        color = 0xED4245  # Red
        rarity = None

    fields = [
        {"name": "Username", "value": f"`{name}`", "inline": True},
        {"name": "Length", "value": str(length), "inline": True},
        {
            "name": "Status",
            "value": "Available" if available else "Unavailable",
            "inline": True,
        },
    ]

    if rarity:
        fields.append({"name": "Rarity", "value": rarity, "inline": False})

    embed = {
        "title": title,
        "color": color,
        "fields": fields,
        "footer": {"text": "discord-finder"},
    }
    if description:
        embed["description"] = description

    payload = {"embeds": [embed]}
    if content:
        payload["content"] = content

    while True:
        try:
            resp = requests.post(webhook_url, json=payload, timeout=TIMEOUT)
            if resp.status_code == 429:
                wait = float(resp.json().get("retry_after", 2)) + 0.5
                print(f"[429 Webhook] Rate limited — waiting {wait:.1f}s...")
                time.sleep(wait)
                continue
            break
        except requests.RequestException as e:
            print(f"[Webhook Error] {e}")
            break


def run():
    print("[*] Starting Discord Username Finder...")
    print(
        f"[*] .env loaded       : {'yes' if os.path.exists(ENV_PATH) else 'NO (missing .env)'}"
    )
    print(f"[*] Lengths           : {LENGTHS}")
    print(f"[*] Delay             : {DELAY}s")
    print(f"[*] Token             : {'yes' if TOKEN else 'no'}")
    print(f"[*] Available Webhook : {'yes' if AVAILABLE_WEBHOOK_URL else 'no'}")
    print(f"[*] Taken Webhook     : {'yes' if TAKEN_WEBHOOK_URL else 'no'}\n")

    if not AVAILABLE_WEBHOOK_URL and not TAKEN_WEBHOOK_URL:
        print(
            "[!] WARNING: Both webhook URLs are empty. Results will only show in"
            " console.\n"
        )

    checked = set()
    total = 0
    hits = 0

    while True:
        name = generate_random_name()
        if name in checked:
            continue
        checked.add(name)

        available = check_username(name)
        if available is None:
            continue

        total += 1
        if available:
            hits += 1
            tag = (
                f"[RARE AVAILABLE - {len(name)} CHARS]"
                if len(name) in (3, 4)
                else "[AVAILABLE]"
            )
            print(f"[{total}] {tag} {name} | Total hits: {hits}")
            with open("available.txt", "a", encoding="utf-8") as f:
                f.write(name + "\n")
        else:
            print(f"[{total}] [TAKEN]     {name}")

        send_to_webhook(name, available)
        time.sleep(DELAY)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[*] Stopped by user.")