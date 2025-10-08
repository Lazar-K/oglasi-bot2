import os
from telegram import Bot

# Učitaj token iz okruženja (sigurnije nego direktno u kod)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")  # npr. "-1001234567890"

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("Nedostaje TELEGRAM_TOKEN ili CHANNEL_CHAT_ID!")

# Kreiraj bota
bot = Bot(token=TELEGRAM_TOKEN)

# Pošalji poruku
bot.send_message(chat_id=CHAT_ID, text="Zdravo 👋")
print("Poruka poslata!")
