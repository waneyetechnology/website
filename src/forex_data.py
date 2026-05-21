import time
import requests
from .log import logger

# Major forex pairs with their Yahoo Finance symbol, typical market spread, and decimal precision
_FOREX_PAIRS = [
    {"symbol": "EURUSD=X", "pair": "EUR/USD", "spread": 0.0002, "decimals": 4},
    {"symbol": "GBPUSD=X", "pair": "GBP/USD", "spread": 0.0003, "decimals": 4},
    {"symbol": "USDJPY=X", "pair": "USD/JPY", "spread": 0.03,   "decimals": 2},
    {"symbol": "USDCHF=X", "pair": "USD/CHF", "spread": 0.0003, "decimals": 4},
    {"symbol": "AUDUSD=X", "pair": "AUD/USD", "spread": 0.0003, "decimals": 4},
    {"symbol": "USDCAD=X", "pair": "USD/CAD", "spread": 0.0004, "decimals": 4},
    {"symbol": "NZDUSD=X", "pair": "NZD/USD", "spread": 0.0004, "decimals": 4},
    {"symbol": "EURGBP=X", "pair": "EUR/GBP", "spread": 0.0002, "decimals": 4},
    {"symbol": "EURJPY=X", "pair": "EUR/JPY", "spread": 0.04,   "decimals": 2},
    {"symbol": "GBPJPY=X", "pair": "GBP/JPY", "spread": 0.05,   "decimals": 2},
]

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

_FALLBACK_DATA = [
    {"pair": "EUR/USD", "bid": 1.0850, "ask": 1.0852, "change": 0.0},
    {"pair": "GBP/USD", "bid": 1.2650, "ask": 1.2653, "change": 0.0},
    {"pair": "USD/JPY", "bid": 155.20, "ask": 155.23, "change": 0.0},
    {"pair": "USD/CHF", "bid": 0.9050, "ask": 0.9053, "change": 0.0},
    {"pair": "AUD/USD", "bid": 0.6450, "ask": 0.6453, "change": 0.0},
    {"pair": "USD/CAD", "bid": 1.3750, "ask": 1.3754, "change": 0.0},
]


def _fetch_yahoo_quote(symbol):
    """Fetch a single forex quote from Yahoo Finance v8 chart API.
    Returns (price, prev_close) or raises on failure.
    """
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

    prev_close = meta.get("chartPreviousClose")
    if prev_close is None and price is not None:
        closes = [c for c in result["indicators"]["quote"][0].get("close", []) if c is not None]
        prev_close = closes[-2] if len(closes) >= 2 else price

    return price, prev_close


def fetch_forex_cfd_data():
    """Fetch live forex pair quotes from Yahoo Finance.

    Returns a list of dicts with keys: pair, bid, ask, change.
    Falls back to last-known hardcoded values if all fetches fail.
    """
    results = []

    for pair_info in _FOREX_PAIRS:
        try:
            price, prev_close = _fetch_yahoo_quote(pair_info["symbol"])
            if price is None:
                logger.warning(f"No price returned for {pair_info['pair']}, skipping")
                continue

            decimals = pair_info["decimals"]
            half_spread = pair_info["spread"] / 2
            bid = round(price - half_spread, decimals)
            ask = round(price + half_spread, decimals)
            change = round(price - (prev_close if prev_close is not None else price), decimals)

            results.append({"pair": pair_info["pair"], "bid": bid, "ask": ask, "change": change})
            time.sleep(0.1)  # avoid hammering the endpoint

        except Exception as e:
            logger.warning(f"Failed to fetch {pair_info['pair']}: {e}")

    if results:
        logger.info(f"Fetched {len(results)}/{len(_FOREX_PAIRS)} forex pairs from Yahoo Finance")
        return results

    logger.error("All forex pair fetches failed, returning fallback data")
    return _FALLBACK_DATA
