# 🤖 Gen-AI Slide Generator — Telegram Bot

AI-powered Telegram bot that generates professional PowerPoint presentations from screenshots/images using OCR.

---

## 🚀 Quick Start (Local)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Add your API keys

Create `.env`

```env
BOT_TOKEN=your_telegram_bot_token
GROUP_CHAT_ID=your_group_chat_id
```

> Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.

> Get your group chat ID by adding the bot to a group and visiting:

```bash
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

---

### 3. Install Tesseract OCR

Download and install:

```bash
https://github.com/UB-Mannheim/tesseract/wiki
```

Install path should be:

```bash
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

### 4. Add a logo

Place any image named `logo.jpg` in the project root folder.

---

### 5. Run

```bash
python main.py
```

---

## 💬 Bot Commands

| Command          | Description                                |
| ---------------- | ------------------------------------------ |
| `/start`         | Show welcome message & available commands  |
| `/set_title`     | Set the presentation title                 |
| `/set_topic`     | Set the topic name                         |
| `/set_teacher`   | Set the teacher/presenter name             |
| `/set_type`      | Set PPT type: `mcq` or `points`            |
| `/status`        | Check current settings                     |
| Send an image    | OCR extract questions or points from image |
| Type `nextlevel` | Generate and receive the `.pptx` file      |

---

## 🛠 Tech Stack

* **Python**
* **pyTelegramBotAPI** — Telegram bot framework
* **pytesseract** — OCR extraction
* **OpenCV** — Image preprocessing
* **python-pptx** — PowerPoint generation
* **Pillow** — Image handling

---

## 📁 Project Structure

```bash
Gen-AI-slide-generator/
├── main.py                       # Entry point
├── telegram_bot.py               # Bot logic & command handlers
├── ppt_generator.py              # MCQ slide builder
├── ai_presentation_generator.py  # Points slide builder
├── ocr.py                        # OCR handler for MCQ images
├── ocr_points_handler.py         # OCR handler for points images
├── validate_data.py              # Data validation helpers
├── config.py                     # Loads environment variables
├── requirements.txt
├── Procfile
├── .gitignore
└── .env.example
```

---

## 👨‍💻 Developed By

Anubhav Srivastava
