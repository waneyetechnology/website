import os
import openai
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
from io import BytesIO

def fetch_financial_headlines():
    """
    Fetches the homepage HTML from major financial news sites using Playwright (headless browser),
    sends the content to OpenAI API, and extracts the top 5 financial/economics-related headlines with their URLs.
    """
    # List of popular financial news sites
    sites = [
        "https://www.cnn.com/business",
        "https://www.bloomberg.com",
        "https://www.ft.com",
        "https://www.reuters.com/finance",
        "https://www.cnbc.com/world/?region=world"
    ]
    all_headlines = []
    for url in sites:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=20000)
                headlines = []
                # Screenshot headline elements and run OCR
                for selector in ["h1", "h2", "h3", "a[aria-label*='headline']", "a[data-analytics*='headline']", "a.headline", "a.card-title", "a.story-title", "a.title"]:
                    for el in page.query_selector_all(selector):
                        # Screenshot the element
                        try:
                            img_bytes = el.screenshot(type="png")
                            img = Image.open(BytesIO(img_bytes))
                            text = pytesseract.image_to_string(img).strip()
                        except Exception:
                            text = el.inner_text().strip()
                        href = el.get_attribute("href")
                        if text and len(text) > 25 and not text.lower().startswith("sign in"):
                            if href and not href.startswith("http"):
                                href = url.rstrip("/") + "/" + href.lstrip("/")
                            if href and href.startswith("http"):
                                headlines.append({"headline": text, "url": href})
                # Fallback: try just h1/h2/h3 if nothing found
                if not headlines:
                    for tag in ["h1", "h2", "h3"]:
                        for el in page.query_selector_all(tag):
                            try:
                                img_bytes = el.screenshot(type="png")
                                img = Image.open(BytesIO(img_bytes))
                                text = pytesseract.image_to_string(img).strip()
                            except Exception:
                                text = el.inner_text().strip()
                            if text and len(text) > 25:
                                headlines.append({"headline": text, "url": url})
                all_headlines.extend(headlines[:2])  # Take top 2 per site
            except Exception:
                all_headlines.append({"headline": url, "url": url})
            finally:
                browser.close()
    # Deduplicate by headline text, keep order
    seen = set()
    unique_headlines = []
    # Filtering: ignore navigation/privacy/marketing and prefer financial keywords
    ignore_keywords = [
        "privacy", "opt-out", "explore", "event", "unusual activity", "sign in", "your computer network", "choices", "cookie", "advert", "subscribe", "newsletter", "sale of personal information"
    ]
    financial_keywords = [
        "market", "stock", "inflation", "fed", "ecb", "economy", "gdp", "rate", "oil", "dollar", "bond", "cpi", "jobs", "unemployment", "central bank", "policy", "forex", "currency", "trade", "recession", "growth", "earnings", "nasdaq", "s&p", "dow", "euro", "yen", "gold", "crypto", "bitcoin", "ipo", "merger", "acquisition"
    ]
    for item in all_headlines:
        headline_lower = item['headline'].lower()
        if any(kw in headline_lower for kw in ignore_keywords):
            continue
        if not any(kw in headline_lower for kw in financial_keywords):
            continue
        if item['headline'] not in seen:
            unique_headlines.append(item)
            seen.add(item['headline'])
    # Do NOT use LLM for filtering or ranking for now
    return unique_headlines[:5]
