import asyncio
import requests
from telegram import Bot
import os

# === PODESI OVO ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://efee.etf.unibl.org:8443/api/public/oglasne-ploce/1"
WEB_URL = "https://efee.etf.unibl.org/simple/oglasi/godina/1"

bot = Bot(token=TELEGRAM_TOKEN)
FILENAME = "sent_ads.txt"

async def get_first_year_ads():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()
    # filtriraj samo oglase sa Prve godine
    first_year_ads = [
        ad for ad in data
        if ad.get("oglasnaPloca", {}).get("id") == 1
    ]
    return first_year_ads

async def main():
    sent_ads = set()
    if os.path.exists(FILENAME):
        
        with open(FILENAME, "r", encoding="utf-8") as f:
            for line in f:
                sent_ads.add(line.strip())

    try:
        ads = await get_first_year_ads()
        new_ads = []

        for ad in ads:
           ad_id = str(ad.get("id"))
           if ad_id not in sent_ads:
            new_ads.append(ad)
            sent_ads.add(ad_id)

        # pošalji nove oglase
        for ad in new_ads:
         message = (
            f"🆕 <b>{ad['naslov']}</b>\n\n"      # bold naslov
            f"{ad['sadrzaj']}\n\n"              # sadržaj odvojen praznim linijama
            f"🔗 <a href='{WEB_URL}'>Detalji</a> "     # link na oglas u italiku
         )
         await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

         # upiši poslate id-ove u fajl
         with open(FILENAME, "w", encoding="utf-8") as f:
                for ad_id in sent_ads:
                    f.write(ad_id + "\n")

    except Exception as e:
            print("Greška:", e)


if __name__ == "__main__":
    asyncio.run(main())