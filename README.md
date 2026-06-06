# 🤖 Gen-AI Slide Generator — Telegram Bot

AI-powered Telegram bot that generates professional PowerPoint presentations
from images (OCR) or `.txt` / `.md` files using Google Gemini AI.

---

## 🚀 Quick Start (Local)

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

> **Windows only:** Also install Tesseract OCR:
> Download from https://github.com/UB-Mannheim/tesseract/wiki
> Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
>
> **Linux/Render:** Tesseract is installed automatically via system packages.
> Add this to your Render service → Settings → **Build Command**:
> `apt-get install -y tesseract-ocr && pip install -r requirements.txt`

---

### 2. Create your `.env` file

```env
BOT_TOKEN=your_telegram_bot_token
GROUP_CHAT_ID=your_group_chat_id
GEMINI_API_KEY=your_gemini_api_key
```

> **BOT_TOKEN** → Get from [@BotFather](https://t.me/BotFather)
>
> **GROUP_CHAT_ID** → Add bot to a group, then visit:
> `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
>
> **GEMINI_API_KEY** → Get from https://aistudio.google.com/app/apikey

---

### 3. Run locally

```bash
python main.py
```

---

## ☁️ Deploying to Render

1. Push your code to GitHub (make sure `venv/` and `.env` are in `.gitignore`)
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set **Build Command:**
   ```
   apt-get install -y tesseract-ocr && pip install -r requirements.txt
   ```
5. Set **Start Command:**
   ```
   python main.py
   ```
6. Add these **Environment Variables** in Render dashboard:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | your Telegram bot token |
| `GEMINI_API_KEY` | your Gemini API key |
| `GROUP_CHAT_ID` | your group chat ID |

---

## 💬 Bot Commands & Usage

| Command / Action | Description |
|---|---|
| `/start` | Show welcome message |
| `/set_title` | Set the presentation title |
| `/set_topic` | Set the topic name |
| `/set_teacher` | Set the teacher/presenter name |
| `/set_type` | Set PPT type: `mcq` or `points` |
| `/status` | Check current settings |
| Send a **photo** | OCR-extract questions or points from image |
| Send a **.txt or .md file** | Parse Markdown content into slides (points mode) |
| Type `nextlevel` | Generate and receive the `.pptx` file |

### 💡 Recommended workflow for "points" mode

Instead of screenshotting a document, **send the `.txt` file directly**:

1. `/set_type` → enter `points`
2. `/set_topic` → enter your topic name
3. Attach your `.txt` or `.md` file (use paperclip → File in Telegram)
4. Type `nextlevel` to generate the presentation

The bot reads `##` headings as slide titles and paragraphs as bullet points automatically.

---

## 🛠 Tech Stack

| Library | Purpose |
|---|---|
| `pyTelegramBotAPI` | Telegram bot framework |
| `google-genai` | Google Gemini AI for MCQ extraction |
| `pytesseract` + `easyocr` | OCR text extraction from images |
| `opencv-python-headless` | Image preprocessing |
| `python-pptx` | PowerPoint generation |
| `Pillow` | Image handling |

---

## 📁 Project Structure

```
Gen-AI-slide-generator/
├── main.py                    # Entry point + health check server
├── telegram_bot.py            # Bot logic, command & file handlers
├── ppt_generator.py           # Slide builder (MCQ + points)
├── ocr.py                     # OCR handler for MCQ images
├── ocr_points_handler.py      # OCR + Markdown parser for points
├── validate_data.py           # Gemini AI data extraction
├── config.py                  # Loads environment variables
├── requirements.txt
├── Procfile
├── .gitignore
└── .env.example
```

---

## 👨‍💻 Developed By

Anubhav Srivastava