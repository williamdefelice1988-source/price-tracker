import os
import re
import statistics
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEARCH_URL = "https://www.ebay.de/sch/i.html?_nkw=raspberry+pi+5+8gb&_sop=15"
DISCOUNT_ALERT = 0.15

EXCLUDE_WORDS = [
    "case", "gehäuse", "cover", "kabel", "cable", "netzteil",
    "cooler", "lüfter", "fan", "sd", "microsd", "zubehör",
    "defekt", "broken", "for parts", "empty box", "nur verpackung"
]

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )

def parse_price(text):
    match = re.search(r"EUR\s*([\d.,]+)", text)
    if not match:
        return None
    value = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None

def main():
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(SEARCH_URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = []

    for result in soup.select(".s-item"):
        title_tag = result.select_one(".s-item__title")
        price_tag = result.select_one(".s-item__price")
        link_tag = result.select_one(".s-item__link")

        if not title_tag or not price_tag or not link_tag:
            continue

        title = title_tag.get_text(" ", strip=True)
        price_text = price_tag.get_text(" ", strip=True)
        link = link_tag.get("href")

        title_lower = title.lower()

        if "raspberry" not in title_lower or "5" not in title_lower or "8gb" not in title_lower:
            continue

        if any(word in title_lower for word in EXCLUDE_WORDS):
            continue

        price = parse_price(price_text)

        if price is None:
            continue

        if price < 40 or price > 300:
            continue

        items.append({
            "title": title,
            "price": price,
            "link": link
        })

    if len(items) < 3:
        send_telegram("⚠️ Tracker eBay: pochi risultati trovati per Raspberry Pi 5 8GB.")
        return

    prices = [item["price"] for item in items]
    avg_price = statistics.mean(prices)
    alert_price = avg_price * (1 - DISCOUNT_ALERT)

    deals = [item for item in items if item["price"] <= alert_price]

    print(f"Risultati validi: {len(items)}")
    print(f"Prezzo medio: {avg_price:.2f}")
    print(f"Soglia alert: {alert_price:.2f}")

    if deals:
        best = sorted(deals, key=lambda x: x["price"])[0]

        message = f"""🔥 Affare Raspberry trovato!

Prodotto:
{best['title']}

Prezzo: {best['price']:.2f} €
Media eBay: {avg_price:.2f} €
Soglia alert: {alert_price:.2f} €

Link:
{best['link']}
"""
        send_telegram(message)
    else:
        print("Nessun affare trovato.")

if __name__ == "__main__":
    main()
