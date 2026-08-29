# Telegram View-Once & Disappearing Media Saver Bot 🚀

A powerful, high-performance Telegram Bot and Userbot designed to automatically save disappearing photos, self-destruct videos, view-once media, and private DM media directly to your Telegram Bot PM, Saved Messages, and Database Storage Channel.

Optimized to run **24/7 on Koyeb Free Tier** with an integrated Flask HTTP health check server.

---

## 🌟 Key Features

- 📸 **Save View-Once & Disappearing Media**: Automatically captures photos & videos with TTL (Time-To-Live) / self-destruct timers.
- 💬 **Reply-Trigger Save**: Reply to any view-once or restricted media message in your DMs to instantly save a permanent copy.
- 🔐 **Multi-User Interactive Telegram Login**: Any user can log in via `/login` inside Telegram (Phone number + Telegram OTP code + 2FA support) or by providing a Pyrogram Session String.
- 💾 **Multi-Destination Storage**: Permanent media copies are delivered to:
  1. Your Direct Chat with the Bot (Bot PM)
  2. Your Personal Telegram **Saved Messages**
  3. Private Database Storage Channel (`DB_CHANNEL`)
- 🛡 **Safe Account Operations**: Built with safe API limits and Pyrogram user session handling to ensure your Telegram ID remains completely safe from bans/freezes.
- ⚡ **Koyeb 24/7 Ready**: Built-in Flask web server health check on port `8080` / `$PORT` so Koyeb Web Services keep the bot active non-stop.

---

## 🛠 Commands

| Command | Description |
|---|---|
| `/start` | Start the bot and view feature menu |
| `/login` | Log in your Telegram account via OTP/Session String to activate view-once saver |
| `/logout` | Safely disconnect your account session and remove stored data |
| `/cancel` | Cancel an ongoing `/login` process |
| `/clear_batch` | Clear your saved batch files |
| `/status` | View total registered bot users (Owner Only) |
| `/broadcast` | Broadcast message to all registered users (Owner Only) |
| `/ban_user` | Ban a user from using the bot (Owner Only) |
| `/unban_user` | Unban a user (Owner Only) |
| `/banned_users` | List all banned users (Owner Only) |

---

## ⚙️ Environment Configuration Variables

Set these environment variables in Koyeb, Heroku, or your `.env` file:

| Variable | Description | Required |
|---|---|---|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | **Yes** |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | **Yes** |
| `BOT_TOKEN` | Bot Token from [@BotFather](https://t.me/BotFather) | **Yes** |
| `BOT_USERNAME` | Telegram Bot Username (without `@`) | **Yes** |
| `DATABASE_URL` | MongoDB Connection URI | **Yes** |
| `DB_CHANNEL` | Telegram Private Channel ID to store saved media | **Yes** |
| `BOT_OWNER` | Telegram Owner User ID | **Yes** |
| `LOG_CHANNEL` | Telegram Channel ID for bot log output | **Yes** |
| `AUTO_SAVE_VIEW_ONCE` | `True` to automatically save incoming DM view-once media | Optional (Default: `True`) |
| `SAVE_TO_SAVED_MESSAGES`| `True` to send copy to Telegram Saved Messages | Optional (Default: `True`) |
| `UPDATES_CHANNEL` | Channel ID for Force Subscribe | Optional |

---

## 🚀 How to Deploy on Koyeb (Free Tier 24/7)

1. Fork or push this repository to your GitHub account.
2. Sign in to [Koyeb](https://app.koyeb.com/).
3. Click **Create Service** -> Choose **GitHub**.
4. Select your repository.
5. Set the Service Type to **Web Service** (Port: `8080`).
6. Add all required Environment Variables listed above under **Environment Variables**.
7. Click **Deploy**. Koyeb will build the Docker container and keep your bot running 24/7!

---

## 🛡 Account Safety Guidelines

- The userbot only Listens to incoming DMs and replied messages to extract media files.
- It does **not** spam, mass message, or perform automated chat actions.
- Your session keys are securely stored in your private MongoDB database.

---

## 📄 License & Credits

- Built with [Pyrogram](https://docs.pyrogram.org) & [Python 3](https://www.python.org).
