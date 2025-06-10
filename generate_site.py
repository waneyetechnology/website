from src import fetch_financial_headlines, fetch_central_bank_policies, fetch_central_bank_rates, fetch_economic_data, fetch_forex_cfd_data, generate_html
from src.log import logger

def main():
    news = fetch_financial_headlines()
    rates_data = fetch_central_bank_rates()
    econ = fetch_economic_data()
    forex = fetch_forex_cfd_data()
    html = generate_html(news, rates_data, econ, forex)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html generated.")

if __name__ == "__main__":
    main()
