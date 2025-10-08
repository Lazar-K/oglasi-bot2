import os
from telegram import Bot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN ili CHAT_ID nije postavljen!")

bot = Bot(token=TELEGRAM_TOKEN)
bot.send_message(chat_id=CHAT_ID, text="Zdravo 👋")
