import logging
from telegram_bot import TelegramBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    logging.info("Starting Gen-AI Slide Generator Bot...")
    bot = TelegramBot()
    bot.start()
