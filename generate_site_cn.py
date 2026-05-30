import argparse
import os
from src.cn_market_data import fetch_cn_market_indices, fetch_pboc_rates, fetch_cn_economic_data, fetch_pboc_economy_at_glance
from src.cn_htmlgen import generate_cn_html
from src.news.cn_news_fetcher import fetch_cn_financial_headlines, cleanup_old_cn_images
from src.log import logger


def main():
    parser = argparse.ArgumentParser(description='Generate Chinese financial news website')
    parser.add_argument('--test-mode', action='store_true',
                        help='Run in test mode with limited headlines for faster CI/CD builds')
    args = parser.parse_args()

    if args.test_mode:
        logger.info("CN site: running in test mode — limiting headlines per source")

    # Ensure output directory exists
    os.makedirs("cn", exist_ok=True)

    # Fetch Chinese news + DeepSeek analysis
    news_data = fetch_cn_financial_headlines(test_mode=args.test_mode)
    news = news_data['headlines'] if isinstance(news_data, dict) else news_data
    financial_analysis = news_data.get('analysis') if isinstance(news_data, dict) else None

    # Clean up stale CN headline images
    cleanup_old_cn_images(news)

    # Fetch Chinese market data
    indices = fetch_cn_market_indices()
    pboc_rates = fetch_pboc_rates()
    econ = fetch_cn_economic_data()
    pboc_economy = fetch_pboc_economy_at_glance()

    # Render HTML
    html = generate_cn_html(news, pboc_rates, econ, indices, pboc_economy, financial_analysis)

    with open("cn/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    if args.test_mode:
        print("cn/index.html generated in test mode (limited data for CI/CD).")
    else:
        print("cn/index.html generated.")


if __name__ == "__main__":
    main()
