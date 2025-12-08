"""
SEO functionality for Waneye financial website
"""
import json
from datetime import datetime
from .log import logger
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def generate_meta_tags(news_data, econ_data):
    """Generate comprehensive meta tags for SEO"""

    # Extract keywords from headlines
    keywords = extract_keywords_from_news(news_data)

    # Generate description based on current financial data
    description = generate_dynamic_description(news_data, econ_data)

    meta_tags = {
        'description': description,
        'keywords': ', '.join(keywords),
        'author': 'Waneye Technology',
        'robots': 'index, follow',
        'googlebot': 'index, follow',
        'language': 'en',
        'distribution': 'global',
        'rating': 'general',
        'revisit-after': '1 day',

        # Open Graph tags for social media
        'og:title': 'Waneye - Real-Time Financial News & Market Analysis',
        'og:description': description,
        'og:type': 'website',
        'og:url': 'https://waneye.com',
        'og:site_name': 'Waneye Financial',
        'og:image': 'https://waneye.com/static/images/waneye-og-image.jpg',
        'og:image:width': '1200',
        'og:image:height': '630',
        'og:locale': 'en_US',

        # Twitter Card tags
        'twitter:card': 'summary_large_image',
        'twitter:site': '@WaneyeTech',
        'twitter:creator': '@WaneyeTech',
        'twitter:title': 'Waneye - Financial News & Market Data',
        'twitter:description': description,
        'twitter:image': 'https://waneye.com/static/images/waneye-twitter-card.jpg',

        # Additional SEO tags
        'theme-color': '#eaf6ff',
        'msapplication-TileColor': '#eaf6ff',
        'msapplication-config': '/browserconfig.xml'
    }

    return meta_tags

def extract_keywords_from_news(news_data):
    """Extract relevant financial keywords from news headlines"""
    financial_keywords = [
        'financial news', 'stock market', 'economy', 'investment', 'trading',
        'forex', 'currency', 'bonds', 'commodities', 'economic indicators',
        'central bank', 'interest rates', 'inflation', 'GDP', 'market analysis',
        'real-time data', 'financial dashboard', 'market trends', 'economic data'
    ]

    # Extract keywords from headlines
    extracted_keywords = set()
    common_financial_terms = [
        'stock', 'market', 'economy', 'dollar', 'euro', 'pound', 'yen',
        'gold', 'oil', 'bitcoin', 'crypto', 'fed', 'bank', 'rate', 'trade',
        'investment', 'growth', 'inflation', 'recession', 'bull', 'bear'
    ]

    for headline in news_data[:20]:  # Check first 20 headlines
        headline_text = headline.get('headline', '').lower()
        for term in common_financial_terms:
            if term in headline_text:
                extracted_keywords.add(term)

    # Combine base keywords with extracted ones
    all_keywords = financial_keywords + list(extracted_keywords)
    return all_keywords[:30]  # Limit to 30 keywords

def generate_dynamic_description(news_data, econ_data):
    """Generate dynamic meta description based on current data"""
    base_description = "Waneye provides real-time financial news, market analysis, and economic indicators. "

    # Add current market focus
    if news_data:
        # Get top categories from headlines
        market_focus = []
        for headline in news_data[:5]:
            text = headline.get('headline', '').lower()
            if any(term in text for term in ['stock', 'market', 'dow', 'nasdaq']):
                market_focus.append('stock market')
            elif any(term in text for term in ['dollar', 'euro', 'currency', 'forex']):
                market_focus.append('currency exchange')
            elif any(term in text for term in ['fed', 'central bank', 'interest']):
                market_focus.append('monetary policy')
            elif any(term in text for term in ['crypto', 'bitcoin', 'ethereum']):
                market_focus.append('cryptocurrency')

        if market_focus:
            unique_focus = list(set(market_focus[:3]))  # Get unique focuses, max 3
            focus_text = f"Track {', '.join(unique_focus)} updates, "
            base_description += focus_text

    base_description += "central bank policies, forex rates, and comprehensive economic data dashboard."

    # Ensure description is within recommended length (150-160 characters)
    if len(base_description) > 160:
        base_description = base_description[:157] + "..."

    return base_description

def generate_structured_data(news_data, last_updated):
    """Generate JSON-LD structured data for better SEO"""

    # Main organization schema
    organization_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Waneye Technology",
        "alternateName": "Waneye",
        "url": "https://waneye.com",
        "logo": "https://waneye.com/favicon.svg",
        "description": "Real-time financial news aggregation and market analysis platform",
        "foundingDate": "2024",
        "sameAs": [
            "https://twitter.com/WaneyeTech",
            "https://github.com/waneyetechnology"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Customer Service",
            "availableLanguage": "English"
        }
    }

    # Website schema
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Waneye — global vision for smarter finance",
        "alternateName": "Waneye",
        "url": "https://waneye.com",
        "description": "Real-time financial news, market data, and economic indicators",
        "publisher": {
            "@type": "Organization",
            "name": "Waneye Technology"
        },
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://waneye.com/?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }

    # News articles schema
    news_articles = []
    for i, article in enumerate(news_data[:10]):  # Top 10 articles
        if article.get('headline') and article.get('url'):
            article_schema = {
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "headline": article['headline'],
                "url": article['url'],
                "datePublished": article.get('publishedAt', last_updated),
                "publisher": {
                    "@type": "Organization",
                    "name": "Waneye Technology",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://waneye.com/favicon.svg"
                    }
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": article['url']
                }
            }

            # Add image if available
            if article.get('image'):
                article_schema["image"] = {
                    "@type": "ImageObject",
                    "url": f"https://waneye.com/{article['image']}",
                    "width": 512,
                    "height": 512
                }

            news_articles.append(article_schema)

    # Financial data dashboard schema
    dashboard_schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Waneye — global vision for smarter finance",
        "url": "https://waneye.com",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Any",
        "description": "Real-time financial dashboard with news, market data, and economic indicators",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }

    return {
        'organization': organization_schema,
        'website': website_schema,
        'news_articles': news_articles,
        'dashboard': dashboard_schema
    }

def generate_sitemap(base_url="https://waneye.com"):
    """Generate XML sitemap"""

    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')

    # Main page
    url_main = ET.SubElement(urlset, 'url')
    ET.SubElement(url_main, 'loc').text = base_url
    ET.SubElement(url_main, 'lastmod').text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    ET.SubElement(url_main, 'changefreq').text = 'hourly'
    ET.SubElement(url_main, 'priority').text = '1.0'

    # Convert to string with pretty formatting
    rough_string = ET.tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')

def generate_robots_txt():
    """Generate robots.txt file"""
    robots_content = """User-agent: *
Allow: /

# Sitemaps
Sitemap: https://waneye.com/sitemap.xml

# Crawl delay (optional, in seconds)
Crawl-delay: 1

# Specific directives for major search engines
User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: Slurp
Allow: /
Crawl-delay: 1
"""
    return robots_content

def save_seo_files(structured_data):
    """Save SEO-related files (sitemap, robots.txt, etc.)"""
    try:
        # Save sitemap
        sitemap_xml = generate_sitemap()
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        logger.info("Generated sitemap.xml")

        # Save robots.txt
        robots_txt = generate_robots_txt()
        with open('robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_txt)
        logger.info("Generated robots.txt")

        # Save structured data as JSON file for reference
        with open('structured-data.json', 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        logger.info("Generated structured-data.json")

    except Exception as e:
        logger.error(f"Error saving SEO files: {e}")
