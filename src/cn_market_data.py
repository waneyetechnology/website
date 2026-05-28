"""
Chinese Market Data Module

Fetches:
- A-share market indices: Shanghai Composite, Shenzhen Component, ChiNext,
  STAR50, CSI 300
- Hong Kong: Hang Seng Index
- PBoC policy rates (LPR 1Y and 5Y)
- Chinese economic indicators: CPI, PPI, PMI, GDP, M2, social financing
"""

import re
import time
import requests
from ..log import logger

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# ─── MARKET INDICES ───────────────────────────────────────────────────────────

_CN_INDICES = [
    {"symbol": "000001.SS", "name": "上证综指",      "name_en": "Shanghai Composite"},
    {"symbol": "399001.SZ", "name": "深证成指",      "name_en": "Shenzhen Component"},
    {"symbol": "399006.SZ", "name": "创业板指",      "name_en": "ChiNext"},
    {"symbol": "000300.SS", "name": "沪深300",       "name_en": "CSI 300"},
    {"symbol": "000688.SS", "name": "科创50",        "name_en": "STAR50"},
    {"symbol": "^HSI",      "name": "恒生指数",      "name_en": "Hang Seng"},
    {"symbol": "^HSCE",     "name": "国企指数",      "name_en": "H-Shares"},
]


