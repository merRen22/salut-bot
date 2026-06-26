# SalutBot 🇫🇷

**SalutBot** is a private French language tutor hosted on Telegram. It helps a small group of authorized users improve their French by enforcing daily writing goals and providing AI-powered grammatical corrections and stylistic suggestions.

## Tech Stack

* **Language:** Python 3.12
* **Framework:** [aiogram 3.x](https://docs.aiogram.dev/) (Asynchronous Telegram Bot API)
* **AI Engine:** OpenRouter (GPT-4o-mini) for grammar, style & naturalness analysis
* **Database:** [aiosqlite](https://github.com/omnilib/aiosqlite) (Asynchronous SQLite for persistent user settings and history)
* **Deployment:** [Dokploy](https://dokploy.com/) (Self-hosted PaaS) on Linode VPS
* **CI/CD:** GitHub Actions + Docker

## 🛠️ Key Features

* **Whitelist Protection:** A dedicated middleware checks every incoming message against the `users` table. If the Telegram ID isn't registered and active, the bot ignores the request.
* **Personalized Constraints:** Individual minimum word counts per user (e.g., 15 words for a beginner, 40 words for advanced practice).
* **AI Linguistic Feedback:** * **Corrections:** Fixes grammar, conjugation, and spelling errors.
    * **Explanations:** Brief notes on *why* a change was made (e.g., gender agreement or verb tense).
    * **Vocabulary Boosts:** Suggestions for more precise or natural French synonyms.
* **Persistence:** All user settings and daily progress are saved in a volume-mapped SQLite database, ensuring data survives container updates.

## 📊 Database Schema

The database initializes automatically on the first run. The core table is `users`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `telegram_id` | INTEGER (PK) | Unique numerical ID from Telegram. |
| `name` | TEXT | Display name for the user. |
| `min_words` | INTEGER | The minimum word count required for this user's daily message. |
| `is_active` | BOOLEAN | Access toggle (1 = Whitelisted, 0 = Blocked). |

## 🔑 Environment Variables

Add these to your **Dokploy Service Environment Variables**:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPEN_ROUTER_API_KEY=your_open_router_ai_key
DATABASE_PATH=/app/data/salutbot.db
```

## 📦 Deployment & Persistence
**1. Persistent Volumes (Dokploy)**

Since SQLite is file-based, you must mount a persistent volume in Dokploy to prevent data loss when pushing new code. If you don't do this, every time you deploy a new version via GitHub, your database (and your French practice history) will be wiped clean.

* **Type:** Volume (or Bind Mount)
* **Host Path:** `<HOST_PATH_ON_VPS>` (This is where the file lives on your Linode VPS)
* **Mount Path:** /app/data (This is where the bot looks for it inside the container)

**2. CI/CD with GitHub Actions**

Every push to main builds a new Docker image, pushes it to the GitHub Container Registry (GHCR), and notifies Dokploy to pull the latest version and restart.

```yaml
name: Build and Deploy
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          
      - name: Trigger Dokploy Webhook
        run: curl -X POST ${{ secrets.DOKPLOY_WEBHOOK_URL }}
```

## **📂 Project Structure**

A modular structure ensures that the "Gatekeeper" (middleware) and the "Brains" (OpenRouter) are easy to maintain.

```
├── .github/workflows/  # GitHub Actions CI/CD
├── src/
│   ├── database/       # aiosqlite connection and CRUD logic
│   ├── handlers/       # Bot commands and message processing
│   ├── middlewares/    # The AccessControl (Whitelist) middleware
│   ├── services/       # OpenRouter AI API wrapper (Linguistic logic)
│   └── main.py         # Entry point (Bot polling setup)
├── Dockerfile          # Optimized Python multistage build
├── requirements.txt    # aiogram, aiosqlite, httpx, python-dotenv
└── .dockerignore
```

## 🛡️ Security Measures

1. **Invisible Firewall:** The bot uses Long Polling. This means your VPS initiates the connection to Telegram. You do not need to open any inbound ports (like 80 or 443) on your VPS for the bot to function.

2. **Encrypted Secrets:** The OpenRouter API key and Telegram Token are never committed to Git; they are managed exclusively via GitHub Secrets and Dokploy Environment Variables.

3. **Strict Whitelisting:** Even if your bot's username is discovered, only IDs present in your salutbot.db can interact with the AI logic.

4. **No Docker Port Mapping:** Since the bot has no web server, do not map any ports in your Docker configuration. This keeps the container completely isolated from inbound internet traffic.

## 🚀 Local Setup

### 1. Prerequisites

- Python 3.12+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- An OpenRouter API key (from [openrouter.ai/keys](https://openrouter.ai/keys))

### 2. Identify your Telegram ID

Message [@userinfobot](https://t.me/userinfobot) on Telegram to get your numerical ID.

### 3. Bootstrap the database

The schema is created automatically on first run, but you need to insert yourself as a whitelisted user:

```bash
mkdir -p data
sqlite3 data/salutbot.db "INSERT INTO users VALUES (<YOUR_TELEGRAM_ID>, 'Admin', 15, 1);"
```

### 4. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPEN_ROUTER_API_KEY=your_open_router_ai_key
DATABASE_PATH=data/salutbot.db
```

### 6. Run

```bash
python -m src.main
```

### 7. Chat with the bot

Search for your bot username on Telegram (e.g., `@frenchTutorDevBot`) and hit **Start**. Send a message in French to receive corrections.

### Troubleshooting

**Polling conflict (`Conflict: terminated by other getUpdates request`)**

This means another instance is already polling the same bot token. Stop any other running instances, then:

```bash
python -c "
import httpx, os
from dotenv import load_dotenv
load_dotenv()
r = httpx.get(f'https://api.telegram.org/bot{os.getenv(\"TELEGRAM_BOT_TOKEN\")}/deleteWebhook?drop_pending_updates=true')
print(r.json())
"
```

Wait a few seconds and try again. Only one bot instance can run per token.

