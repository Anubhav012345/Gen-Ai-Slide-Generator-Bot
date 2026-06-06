import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
GROUP_CHAT_ID  = os.environ.get("GROUP_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set! Add it to your .env file.")