def _fetch_yahoo_quote(symbol):
    """Fetch single quote from Yahoo Finance v8 chart API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    resp = requests.get(
        url,
        headers=_HEADERS,
        params={"interval": "1d", "range": "5d", "includePrePost": "false"},
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json()["chart"]["result"][0]
    meta = result["meta"]

    price = meta.get("regularMarketPrice")
    if price is None:
        closes = [c for c in result["indicators"]["quote"][0].get("close", []) if c is not None]
        price = closes[-1] if closes else None

    prev = meta.get("chartPreviousClose")
    if prev is None and price is not None:
        closes = [c for c in result["indicators"]["quote"][0].get("close", []) if c is not None]
        prev = closes[-2] if len(closes) >= 2 else price

    return price, prev


def fetch_cn_market_indices():
    """
    Fetch Chinese market index data from Yahoo Finance.
    Returns list of dicts compatible with template rendering.
    """
    results = []
    for idx in _CN_INDICES:
        try:
            price, prev = _fetch_yahoo_quote(idx["symbol"])
            if price is None:
                continue

            change = price - prev if prev else 0
            pct = (change / prev * 100) if prev else 0
            sign = "+" if change >= 0 else ""
            direction = "up" if change > 0 else ("down" if change < 0 else "flat")

            results.append({
                "symbol": idx["symbol"],
                "name": idx["name"],
                "name_en": idx["name_en"],
                "price": f"{price:,.2f}",
                "change": f"{sign}{change:,.2f}",
                "change_pct": f"{sign}{pct:.2f}%",
                "direction": direction,
                "numeric_change_pct": round(pct, 2),
            })
            time.sleep(0.2)  # Rate limiting
        except Exception as e:
            logger.warning(f"Failed to fetch {idx['symbol']}: {e}")

    logger.info(f"Fetched {len(results)} CN market indices")
    return results


# ─── PBoC POLICY RATES ────────────────────────────────────────────────────────

# Static fallback rates (updated to latest known values)
_PBOC_FALLBACK = [
    {"indicator": "LPR 1年期", "value": "3.10%", "indicator_en": "LPR 1Y"},
    {"indicator": "LPR 5年期", "value": "3.60%", "indicator_en": "LPR 5Y"},
    {"indicator": "存款准备金率(大型)", "value": "9.50%", "indicator_en": "RRR Large Banks"},
    {"indicator": "存款准备金率(中小型)", "value": "7.50%", "indicator_en": "RRR Small Banks"},
]


def fetch_pboc_rates():
    """
    Fetch PBoC LPR rates from official PBoC website or fallback to static values.
    Returns list of dicts: {"indicator", "value", "indicator_en"}
    """
    try:
        # Try to scrape PBoC LPR page
        url = "http://www.pbc.gov.cn/zhengcehuobisi/125207/125213/125440/125838/125888/index.html"
        resp = requests.get(url, headers={**_HEADERS, "Accept": "text/html"}, timeout=15)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "gb2312"
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.select("table tr")
            rates = {}
            for row in rows[:10]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    label = cells[0].get_text(strip=True)
                    value = cells[-1].get_text(strip=True)
                    if "1年" in label:
                        rates["1Y"] = value
                    elif "5年" in label:
                        rates["5Y"] = value

            if rates:
                result = []
                if "1Y" in rates:
                    result.append({"indicator": "LPR 1年期", "value": rates["1Y"], "indicator_en": "LPR 1Y"})
                if "5Y" in rates:
                    result.append({"indicator": "LPR 5年期", "value": rates["5Y"], "indicator_en": "LPR 5Y"})
                if result:
                    logger.info(f"Fetched PBoC LPR rates: {result}")
                    return result + _PBOC_FALLBACK[2:]  # Add RRR from fallback
    except Exception as e:
        logger.warning(f"PBoC rates fetch error: {e}")

    logger.info("Using PBoC fallback rates")
    return _PBOC_FALLBACK


# ─── CHINESE ECONOMIC INDICATORS ─────────────────────────────────────────────

_ECON_FALLBACK = [
    {"event": "GDP增速(同比)", "value": "5.0%", "date": "近期", "numeric_value": 5.0, "max_value": 10.0, "unit": "%", "sentiment": "positive"},
    {"event": "CPI(同比)",     "value": "0.1%", "date": "近期", "numeric_value": 0.1, "max_value": 8.0,  "unit": "%", "sentiment": "neutral"},
    {"event": "PPI(同比)",     "value": "-2.2%","date": "近期", "numeric_value": 2.2, "max_value": 10.0, "unit": "%", "sentiment": "negative"},
    {"event": "制造业PMI",     "value": "50.4", "date": "近期", "numeric_value": 50.4,"max_value": 60.0, "unit": "",  "sentiment": "positive"},
    {"event": "M2增速(同比)",  "value": "7.0%", "date": "近期", "numeric_value": 7.0, "max_value": 20.0, "unit": "%", "sentiment": "neutral"},
]


def _fetch_nbstat_cpi():
    """
    Attempt to fetch CPI from NBS (National Bureau of Statistics) data API.
    Returns (value_str, date_str, numeric, max_val, sentiment) or raises.
    """
    # NBS API endpoint for CPI monthly data
    url = "https://data.stats.gov.cn/easyquery.htm"
    params = {
        "m": "QueryData",
        "dbcode": "hgjnd",
        "rowcode": "zb",
        "colcode": "sj",
        "wds": "[]",
        "dfwds": '[{"wdcode":"zb","valuecode":"A01010101"}]',
        "k1": str(int(time.time() * 1000)),
    }
    headers = {
        **_HEADERS,
        "Accept": "application/json",
        "Referer": "https://data.stats.gov.cn/",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("returndata", {}).get("datanodes", [])
    if rows:
        latest = rows[0]
        val = float(latest.get("data", {}).get("strdata", "100")) - 100
        period = latest.get("wds", [{}])[0].get("valuecode", "近期")
        sentiment = "negative" if val > 3.0 else ("positive" if val < 0.5 else "neutral")
        return f"{val:+.1f}%", period, min(abs(val), 8.0), 8.0, sentiment
    raise ValueError("No NBS CPI data found")


def _fetch_nbstat_pmi():
    """Attempt to fetch Manufacturing PMI from NBS."""
    url = "https://data.stats.gov.cn/easyquery.htm"
    params = {
        "m": "QueryData",
        "dbcode": "hgjnd",
        "rowcode": "zb",
        "colcode": "sj",
        "wds": "[]",
        "dfwds": '[{"wdcode":"zb","valuecode":"A0K0103"}]',
        "k1": str(int(time.time() * 1000)),
    }
    headers = {**_HEADERS, "Referer": "https://data.stats.gov.cn/"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("returndata", {}).get("datanodes", [])
    if rows:
        val = float(rows[0].get("data", {}).get("strdata", "50"))
        period = rows[0].get("wds", [{}])[0].get("valuecode", "近期")
        sentiment = "positive" if val >= 50 else "negative"
        return f"{val:.1f}", period, min(val, 60), 60.0, sentiment
    raise ValueError("No NBS PMI data found")


def fetch_cn_economic_data():
    """
    Fetch key Chinese economic indicators.
    Returns a list of dicts for template rendering (same structure as economic_data.py).
    """
    indicators = []

    # Try live NBS data, fall back to static
    for name, fetcher, unit, fallback in [
        ("CPI(同比)", _fetch_nbstat_cpi, "%", _ECON_FALLBACK[1]),
        ("制造业PMI", _fetch_nbstat_pmi, "", _ECON_FALLBACK[3]),
    ]:
        try:
            value_str, date_str, numeric, max_val, sentiment = fetcher()
            indicators.append({
                "event": name,
                "value": value_str,
                "date": date_str,
                "numeric_value": numeric,
                "max_value": max_val,
                "unit": unit,
                "sentiment": sentiment,
            })
        except Exception as e:
            logger.warning(f"Live CN econ fetch failed for {name}: {e}, using fallback")
            indicators.append(fallback)

    # Add remaining static indicators (GDP, PPI, M2)
    for fb in [_ECON_FALLBACK[0], _ECON_FALLBACK[2], _ECON_FALLBACK[4]]:
        if not any(i["event"] == fb["event"] for i in indicators):
            indicators.append(fb)

    # Sort to consistent order
    order = ["GDP增速(同比)", "CPI(同比)", "PPI(同比)", "制造业PMI", "M2增速(同比)"]
    indicators.sort(key=lambda x: order.index(x["event"]) if x["event"] in order else 99)

    logger.info(f"CN economic indicators: {[i['event'] for i in indicators]}")
    return indicators


# ─── PBoC "ECONOMY AT A GLANCE" (equivalent of Fed glance data) ──────────────

def fetch_pboc_economy_at_glance():
    """
    Returns key PBoC/SAFE data snapshot items.
    Format mirrors fetch_fed_economy_at_glance: [{"indicator": ..., "value": ...}]
    """
    data = [
        {"indicator": "LPR 1年期",  "value": "3.10%"},
        {"indicator": "LPR 5年期",  "value": "3.60%"},
        {"indicator": "人民币中间价", "value": _fetch_rmb_midrate()},
        {"indicator": "外汇储备",    "value": "3.24万亿美元"},
    ]
    return data


def _fetch_rmb_midrate():
    """Fetch USD/CNY mid-rate from SAFE or Yahoo Finance."""
    try:
        price, _ = _fetch_yahoo_quote("USDCNY=X")
        if price:
            return f"{price:.4f}"
    except Exception:
        pass
    return "7.25"  # fallback
