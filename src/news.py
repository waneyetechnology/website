import requests

def fetch_financial_headlines():
    html = requests.get("https://www.cnn.com").text
    # ... LLM API call as in your existing code ...
    # For demo, return mock data:
    return [
        {"headline": "US Fed raises rates by 0.25%", "url": "https://cnn.com/fed-news"},
        {"headline": "ECB signals policy shift", "url": "https://cnn.com/ecb-news"},
        {"headline": "US jobs data beats expectations", "url": "https://cnn.com/jobs-news"},
        {"headline": "Oil prices surge on supply fears", "url": "https://cnn.com/oil-news"},
        {"headline": "Dollar strengthens against Euro", "url": "https://cnn.com/dollar-news"},
    ]
