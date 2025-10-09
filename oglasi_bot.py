import asyncio
import aiohttp
from telegram import Bot
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === PODESI OVO ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_ID = os.getenv("SHEET_ID")  # Dodaj u GitHub Secrets

SERVICE_FILE = "service-account.json"
API_URL = "https://efee.etf.unibl.org:8443/api/public/oglasne-ploce/2"
PRILOG_URL = "https://efee.etf.unibl.org:8443/api/public/oglasi/"

bot = Bot(token=TELEGRAM_TOKEN)

# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

async def get_first_year_ads():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return [ad for ad in data if ad.get("oglasnaPloca", {}).get("id") == 2]

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

        for ad in new_ads:
            ad_id = ad['id']
            message = (
                f"🆕 <b>{ad['naslov']}</b>\n\n"
                f"{ad['sadrzaj']}\n\n"
            )
            
            prilozi = ad.get("oglasPrilozi", [])
            if prilozi:
                for prilog in prilozi:
                    naziv = prilog.get("originalniNaziv", "Prilog")
                    prilog_link = f"{PRILOG_URL}{ad_id}/download"
                    message += f"🔗 <a href='{prilog_link}'>{naziv}</a>\n"
            
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
            sheet.append_row([ad['id']])

    except Exception as e:
        print("Greška:", e)  # komentar odvojeno

if __name__ == "__main__":
    asyncio.run(main())
