from .log import logger

def fetch_economic_data():
    """
    Fetch key economic data with values formatted for visualization.
    """
    return [
        {
            "event": "US Nonfarm Payrolls",
            "value": "+250K",
            "date": "2025-05-20",
            "numeric_value": 250,
            "max_value": 500,  # A reasonable max for NFP to show progress against
            "unit": "K",
            "sentiment": "positive"
        },
        {
            "event": "Eurozone CPI",
            "value": "2.1% YoY",
            "date": "2025-05-19",
            "numeric_value": 2.1,
            "max_value": 5.0,  # A reasonable max for CPI
            "unit": "%",
            "sentiment": "neutral"
        },
    ]
