import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://www.subito.it/annunci-italia/vendita/informatica/?q=raspberry+pi+5&shp=true"

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )

def main():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=20)

    print("Status code:", response.status_code)
    print("Final URL:", response.url)
    print("HTML length:", len(response.text))

    if response.status_code != 200:
        send_telegram(f"⚠️ Subito test fallito. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(" ", strip=True).lower()

    raspberry_count = text.count("raspberry")
    pi_count = text.count("pi 5")

    send_telegram(
        f"""🔎 Test Subito completato

Status code: {response.status_code}
Lunghezza HTML: {len(response.text)}
Parola 'raspberry' trovata: {raspberry_count} volte
Parola 'pi 5' trovata: {pi_count} volte

Link:
{URL}
"""
    )

if __name__ == "__main__":
    main()