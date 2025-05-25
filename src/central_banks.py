import requests

def fetch_central_bank_policies():
    """
    Fetches the latest policy statements, rate decisions, and monetary policy outlooks for the 9 most important central banks for traders.
    Returns a list of dicts: {"bank": ..., "policy": ...}
    """
    banks = [
        {"name": "Federal Reserve", "country": "United States", "code": "fed", "url": "https://www.federalreserve.gov/monetarypolicy.htm"},
        {"name": "European Central Bank", "country": "Eurozone", "code": "ecb", "url": "https://www.ecb.europa.eu/press/pr/date/latest/html/index.en.html"},
        {"name": "Bank of England", "country": "United Kingdom", "code": "boe", "url": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes"},
        {"name": "Bank of Japan", "country": "Japan", "code": "boj", "url": "https://www.boj.or.jp/en/mopo/mpmdeci/index.htm/"},
        {"name": "Swiss National Bank", "country": "Switzerland", "code": "snb", "url": "https://www.snb.ch/en/iabout/stat/statpub/zirefi/id/statpub_zirefi_hist"},
        {"name": "Bank of Canada", "country": "Canada", "code": "boc", "url": "https://www.bankofcanada.ca/press/press-releases/"},
        {"name": "Reserve Bank of Australia", "country": "Australia", "code": "rba", "url": "https://www.rba.gov.au/media-releases/"},
        {"name": "People's Bank of China", "country": "China", "code": "pboc", "url": "http://www.pbc.gov.cn/english/130721/index.html"},
        {"name": "Reserve Bank of New Zealand", "country": "New Zealand", "code": "rbnz", "url": "https://www.rbnz.govt.nz/news"},
    ]
    # For now, fetch the latest press release headline for each bank (as a placeholder for real scraping/LLM extraction)
    policies = []
    for bank in banks:
        try:
            resp = requests.get(bank["url"], timeout=10)
            if resp.ok:
                # Simple extraction: get the first <title> or <h1>/<h2> tag as the latest policy headline
                text = resp.text
                import re
                match = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE)
                title = match.group(1).strip() if match else "Latest policy update not found."
                # Try to get a headline from h1/h2 if available
                match2 = re.search(r'<h[12][^>]*>(.*?)</h[12]>', text, re.IGNORECASE)
                if match2:
                    title = match2.group(1).strip()
                policies.append({"bank": bank["name"], "policy": title, "url": bank["url"]})
            else:
                policies.append({"bank": bank["name"], "policy": "Could not fetch latest policy.", "url": bank["url"]})
        except Exception:
            policies.append({"bank": bank["name"], "policy": "Error fetching policy.", "url": bank["url"]})
    return policies
