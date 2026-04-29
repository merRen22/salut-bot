# SalutBot 🇫🇷

**SalutBot** is a private French language tutor hosted on Telegram. It helps a small group of authorized users improve their French by enforcing daily writing goals and providing AI-powered grammatical corrections and stylistic suggestions.

## Tech Stack

* **Language:** Python 3.12
* **Framework:** [aiogram 3.x](https://docs.aiogram.dev/) (Asynchronous Telegram Bot API)
* **AI Engine:** Open router (Grammar, Style & Naturalness analysis)
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
├── requirements.txt    # aiogram, aiosqlite, google-generativeai
└── .dockerignore
```

## 🛡️ Security Measures

1. **Invisible Firewall:** The bot uses Long Polling. This means your VPS initiates the connection to Telegram. You do not need to open any inbound ports (like 80 or 443) on your VPS for the bot to function.

2. **Encrypted Secrets:** The OpenRouter API key and Telegram Token are never committed to Git; they are managed exclusively via GitHub Secrets and Dokploy Environment Variables.

3. **Strict Whitelisting:** Even if your bot's username is discovered, only IDs present in your salutbot.db can interact with the AI logic.

4. **No Docker Port Mapping:** Since the bot has no web server, do not map any ports in your Docker configuration. This keeps the container completely isolated from inbound internet traffic.

## 🚀 Local Setup & Initialization

1. **Identify your ID**

Message @userinfobot on Telegram to get your numerical ID (and your family member's ID).

2. **Bootstrap the DB**

Before your first deployment, create the folder and insert your admin user manually to ensure you have access immediately:

```bash
# Create the local data directory
mkdir -p data

# Create the schema
sqlite3 data/salutbot.db "CREATE TABLE users (telegram_id INTEGER PRIMARY KEY, name TEXT, min_words INTEGER, is_active BOOLEAN);"

# Insert yourself as the admin (replace 12345678 with your actual ID)
sqlite3 data/salutbot.db "INSERT INTO users VALUES (12345678, 'Admin', 15, 1);"
```

3. **Install & Run**

```bash
# Clone & Install
pip install -r requirements.txt

# Create your .env with your keys
cp .env.example .env 

# Run locally for testing
python -m src.main
```

