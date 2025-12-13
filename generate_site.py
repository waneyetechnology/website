import argparse
from src import fetch_financial_headlines, fetch_central_bank_policies, fetch_central_bank_rates, fetch_fed_economy_at_glance, fetch_economic_data, fetch_forex_cfd_data, generate_html
from src.news import cleanup_old_images
from src.log import logger

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate financial news website')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with limited headlines for faster CI/CD builds')
    args = parser.parse_args()

    if args.test_mode:
        logger.info("Running in test mode - limiting headlines per source for faster builds")

    news_data = fetch_financial_headlines(test_mode=args.test_mode)
    # Extract headlines and analysis from the new return format
    news = news_data['headlines'] if isinstance(news_data, dict) else news_data
    financial_analysis = news_data.get('analysis') if isinstance(news_data, dict) else None

    # Clean up images that are no longer associated with current headlines
    cleanup_old_images(news)

    rates_data = fetch_central_bank_rates()
    fed_econ_data = fetch_fed_economy_at_glance()
    econ = fetch_economic_data()
    forex = fetch_forex_cfd_data()
    html = generate_html(news, rates_data, econ, forex, fed_econ_data, financial_analysis)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    if args.test_mode:
        print("index.html generated in test mode (limited data for CI/CD).")
    else:
        print("index.html generated.")

if __name__ == "__main__":
    main()
