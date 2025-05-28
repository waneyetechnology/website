import os
import openai
import requests
from .log import logger

def fetch_newsapi_headlines():
    api_key = os.environ.get("NEWSAPI_API_KEY")
    if not api_key:
        # Log a warning for debugging in CI/CD
        logger.warning("NEWSAPI_API_KEY is not set or empty.")
        return []
    url = "https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=10&apiKey=" + api_key
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("articles", []):
                # Use publishedAt if available
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedAt")
                })
        else:
            logger.warning(f"NewsAPI request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from NewsAPI")
    logger.info(f"NewsAPI headlines: {headlines}")
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
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedDate")
                })
        else:
            logger.warning(f"FMP request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"FMP fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from FMP")
    logger.info(f"FMP headlines: {headlines}")
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
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("published_at")
                })
        else:
            logger.warning(f"Marketaux request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Marketaux fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Marketaux")
    logger.info(f"Marketaux headlines: {headlines}")
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
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedAt")
                })
        else:
            logger.warning(f"GNews request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"GNews fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from GNews")
    logger.info(f"GNews headlines: {headlines}")
    return headlines

def fetch_yahoo_finance_headlines():
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://finance.yahoo.com/news/rssindex"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text
                pubdate = item.find("pubDate")
                publishedAt = None
                if pubdate is not None:
                    try:
                        publishedAt = parsedate_to_datetime(pubdate.text).isoformat()
                    except Exception:
                        publishedAt = pubdate.text
                headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"Yahoo Finance RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Yahoo Finance fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Yahoo Finance RSS")
    logger.info(f"Yahoo Finance headlines: {headlines}")
    return headlines

def llm_filter_headlines(headlines, api_key, top_n=3):
    import json
    from datetime import datetime, timedelta
    # Remove headlines older than 3 days if possible
    now = datetime.utcnow()
    filtered = []
    for h in headlines:
        dt = h.get("publishedAt")
        try:
            if dt:
                dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00')) if 'T' in dt else datetime.strptime(dt, "%a, %d %b %Y %H:%M:%S %Z")
                if now - dt_obj > timedelta(days=3):
                    continue
        except Exception:
            logger.debug(f"Could not parse date for headline: {h}")
        filtered.append(h)
    # Sort by recency if possible
    filtered = sorted(filtered, key=lambda x: x.get('publishedAt', ''), reverse=True)
    logger.info(f"Filtering {len(filtered)} headlines with LLM for top {top_n}")
    client = openai.OpenAI(api_key=api_key)
    prompt = (
        f"You are a trading research assistant. Given the following list of financial headlines (with URLs), "
        f"deduplicate, filter, and select the top {top_n} most significant and globally relevant headlines. "
        "If multiple headlines are equally significant, always prefer the most recent ones. "
        "Return a JSON list of objects with 'headline' and 'url' fields.\n" + json.dumps(filtered, ensure_ascii=False)
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
        filtered_llm = json.loads(text[start:end])
        logger.info(f"LLM returned {len(filtered_llm)} headlines.")
        return filtered_llm[:top_n]
    except Exception as e:
        logger.error(f"LLM filter error: {e}")
        return filtered[:top_n]

def fetch_financial_headlines():
    """
    Fetches top financial headlines from 5 sources/APIs, applies LLM filter to each source to get top 3, then combines them and returns the top 10 significant headlines for a global financial overview. No final LLM deduplication is performed.
    """
    import json
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it in your environment or repository secrets.")
    all_headlines = []
    # Apply LLM filter to each source
    all_headlines += llm_filter_headlines(fetch_newsapi_headlines(), api_key, top_n=3)
    all_headlines += llm_filter_headlines(fetch_fmp_headlines(), api_key, top_n=3)
    all_headlines += llm_filter_headlines(fetch_marketaux_headlines(), api_key, top_n=3)
    all_headlines += llm_filter_headlines(fetch_gnews_headlines(), api_key, top_n=3)
    all_headlines += llm_filter_headlines(fetch_yahoo_finance_headlines(), api_key, top_n=3)
    # Return the combined headlines directly (no final LLM deduplication)
    return all_headlines[:10]
