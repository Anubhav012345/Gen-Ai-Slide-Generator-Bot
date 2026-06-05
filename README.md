# 🤖 Gen-AI Slide Generator — Telegram Bot

An AI-powered Telegram bot that generates professional PowerPoint presentations from images using OCR + GPT.

---

## 🚀 Quick Start (Local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API keys
Open `config.py` and replace the placeholder values:
```python
BOT_TOKEN      = "your_telegram_bot_token"
GROUP_CHAT_ID  = "your_group_chat_id"
OPENAI_API_KEY = "your_openai_api_key"
```

> Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.  
> Get your group chat ID by adding the bot to a group and visiting:  
> `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`

### 3. Add a logo
Place any image named `logo.jpg` in the project root folder.

### 4. Run
```bash
python main.py
```

---

## 💬 Bot Commands

| Command | Description |
|---|---|
| `/start` | Show welcome message & available commands |
| `/set_title` | Set the presentation title |
| `/set_topic` | Set the topic name |
| `/set_teacher` | Set the teacher/presenter name |
| `/set_type` | Set PPT type: `mcq` or `points` |
| `/status` | Check current settings |
| Send an image | OCR-extract questions or points from the image |
| Type `nextlevel` | Generate and receive the `.pptx` file |

---

## 🛠 Tech Stack

- **Python**
- **pyTelegramBotAPI** — Telegram bot framework
- **EasyOCR** — Multilingual OCR (English + Hindi)
- **OpenAI GPT-4o-mini** — AI content parsing & generation
- **python-pptx** — PowerPoint generation
- **OpenCV** — Image preprocessing

---

## ☁️ Deploy on Railway (Free Hosting)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables in the **Variables** tab:
   - `BOT_TOKEN`
   - `GROUP_CHAT_ID`
   - `OPENAI_API_KEY`
4. Railway auto-deploys. Your bot runs 24/7 🎉

> ⚠️ `config.py` is in `.gitignore` — it will NOT be pushed to GitHub.  
> On Railway, use the Variables tab instead.

---

## 📁 Project Structure

```
Gen-AI-slide-generator/
├── main.py                       # Entry point
├── telegram_bot.py               # Bot logic & command handlers
├── ppt_generator.py              # MCQ slide builder
├── ai_presentation_generator.py  # Bullet-point slide builder (AI)
├── ocr.py                        # OCR handler for MCQ images
├── ocr_points_handler.py         # OCR handler for points images
├── validate_data.py              # Data validation helpers
├── config.py                     # API keys (NOT pushed to GitHub)
├── requirements.txt
├── Procfile                      # For Railway deployment
├── .gitignore
└── .env.example                  # Key template (safe to share)
```
