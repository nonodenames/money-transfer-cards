from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

BASELINE_MONTHS = 14
BASELINE_FEE = 3.99

def parse_months(text):
    match = re.search(r'(\d+)\s*months?', text)
    return int(match.group(1)) if match else None

def parse_fee(text):
    match = re.search(r'([\d.]+)%\s*(fee|transfer)', text, re.I)
    return float(match.group(1)) if match else None

def check_money_transfer_cards():
    url = "https://www.moneysavingexpert.com/credit-cards/money-transfers/"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/115.0 Safari/537.36")
        page.goto(url, timeout=60000)
        page.wait_for_selector("body", timeout=20000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    offers = []

    cards = soup.select("article.card")
    for card in cards:
        name_el = card.select_one("h3.card-title")
        name = name_el.get_text(strip=True) if name_el else "Unnamed"

        text = card.get_text(separator=" ", strip=True)
        months = parse_months(text)
        fee = parse_fee(text)

        if months and fee:
            is_better = (months > BASELINE_MONTHS) or (months == BASELINE_MONTHS and fee < BASELINE_FEE)
            if is_better:
                offers.append({
                    "name": name,
                    "months": months,
                    "fee": fee,
                    "better": is_better
                })

    return offers

def main():
    print(f"\nBaseline: {BASELINE_MONTHS} months at {BASELINE_FEE}% fee\n")
    offers = check_money_transfer_cards()

    if offers:
        for offer in offers:
            print(f"✅ BETTER {offer['name']} — {offer['months']} months @ {offer['fee']}% fee")
    else:
        print("We haven't found any better than the Tesco card.")

if __name__ == "__main__":
    main()
