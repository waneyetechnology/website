import os
import openai
import requests
import random
import hashlib
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
from pathlib import Path
from .log import logger

def fetch_newsapi_headlines():
    api_key = os.environ.get("NEWSAPI_API_KEY")
    if not api_key:
        # Log a warning for debugging in CI/CD
        logger.warning("NEWSAPI_API_KEY is not set or empty.")
        return []
    url = "https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=10&apiKey=" + api_key
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("articles", []):
                # Use publishedAt if available
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedAt")
                })
        else:
            logger.warning(f"NewsAPI request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from NewsAPI")
    logger.info(f"NewsAPI headlines: {headlines}")
    return headlines

def fetch_fmp_headlines():
    api_key = os.environ.get("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/stock_news?limit=10&apikey={api_key}"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data:
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedDate")
                })
        else:
            logger.warning(f"FMP request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"FMP fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from FMP")
    logger.info(f"FMP headlines: {headlines}")
    return headlines

def fetch_marketaux_headlines():
    api_key = os.environ.get("MARKETAUX_API_KEY")
    url = f"https://api.marketaux.com/v1/news/all?language=en&filter_entities=true&api_token={api_key}&limit=10"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("data", []):
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("published_at")
                })
        else:
            logger.warning(f"Marketaux request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Marketaux fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Marketaux")
    logger.info(f"Marketaux headlines: {headlines}")
    return headlines

def fetch_gnews_headlines():
    api_key = os.environ.get("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/top-headlines?topic=business&lang=en&token={api_key}&max=10"
    headlines = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            for article in data.get("articles", []):
                headlines.append({
                    "headline": article["title"],
                    "url": article["url"],
                    "publishedAt": article.get("publishedAt")
                })
        else:
            logger.warning(f"GNews request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"GNews fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from GNews")
    logger.info(f"GNews headlines: {headlines}")
    return headlines

def fetch_yahoo_finance_headlines():
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://finance.yahoo.com/news/rssindex"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text
                pubdate = item.find("pubDate")
                publishedAt = None
                if pubdate is not None:
                    try:
                        publishedAt = parsedate_to_datetime(pubdate.text).isoformat()
                    except Exception:
                        publishedAt = pubdate.text
                headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"Yahoo Finance RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Yahoo Finance fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Yahoo Finance RSS")
    logger.info(f"Yahoo Finance headlines: {headlines}")
    return headlines

def ensure_image_dir():
    img_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "static" / "images" / "headlines"
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir

def fetch_and_save_image(url, headline_id):
    img_dir = ensure_image_dir()
    image_path = f"static/images/headlines/{headline_id}.jpg"
    full_path = img_dir / f"{headline_id}.jpg"

    # For testing only: Force at least one AI generation by picking a specific headline ID
    if headline_id == "6219af0b4fb4bc727a156631fb23954d":
        # Remove existing image if it exists
        if os.path.exists(full_path):
            os.remove(full_path)
        return generate_ai_image(headline_id)
    
    # Don't refetch if we already have the image
    if os.path.exists(full_path):
        logger.info(f"Image already exists for {headline_id}")
        return image_path

    # Try to fetch the page and extract an image
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if not response.ok:
            logger.warning(f"Failed to fetch URL {url}: {response.status_code}")
            return None

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # First try Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image.get('content')
        else:
            # Then try Twitter image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image.get('content')
            else:
                # Finally try the first large image
                images = soup.find_all('img')
                image_url = None
                for img in images:
                    src = img.get('src') or img.get('data-src')
                    if src and not re.search(r'(logo|icon|avatar|banner)', src, re.I) and (
                        re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', src, re.I) or
                        'width' in img.attrs and 'height' in img.attrs and
                        int(img.get('width', '0')) > 200 and int(img.get('height', '0')) > 100
                    ):
                        image_url = src
                        break

        # If we found an image URL, download it
        if image_url:
            # Handle relative URLs
            if not image_url.startswith(('http://', 'https://')):
                # Extract base URL
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                image_url = f"{base_url}{image_url if image_url.startswith('/') else f'/{image_url}'}"

            # Download the image
            img_response = requests.get(image_url, headers=headers, timeout=10)
            if img_response.ok:
                with open(full_path, 'wb') as f:
                    f.write(img_response.content)
                logger.info(f"Saved image for {headline_id} from {image_url}")
                return image_path
    except Exception as e:
        logger.error(f"Error fetching image for {url}: {e}")

    # No image found, generate one with OpenAI
    return generate_ai_image(headline_id)

def generate_ai_image(headline_id):
    """
    Generate an image using OpenAI's DALL-E API for headlines that don't have images
    """
    img_dir = ensure_image_dir()
    image_path = f"static/images/headlines/{headline_id}.jpg"
    full_path = img_dir / f"{headline_id}.jpg"
    
    try:
        # Get the OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set or empty.")
            return "static/images/headlines/default.jpg"
        
        # Configure the OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Get the headline text from all_headlines global
        headline_text = ""
        for headline in fetch_financial_headlines.current_headlines:
            if hashlib.md5(headline['url'].encode()).hexdigest() == headline_id:
                headline_text = headline['headline']
                break
        
        if not headline_text:
            logger.warning(f"Could not find headline text for ID {headline_id}")
            return "static/images/headlines/default.jpg"
        
        # Generate prompt for DALL-E - simpler prompt for smaller image size
        prompt = f"Simple financial news icon for: {headline_text}. Minimalist business style."
        
        # Generate the image with DALL-E 2 at smaller size for cost efficiency
        response = client.images.generate(
            model="dall-e-2",  # Using DALL-E 2 which is more cost-effective
            prompt=prompt,
            size="256x256",  # Smallest size for lowest cost
            n=1,
        )
        
        # Get image URL from response
        image_url = response.data[0].url
        
        # Download the generated image
        img_response = requests.get(image_url, timeout=10)
        if img_response.ok:
            with open(full_path, 'wb') as f:
                f.write(img_response.content)
            logger.info(f"Generated AI image for headline ID: {headline_id}")
            # Return the path with a flag that this is an AI-generated image
            return image_path + "#ai-generated"
    except Exception as e:
        logger.error(f"Error generating AI image for headline ID {headline_id}: {e}")
    
    return "static/images/headlines/default.jpg"

def fetch_financial_headlines():
    """
    Fetches financial headlines from 5 sources/APIs, applies a random weight to each source,
    fetches images for each headline, and returns all headlines with local image paths.
    """
    # Initialize the class attribute if it doesn't exist
    if not hasattr(fetch_financial_headlines, 'current_headlines'):
        fetch_financial_headlines.current_headlines = []
    sources = [
        fetch_newsapi_headlines,
        fetch_fmp_headlines,
        fetch_marketaux_headlines,
        fetch_gnews_headlines,
        fetch_yahoo_finance_headlines
    ]
    # Assign a random weight to each source
    weighted_sources = [(random.random(), fn) for fn in sources]
    weighted_sources.sort(reverse=True)  # Higher weight = higher priority
    all_headlines = []
    for _, fn in weighted_sources:
        all_headlines += fn()
    
    # Store the current headlines to access from generate_ai_image
    fetch_financial_headlines.current_headlines = all_headlines.copy()

    # Add image paths to headlines
    for headline in all_headlines:
        # Create a unique ID for the headline based on URL
        headline_id = hashlib.md5(headline['url'].encode()).hexdigest()
        # Fetch and save the image
        image_path = fetch_and_save_image(headline['url'], headline_id)
        # Add the image path to the headline
        headline['image'] = image_path

    return all_headlines
