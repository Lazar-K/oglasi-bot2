import asyncio
import os
import requests
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("✅ Python pokrenut")

# === PROVJERA ENVIRONMENT PROMENLJIVIH ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_ID = os.getenv("SHEET_ID")

print(f"🔑 TELEGRAM_TOKEN: {'POSTOJI' if TELEGRAM_TOKEN else 'NE POSTOJI'}")
print(f"🔑 CHAT_ID: {'POSTOJI' if CHAT_ID else 'NE POSTOJI'}")
print(f"🔑 SHEET_ID: {'POSTOJI' if SHEET_ID else 'NE POSTOJI'}")

if not all([TELEGRAM_TOKEN, CHAT_ID, SHEET_ID]):
    raise ValueError("❌ Nedostaje jedna ili više environment promenljivih!")

# === INICIJALIZACIJA BOTA ===
bot = Bot(token=TELEGRAM_TOKEN)

# === TEST PORUKA — vidiš odmah da li radi bot ===
async def test_message():
    try:
        await bot.send_message(chat_id=CHAT_ID, text="✅ Bot je uspješno pokrenut u GitHub Actions!")
        print("📨 Test poruka poslata na Telegram.")
    except Exception as e:
        print("❌ Ne mogu poslati test poruku:", e)
        raise

# === GOOGLE SHEETS SETUP ===
SERVICE_FILE = "service-account.json"
if not os.path.exists(SERVICE_FILE):
    raise FileNotFoundError("❌ service-account.json fajl ne postoji!")

try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    print("✅ Uspješno povezan sa Google Sheets.")
except Exception as e:
    print("❌ Greška pri povezivanju sa Google Sheets:", e)
    raise

# === URL-OVI ===
API_URL = "https://efee.etf.unibl.org:8443/api/public/oglasne-ploce/2"
PRILOG_URL = "https://efee.etf.unibl.org:8443/api/public/oglasi/"

# === FUNKCIJE ===
async def get_first_year_ads():
    print("📡 Preuzimam oglase sa servera...")
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        print(f"✅ Primljeno {len(data)} oglasa sa servera.")
        return [ad for ad in data if ad.get("oglasnaPloca", {}).get("id") == 1]
    except Exception as e:
        print("❌ Greška pri preuzimanju oglasa:", e)
        return []


async def main():
    await test_message()  # testiraj da li bot uopšte može slati poruke

    print("📄 Učitavam već poslate oglase iz Google Sheets...")
    try:
        sent_ads = set(sheet.col_values(1))
        print(f"✅ Nađeno {len(sent_ads)} već poslatih oglasa.")
    except Exception as e:
        print("❌ Greška pri čitanju iz Sheets:", e)
        sent_ads = set()

    ads = await get_first_year_ads()
    new_ads = []

    for ad in ads:
        ad_id = str(ad.get("id"))
        if ad_id not in sent_ads:
            new_ads.append(ad)
            sent_ads.add(ad_id)

    print(f"🆕 Pronađeno {len(new_ads)} novih oglasa.")

    for ad in new_ads:
        ad_id = ad["id"]
        naslov = ad.get("naslov", "Bez naslova")
        sadrzaj = ad.get("sadrzaj", "")
        message = f"🆕 <b>{naslov}</b>\n\n{sadrzaj}\n\n"

        prilozi = ad.get("oglasPrilozi", [])
        if prilozi:
            for prilog in prilozi:
                naziv = prilog.get("originalniNaziv", "Prilog")
                prilog_link = f"{PRILOG_URL}{ad_id}/download"
                message += f"🔗 <a href='{prilog_link}'>{naziv}</a>\n"

        print(f"📤 Šaljem oglas: {naslov}")
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
            sheet.append_row([ad_id])
            print("✅ Poslato i upisano u Google Sheets.")
        except Exception as e:
            print(f"❌ Greška pri slanju oglasa {ad_id}:", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("🎯 Skripta završena.")
    except Exception as e:
        print("❌ Greška u glavnom programu:", e)

