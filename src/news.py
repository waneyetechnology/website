import os
import openai
import requests

def fetch_newsapi_headlines():
    api_key = os.environ.get("NEWSAPI_API_KEY")
    if not api_key:
        # Log a warning for debugging in CI/CD
        print("[WARN] NEWSAPI_API_KEY is not set or empty.")
        return []
    url = "https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=10&apiKey=" + api_key
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("articles", []):
                headlines.append({"headline": article["title"], "url": article["url"]})
    except Exception:
        return []
    return headlines

def fetch_fmp_headlines():
    api_key = os.environ.get("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/stock_news?limit=10&apikey={api_key}"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data:
                headlines.append({"headline": article["title"], "url": article["url"]})
    except Exception:
        return []
    return headlines

def fetch_marketaux_headlines():
    api_key = os.environ.get("MARKETAUX_API_KEY")
    url = f"https://api.marketaux.com/v1/news/all?language=en&filter_entities=true&api_token={api_key}&limit=10"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("data", []):
                headlines.append({"headline": article["title"], "url": article["url"]})
    except Exception:
        return []
    return headlines

def fetch_gnews_headlines():
    api_key = os.environ.get("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/top-headlines?topic=business&lang=en&token={api_key}&max=10"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("articles", []):
                headlines.append({"headline": article["title"], "url": article["url"]})
    except Exception:
        return []
    return headlines

def fetch_yahoo_finance_headlines():
    # Yahoo Finance does not have a free official API, so we use their RSS feed
    import xml.etree.ElementTree as ET
    url = "https://finance.yahoo.com/news/rssindex"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text
                headlines.append({"headline": title, "url": link})
    except Exception:
        return []
    return headlines

def fetch_financial_headlines():
    """
    Fetches top financial headlines from 5 sources/APIs, deduplicates and ranks them using LLM, and returns the top 5 significant headlines for a global financial overview.
    """
    import json
    all_headlines = []
    all_headlines += fetch_newsapi_headlines()
    all_headlines += fetch_fmp_headlines()
    all_headlines += fetch_marketaux_headlines()
    all_headlines += fetch_gnews_headlines()
    all_headlines += fetch_yahoo_finance_headlines()
    # Deduplicate and rank with LLM
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it in your environment or repository secrets.")
    client = openai.OpenAI(api_key=api_key)
    prompt = (
        "You are a financial news assistant. "
        "Given the following list of financial headlines (with URLs) from multiple reputable sources, "
        "deduplicate, filter, and select the top 10 most significant and globally relevant headlines that would help a trader make informed decisions. "
        "Return a JSON list of objects with 'headline' and 'url' fields.\n" + json.dumps(all_headlines, ensure_ascii=False)
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2
    )
    try:
        text = response.choices[0].message.content
        start = text.find("[")
        end = text.rfind("]") + 1
        headlines = json.loads(text[start:end])
        return headlines[:10]
    except Exception:
        return all_headlines[:10]
