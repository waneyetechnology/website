import os
import openai
from playwright.sync_api import sync_playwright

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
    html_blobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in sites:
            try:
                page.goto(url, timeout=20000)
                html = page.content()
                html_blobs.append(f"URL: {url}\n" + html[:20000])  # limit size for token safety
            except Exception:
                continue
        browser.close()
    prompt = (
        "You are a financial news assistant. "
        "Given the following HTML content from several major financial news websites, "
        "extract the top 5 most important financial or economics-related headlines. "
        "For each, return a JSON list of objects with 'headline' and 'url' fields. "
        "If a headline is not directly linked, do your best to infer the correct URL from the HTML. "
        "HTML content:\n" + "\n\n".join(html_blobs)
    )
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2
    )
    import json
    try:
        text = response.choices[0].message.content
        start = text.find("[")
        end = text.rfind("]") + 1
        headlines = json.loads(text[start:end])
        return headlines[:5]
    except Exception:
        return [
            {"headline": url, "url": url} for url in sites
        ]
