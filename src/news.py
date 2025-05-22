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
    for url in sites:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=20000)
                # Extract visible headlines and their URLs from the DOM
                headlines = []
                # Try h1, h2, h3, and prominent a tags
                for selector in ["h1", "h2", "h3", "a[aria-label*='headline']", "a[data-analytics*='headline']", "a.headline", "a.card-title", "a.story-title", "a.title"]:
                    for el in page.query_selector_all(selector):
                        text = el.inner_text().strip()
                        href = el.get_attribute("href")
                        # Only consider non-empty, non-navigation headlines
                        if text and len(text) > 25 and not text.lower().startswith("sign in"):
                            # Make href absolute
                            if href and not href.startswith("http"):
                                href = url.rstrip("/") + "/" + href.lstrip("/")
                            if href and href.startswith("http"):
                                headlines.append({"headline": text, "url": href})
                # Fallback: try just h1/h2/h3 if nothing found
                if not headlines:
                    for tag in ["h1", "h2", "h3"]:
                        for el in page.query_selector_all(tag):
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
    for item in all_headlines:
        if item['headline'] not in seen:
            unique_headlines.append(item)
            seen.add(item['headline'])
    # Optionally, use LLM to filter or rank the headlines
    api_key = os.environ.get("OPENAI_API_KEY")
    use_llm = api_key is not None and len(unique_headlines) > 5
    if use_llm:
        import openai
        client = openai.OpenAI(api_key=api_key)
        import json
        # Prepare a prompt with the extracted headlines
        prompt = (
            "You are a financial news assistant. "
            "Given the following list of financial/economics-related headlines (with URLs), "
            "select and return the top 5 most important and up-to-date headlines as a JSON list of objects with 'headline' and 'url' fields. "
            "Headlines list:\n" + json.dumps(unique_headlines, ensure_ascii=False)
        )
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )
            text = response.choices[0].message.content
            start = text.find("[")
            end = text.rfind("]") + 1
            headlines = json.loads(text[start:end])
            return headlines[:5]
        except Exception:
            pass  # fallback to non-LLM headlines
    return unique_headlines[:5]
