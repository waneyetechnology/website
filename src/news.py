import os
import openai
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
from io import BytesIO

def fetch_financial_headlines():
    """
    Fetches the homepage HTML from major financial news sites using Playwright (headless browser),
    extracts all visible text and links, sends the text to OpenAI API, and extracts the top 5 financial/economics-related headlines with their URLs.
    """
    import re
    import json
    sites = [
        "https://www.cnn.com/business",
        "https://www.bloomberg.com",
        "https://www.ft.com",
        "https://www.reuters.com/finance",
        "https://www.cnbc.com/world/?region=world"
    ]
    results = []
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it in your environment or repository secrets.")
    import openai
    client = openai.OpenAI(api_key=api_key)
    for url in sites:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=20000)
                # Collect all text blocks with their hrefs
                text_blocks = []
                for el in page.query_selector_all('a'):
                    text = el.inner_text().strip()
                    href = el.get_attribute('href')
                    if text and href:
                        if not href.startswith('http'):
                            href = url.rstrip('/') + '/' + href.lstrip('/')
                        text_blocks.append({'text': text, 'url': href})
                # Limit to first 200 text blocks per site for token safety
                site_text = f"Source: {url}\n" + "\n".join([tb['text'] for tb in text_blocks[:200]])
                prompt = (
                    "You are a financial news assistant. "
                    "Given the following sentences (each with a link) from a financial news website, "
                    "extract the top 2 most important financial or economics-related headlines. "
                    "Return a JSON list of headline strings only.\n" + site_text
                )
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.2
                )
                try:
                    text = response.choices[0].message.content
                    start = text.find("[")
                    end = text.rfind("]") + 1
                    headlines = json.loads(text[start:end])
                except Exception:
                    headlines = [url]
                # Correlate headlines to URLs for this site
                for headline in headlines:
                    best_url = None
                    best_score = 0
                    for tb in text_blocks:
                        score = len(set(headline.lower().split()) & set(tb['text'].lower().split()))
                        if score > best_score:
                            best_score = score
                            best_url = tb['url']
                    results.append({"headline": headline, "url": best_url or url})
            except Exception:
                results.append({"headline": url, "url": url})
            finally:
                browser.close()
    return results[:5]
