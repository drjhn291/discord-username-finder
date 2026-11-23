<div align="center">

# 🎯 Discord Username Finder

**A fast, resilient Python CLI tool to hunt for available 3–5 character alphanumeric Discord usernames with rarity-based Discord alerts, dual-webhook routing, and automatic rate-limit recovery.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Discord API](https://img.shields.io/badge/Discord_API-v9-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Charset](https://img.shields.io/badge/Charset-a--z%20%7C%200--9-00B894?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)

[Features](#-features) • [Rarity System & Preview](#-rarity-system--live-preview) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Presets](#-tuning--presets) • [Error Handling](#-http-status-handling)

</div>

---

## 📖 Overview

**Discord Username Finder** automates the search for short, rare Discord usernames (`3` to `5` characters combining lowercase letters `a–z` and digits `0–9`, such as `2la`, `9xk`, or `a4b7`). 

Built for stability during long scanning sessions, it separates **Available** and **Taken** results into dedicated Discord channels, highlights ultra-rare 3- and 4-character hits with instant `@everyone` pings, and dynamically adapts to Discord API rate limits and endpoint changes without crashing.

---

## ✨ Features

- **🎲 Alphanumeric Generator with Deduplication:** Randomly generates unique `3`, `4`, and `5`-character combinations (`a–z`, `0–9`) while tracking checked names in memory so no username is queried twice per session.
- **🏆 Rarity-Based Alert System:** Automatically classifies available usernames by length and customizes the Discord notification:
  - **3 Characters (Ultra Rare):** Gold embed (`#FFD700`) + `@everyone` instant alert.
  - **4 Characters (Rare):** Amber Gold embed (`#F1C40F`) + `@everyone` instant alert.
  - **5 Characters (Standard):** Clean Green embed (`#57F287`) with no ping spam.
- **🔀 Dual-Webhook Routing:** Routes hits and misses into two independent Discord channels (`AVAILABLE_WEBHOOK_URL` and `TAKEN_WEBHOOK_URL`) to keep your rare finds clean and organized.
- **🔄 Dual-Endpoint Architecture (Authed & Unauthed):**
  - Uses Discord's authenticated `users/@me/pomelo-attempt` endpoint when a `DISCORD_TOKEN` is configured.
  - Automatically strips expired/invalid tokens (`401` / `404`) and falls back to `unique-username/username-attempt-unauthed` seamlessly.
- **🛡️ Bulletproof Rate-Limit & Block Recovery:** Reads exact `retry_after` cooldowns on `429` responses (for both the Discord API and Webhooks) and gracefully handles `400` CAPTCHA challenges, `403` Cloudflare/verification blocks, and network drops.
- **💾 Real-Time Local Backup:** Every available username is immediately appended to `available.txt`.
- **🔒 Zero-Leak Credential Management:** Loads environment variables via `python-dotenv` with automatic whitespace/quote sanitization, while `.gitignore` keeps `.env` and `available.txt` out of Git.

---

## 🏆 Rarity System & Live Preview

### Discord Webhook Tiers

| Category | Condition | Embed Color | Ping | Webhook Destination |
| :--- | :--- | :---: | :---: | :--- |
| **🔥 Ultra Rare** | Available (`3 chars`, e.g. `2la`) | `🟨 #FFD700` (Gold) | `@everyone` | `AVAILABLE_WEBHOOK_URL` |
| **💎 Rare** | Available (`4 chars`, e.g. `x9zq`) | `🟧 #F1C40F` (Amber) | `@everyone` | `AVAILABLE_WEBHOOK_URL` |
| **✅ Standard** | Available (`5 chars`, e.g. `k7m2p`) | `🟩 #57F287` (Green) | *None* | `AVAILABLE_WEBHOOK_URL` |
| **❌ Taken** | Unavailable (any length) | `🟥 #ED4245` (Red) | *None* | `TAKEN_WEBHOOK_URL` |

### Console Output Example

```text
[*] Starting Discord Username Finder...
[*] .env loaded       : yes
[*] Lengths           : [3, 4, 5]
[*] Delay             : 2.1s
[*] Token             : yes
[*] Available Webhook : yes
[*] Taken Webhook     : yes

[1] [TAKEN]     qwe
[2] [TAKEN]     9x4z
[3] [RARE AVAILABLE - 3 CHARS] 2la | Total hits: 1
[4] [AVAILABLE] m4k9p | Total hits: 2
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/drjhn291/discord-username-finder.git
cd discord-username-finder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the template file to create your local `.env`:
```bash
cp .env.example .env
```

Open `.env` and paste your configuration (one variable per line, with no quotes or spaces around `=`):
```env
AVAILABLE_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_AVAILABLE_WEBHOOK_HERE
TAKEN_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_TAKEN_WEBHOOK_HERE
DISCORD_TOKEN=
```

### 4. Start Searching
```bash
python finder.py
```
Press `Ctrl + C` at any time to stop the scanner cleanly.

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Description |
| :--- | :---: | :--- |
| `AVAILABLE_WEBHOOK_URL` | Optional | Discord Webhook URL where **available** (3, 4, and 5-char) usernames are sent. |
| `TAKEN_WEBHOOK_URL` | Optional | Discord Webhook URL where **taken** usernames are logged. |
| `DISCORD_TOKEN` | Optional | Discord account token for authenticated checks (`pomelo-attempt`). Leave blank to run in unauthenticated mode. |

> [!TIP]
> **Minimalist Setup:** Both webhooks are optional. If you only want notifications when a free username is found, leave `TAKEN_WEBHOOK_URL=` empty. If both are left blank, results will still display in your terminal and save to `available.txt`.

### How to Create a Discord Webhook
1. Open a Discord server where you have **Manage Webhooks** permissions.
2. Go to **Server Settings → Integrations → Webhooks**.
3. Click **New Webhook**, choose your target channel, and click **Copy Webhook URL**.
4. Paste the URL into your `.env` file.

---

## 🎛️ Tuning & Presets

You can fine-tune the scanner by modifying the constants at the top of `finder.py`:

```python
LENGTHS = [3, 4, 5]                               # Username lengths to check
CHARSET = string.ascii_lowercase + string.digits  # Character pool (a–z, 0–9)
DELAY = 2.1                                       # Seconds between checks
TIMEOUT = 10                                      # HTTP request timeout in seconds
```

### Recommended Profiles

| Profile | `LENGTHS` | `DELAY` | Best Use Case |
| :--- | :---: | :---: | :--- |
| **Default (Balanced)** | `[3, 4, 5]` | `2.1` | Fast scanning bursts across all short lengths. |
| **Rare Hunter** | `[3, 4]` | `6.0` | Focusing exclusively on 3- and 4-character rare usernames. |
| **Stealth (Long-Run)** | `[4, 5]` | `10.0` | Running with a `DISCORD_TOKEN` for hours while minimizing `429` rate limits. |

---

## 📡 HTTP Status Handling

`finder.py` automatically interprets Discord API responses and recovers on the fly:

| Status | Meaning | Automated Response |
| :---: | :--- | :--- |
| **`200`** | Valid check completed | Logs result, appends hits to `available.txt`, and dispatches webhook embed. |
| **`400`** | Invalid format / CAPTCHA | Skips invalid strings or pauses `15s` if Discord triggers a `captcha_key`. |
| **`401`** | Invalid or expired token | Strips `Authorization` header and switches to unauthenticated mode. |
| **`403`** | Cloudflare / Account lock | Pauses `15s` before retrying (common on flagged mobile CGNAT IPs). |
| **`404`** | Authed endpoint unavailable | Falls back from `pomelo-attempt` to `username-attempt-unauthed`. |
| **`429`** | Rate limited | Parses exact `retry_after` timer and sleeps until cooldown expires. |

---

## 📁 Project Structure

```text
discord-username-finder/
├── finder.py          # Core scanner, rarity classifier, API client & webhook dispatcher
├── requirements.txt   # Python dependencies (requests, python-dotenv)
├── .env.example       # Safe template for environment variables
├── .gitignore         # Excludes .env and available.txt from Git commits
└── README.md          # Project documentation
```

---

## ⚠️ Security & Disclaimer

> [!WARNING]
> **Keep Your Credentials Private:** Never commit your `.env` file or share your `DISCORD_TOKEN` publicly. If you run in authenticated mode, always use a secondary account—rapid automated requests can trigger email or phone verification prompts.

This project is intended strictly for educational and research purposes. Automated querying of Discord's API may violate Discord's Terms of Service. Use responsibly and at your own risk.

---
## 📄 Support
* **Support:** If you find **Footprint Audit** useful, consider supporting future updates on [Ko-fi](https://ko-fi.com/drjhn291).

## 📄 License

Distributed under the **MIT License**.
