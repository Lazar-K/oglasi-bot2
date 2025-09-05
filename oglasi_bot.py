import asyncio
import requests
from telegram import Bot
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === PODESI OVO ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_ID = os.getenv("SHEET_ID")  # Dodaj u GitHub Secrets

SERVICE_FILE = "service-account.json"
API_URL = "https://efee.etf.unibl.org:8443/api/public/oglasne-ploce/1"
WEB_URL = "https://efee.etf.unibl.org/simple/oglasi/godina/1"

bot = Bot(token=TELEGRAM_TOKEN)

# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

async def get_first_year_ads():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()
    # filtriraj samo oglase sa Prve godine
    return [
        ad for ad in data
        if ad.get("oglasnaPloca", {}).get("id") == 1
    ]

async def main():
    sent_ads = set(sheet.col_values(1))
    
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
         sheet.append_row([ad['id']])

    except Exception as e:
            print("Greška:", e)


if __name__ == "__main__":
    asyncio.run(main())
