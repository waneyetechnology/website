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
    all_headlines = []
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it in your environment or repository secrets.")
    client = openai.OpenAI(api_key=api_key)
    import json
    for url in sites:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=20000)
                html = page.content()
                # Only send a small portion of the HTML to the LLM
                html_snippet = html[:5000]
                prompt = (
                    f"You are a financial news assistant. Given the following HTML content from a financial news website, "
                    f"extract the top 2 most important financial or economics-related headlines. "
                    f"For each, return a JSON list of objects with 'headline' and 'url' fields. "
                    f"If a headline is not directly linked, do your best to infer the correct URL from the HTML. "
                    f"HTML content from {url}:\n" + html_snippet
                )
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.2
                )
                text = response.choices[0].message.content
                start = text.find("[")
                end = text.rfind("]") + 1
                headlines = json.loads(text[start:end])
                all_headlines.extend(headlines)
            except Exception:
                # fallback: add the site itself as a headline
                all_headlines.append({"headline": url, "url": url})
            finally:
                browser.close()
    # Deduplicate by headline text, keep order
    seen = set()
    unique_headlines = []
    for item in all_headlines:
        if item['headline'] not in seen:
            unique_headlines.append(item)
            seen.add(item['headline'])
    return unique_headlines[:5]
