from .log import logger

def fetch_forex_cfd_data():
    """
    Fetch forex data with mock changes for visualization.
    In a real application, this would be calculated from a live data stream.
    """
    return [
        {
            "pair": "EUR/USD",
            "bid": 1.0850,
            "ask": 1.0852,
            "change": -0.0002,
        },
        {
            "pair": "USD/JPY",
            "bid": 155.20,
            "ask": 155.23,
            "change": 0.05,
        },
    ]
