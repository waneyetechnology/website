import requests
from datetime import datetime
from .log import logger

_BLS_BASE = "https://api.bls.gov/publicAPI/v1/timeseries/data"

# Static fallbacks used when live API calls fail
_FALLBACKS = {
    "US Unemployment Rate": ("4.2%",    "Recent",  4.2, 10.0, "neutral"),
    "US Core CPI (YoY)":    ("2.8% YoY","Recent",  2.8,  8.0, "neutral"),
    "US Nonfarm Payrolls":  ("+180K",   "Recent",  180, 700.0, "neutral"),
    "Eurozone HICP (YoY)":  ("2.2% YoY","Recent",  2.2,  8.0, "neutral"),
}


def _bls_fetch(series_id, years_back=2):
    """Fetch BLS time-series data for the past *years_back* calendar years.

    Filters out M13 (annual summary) rows and rows with a missing value ("-").
    Data is returned newest-first as the BLS API delivers it.
    """
    now = datetime.utcnow()
    end_year = now.year
    start_year = end_year - years_back

    resp = requests.get(
        f"{_BLS_BASE}/{series_id}",
        params={"startyear": str(start_year), "endyear": str(end_year)},
        timeout=15,
    )
    resp.raise_for_status()

    body = resp.json()
    if body.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS API error for {series_id}: {body.get('message', body.get('status'))}")

    raw = body["Results"]["series"][0]["data"]
    return [d for d in raw if d.get("period", "M13") != "M13" and d.get("value", "-") != "-"]


def _unemployment():
    """US Unemployment Rate — BLS series LNS14000000."""
    data = _bls_fetch("LNS14000000", years_back=1)
    latest = data[0]
    rate = float(latest["value"])
    date_str = f"{latest['periodName']} {latest['year']}"
    sentiment = "positive" if rate < 4.0 else ("negative" if rate > 5.5 else "neutral")
    return f"{rate}%", date_str, rate, 10.0, sentiment


def _core_cpi_yoy():
    """US Core CPI Year-over-Year — BLS series CUUR0000SA0L1E (index, not seasonally adjusted)."""
    data = _bls_fetch("CUUR0000SA0L1E", years_back=2)
    if len(data) < 13:
        raise ValueError("Not enough CPI data points for YoY calculation")

    latest = data[0]
    target_period = latest["period"]
    target_year_ago = str(int(latest["year"]) - 1)

    year_ago = next(
        (d for d in data if d["period"] == target_period and d["year"] == target_year_ago),
        None,
    )
    if year_ago is None:
        raise ValueError(f"Year-ago CPI data not found (period={target_period}, year={target_year_ago})")

    yoy = round((float(latest["value"]) / float(year_ago["value"]) - 1) * 100, 1)
    date_str = f"{latest['periodName']} {latest['year']}"
    sentiment = "negative" if yoy > 4.0 else ("positive" if yoy < 1.5 else "neutral")
    return f"{yoy}% YoY", date_str, min(abs(yoy), 8.0), 8.0, sentiment


def _nonfarm_payrolls():
    """US Nonfarm Payrolls monthly change — BLS series CES0000000001 (total, in thousands)."""
    data = _bls_fetch("CES0000000001", years_back=1)
    if len(data) < 2:
        raise ValueError("Not enough NFP data points")

    change = int(data[0]["value"]) - int(data[1]["value"])
    date_str = f"{data[0]['periodName']} {data[0]['year']}"
    prefix = "+" if change >= 0 else ""
    sentiment = "positive" if change > 100 else ("negative" if change < 0 else "neutral")
    return f"{prefix}{change:,}K", date_str, min(abs(change), 700), 700.0, sentiment


def _eurozone_hicp_yoy():
    """Eurozone HICP Year-over-Year — ECB Statistical Data Warehouse API (already a % value)."""
    url = "https://data-api.ecb.europa.eu/service/data/ICP/M.U2.N.000000.4.ANR"
    resp = requests.get(url, params={"lastNObservations": "1", "format": "jsondata"}, timeout=15)
    resp.raise_for_status()

    body = resp.json()
    ds = body["dataSets"][0]
    series = list(ds["series"].values())[0]
    obs = series["observations"]

    last_idx = str(max(int(k) for k in obs.keys()))
    yoy = float(obs[last_idx][0])

    time_values = body["structure"]["dimensions"]["observation"][0]["values"]
    idx = int(last_idx)
    period_label = time_values[idx]["name"] if idx < len(time_values) else "Latest"

    sentiment = "negative" if yoy > 4.0 else ("positive" if yoy < 1.5 else "neutral")
    return f"{yoy}% YoY", period_label, min(abs(yoy), 8.0), 8.0, sentiment


def fetch_economic_data():
    """Fetch key economic indicators from BLS (US) and ECB (Eurozone).

    Returns a list of dicts compatible with the Jinja2 template's Economic Indicators panel:
      event, value, date, numeric_value (clamped to max_value), max_value, unit, sentiment
    """
    fetchers = [
        ("US Unemployment Rate", _unemployment,      "%"),
        ("US Core CPI (YoY)",    _core_cpi_yoy,      "%"),
        ("US Nonfarm Payrolls",  _nonfarm_payrolls,  "K"),
        ("Eurozone HICP (YoY)",  _eurozone_hicp_yoy, "%"),
    ]

    indicators = []
    for name, fetcher, unit in fetchers:
        try:
            value_str, date_str, numeric_value, max_value, sentiment = fetcher()
            indicators.append({
                "event": name,
                "value": value_str,
                "date": date_str,
                "numeric_value": numeric_value,
                "max_value": max_value,
                "unit": unit,
                "sentiment": sentiment,
            })
            logger.info(f"Fetched economic indicator — {name}: {value_str} ({date_str})")
        except Exception as e:
            logger.warning(f"Failed to fetch {name}: {e} — using fallback")
            fb = _FALLBACKS[name]
            indicators.append({
                "event": name,
                "value": fb[0],
                "date": fb[1],
                "numeric_value": fb[2],
                "max_value": fb[3],
                "unit": unit,
                "sentiment": fb[4],
            })

    return indicators
