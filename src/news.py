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
    
    # Ensure default.jpg exists
    default_img_path = img_dir / "default.jpg"
    if not default_img_path.exists() or os.path.getsize(default_img_path) < 1000:  # Check if it's missing or too small
        try:
            # Create a simple default image or copy from an existing one
            existing_images = list(img_dir.glob("*.jpg"))
            if existing_images:
                import shutil
                source_image = sorted(existing_images, key=lambda p: os.path.getsize(p))[-1]  # Use the largest image
                shutil.copy(source_image, default_img_path)
                logger.info(f"Created default.jpg from existing image: {source_image}")
            else:
                # Create a simple gradient image as fallback
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (256, 256), color=(234, 246, 255))
                draw = ImageDraw.Draw(img)
                draw.rectangle([(0, 0), (256, 256)], fill=(234, 246, 255))
                draw.rectangle([(20, 20), (236, 236)], fill=(0, 116, 217), outline=(0, 74, 217))
                img.save(default_img_path, 'JPEG')
                logger.info("Created new default.jpg image")
        except Exception as e:
            logger.error(f"Error creating default.jpg: {e}")
            
    return img_dir

def fetch_and_save_image(url, headline_id):
    img_dir = ensure_image_dir()
    image_path = f"static/images/headlines/{headline_id}.jpg"
    full_path = img_dir / f"{headline_id}.jpg"
    
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
            # Try to generate an AI image instead of returning None
            return generate_ai_image(headline_id)

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # More comprehensive approach to find images in meta tags for any site
        image_url = None
        
        # Step 1: Try all common image meta tags using a systematic approach
        meta_image_properties = [
            # Open Graph tags (used by Facebook and many sites)
            'og:image', 'og:image:url', 'og:image:secure_url',
            # Twitter card tags
            'twitter:image', 'twitter:image:src',
            # Other common meta image tags
            'image', 'thumbnail', 'msapplication-TileImage'
        ]
        
        # Check meta tags with 'property' attribute
        for prop in meta_image_properties:
            if image_url:
                break
            meta_tags = soup.find_all('meta', property=prop)
            for meta in meta_tags:
                if meta.get('content'):
                    content = meta.get('content')
                    if re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I):
                        image_url = content
                        logger.info(f"Found image in meta property '{prop}': {image_url}")
                        break
        
        # Check meta tags with 'name' attribute if still no image found
        if not image_url:
            for prop in meta_image_properties:
                if image_url:
                    break
                meta_tags = soup.find_all('meta', attrs={'name': prop})
                for meta in meta_tags:
                    if meta.get('content'):
                        content = meta.get('content')
                        if re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I):
                            image_url = content
                            logger.info(f"Found image in meta name '{prop}': {image_url}")
                            break
        
        # Check meta tags with 'itemprop' attribute (used in schema.org markup)
        if not image_url:
            for prop in ['image', 'thumbnailUrl', 'contentUrl']:
                if image_url:
                    break
                meta_tags = soup.find_all('meta', attrs={'itemprop': prop})
                for meta in meta_tags:
                    if meta.get('content'):
                        content = meta.get('content')
                        if re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I):
                            image_url = content
                            logger.info(f"Found image in meta itemprop '{prop}': {image_url}")
                            break

        # Step 2: If meta tags didn't work, look for structured JSON-LD data
        if not image_url:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                if script.string:
                    try:
                        import json
                        data = json.loads(script.string)
                        # Look for image in JSON-LD data
                        if isinstance(data, dict):
                            # Check for image property in various structures
                            for img_prop in ['image', 'thumbnailUrl', 'contentUrl']:
                                if img_prop in data and data[img_prop]:
                                    if isinstance(data[img_prop], str):
                                        image_url = data[img_prop]
                                    elif isinstance(data[img_prop], list) and data[img_prop]:
                                        image_url = data[img_prop][0]
                                    if image_url:
                                        logger.info(f"Found image in JSON-LD data: {image_url}")
                                        break
                    except Exception as json_err:
                        logger.debug(f"Error parsing JSON-LD: {json_err}")
        
        # Step 3: If still no image, try image elements with specific attributes
        if not image_url:
            # Look for article-related image elements with multiple source attributes
            image_attrs = ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-url', 'data-hi-res-src']
            promising_classes = ['article-image', 'story-img', 'article-img', 'post-image', 'featured-image', 'entry-image', 'hero-image']
            
            # First try to find images with promising class names
            for class_name in promising_classes:
                if image_url:
                    break
                images = soup.find_all('img', class_=re.compile(class_name))
                for img in images:
                    for attr in image_attrs:
                        if img.get(attr):
                            src = img.get(attr)
                            if src and not re.search(r'(logo|icon|avatar|banner|small)', src, re.I):
                                image_url = src
                                logger.info(f"Found image with class {class_name}: {image_url}")
                                break
                    if image_url:
                        break
            
            # If still no image, look for large images
            if not image_url:
                images = soup.find_all('img')
                for img in images:
                    # Try multiple source attributes
                    for attr in image_attrs:
                        if image_url:
                            break
                        src = img.get(attr)
                        if src and not re.search(r'(logo|icon|avatar|banner|small|button)', src, re.I) and (
                            re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', src, re.I) or
                            ('width' in img.attrs and 'height' in img.attrs and 
                             int(img.get('width', '0')) > 200 and int(img.get('height', '0')) > 100)
                        ):
                            image_url = src
                            logger.info(f"Found image via {attr} attribute: {image_url}")
                            break
                
                # If still no image, look for the largest image by dimensions
                if not image_url:
                    largest_area = 0
                    largest_img_src = None
                    
                    for img in images:
                        try:
                            width = int(img.get('width', 0))
                            height = int(img.get('height', 0))
                            src = img.get('src')
                            
                            if src and width > 0 and height > 0:
                                area = width * height
                                if area > largest_area and not re.search(r'(logo|icon|avatar|banner)', src, re.I):
                                    largest_area = area
                                    largest_img_src = src
                        except (ValueError, TypeError):
                            pass
                    
                    if largest_area > 10000:  # Minimum area threshold
                        image_url = largest_img_src
                        logger.info(f"Found largest image by dimensions: {image_url}")

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
        
        # Detect if this might be a paywalled or restricted site
        domain = urlparse(url).netloc
        is_likely_paywalled = any(site in domain for site in [
            'wsj.com', 'nytimes.com', 'ft.com', 'bloomberg.com', 
            'economist.com', 'barrons.com', 'seekingalpha.com',
            'businessinsider.com', 'morningstar.com'
        ])
        
        if is_likely_paywalled:
            logger.info(f"Likely paywalled content detected for domain: {domain}")
            
        # Try to use headline text for an alternative image source
        try:
            # Extract article title
            title = ""
            for headline in fetch_financial_headlines.current_headlines:
                if hashlib.md5(headline['url'].encode()).hexdigest() == headline_id:
                    title = headline['headline']
                    break
            
            if title:
                # Log information about the headline for debugging
                logger.info(f"Using headline text for alternative image search: {title}")
                
                # We could implement image search here if approved
                # For now, just prepare for AI image generation
                pass
                
        except Exception as search_ex:
            logger.error(f"Error with alternative image approach: {search_ex}")
    
    # No image found or all methods failed, generate one with OpenAI
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
        
        # Configure the OpenAI client - using the updated method we fixed earlier
        openai.api_key = api_key
        client = openai.OpenAI()
        
        # Get the headline text from all_headlines global
        headline_text = ""
        for headline in fetch_financial_headlines.current_headlines:
            if hashlib.md5(headline['url'].encode()).hexdigest() == headline_id:
                headline_text = headline['headline']
                break
        
        if not headline_text:
            logger.warning(f"Could not find headline text for ID {headline_id}")
            # Try to use the headline_id as a fallback for the prompt
            headline_text = f"Financial news with ID {headline_id}"
        
        # Generate prompt for DALL-E - optimized for financial imagery
        prompt = f"A high quality financial news image for: {headline_text}. Professional business style with clear details, suitable for financial news."
        
        # Generate the image with DALL-E 2 at the optimal size for cost vs. quality
        try:
            logger.info(f"Generating AI image for headline: '{headline_text[:50]}...'")
            response = client.images.generate(
                model="dall-e-2",  # DALL-E 2 is more cost-effective than DALL-E 3
                prompt=prompt,
                size="512x512",  # Best balance between cost and quality (512x512 is mid-tier for DALL-E 2)
                n=1,
                quality="standard",  # Standard quality is the most cost-effective
            )
            
            # Get image URL from response
            image_url = response.data[0].url
            logger.info(f"Successfully generated AI image URL: {image_url}")
            
            # Download the generated image
            img_response = requests.get(image_url, timeout=10)
            if img_response.ok:
                with open(full_path, 'wb') as f:
                    f.write(img_response.content)
                logger.info(f"Generated AI image for headline ID: {headline_id}")
                # Return the path with a flag that this is an AI-generated image
                return image_path + "#ai-generated"
            else:
                logger.error(f"Failed to download AI image. Status code: {img_response.status_code}")
        except Exception as api_error:
            logger.error(f"OpenAI API error: {api_error}")
            
            # Try to fall back to a more reliable image generation method if possible
            try:
                # Check if we can copy an existing AI image as a fallback
                ai_images = list(img_dir.glob("*#ai-generated"))
                existing_ai_images = [p for p in img_dir.glob("*.jpg") if os.path.getsize(p) > 5000]
                
                if existing_ai_images:
                    # Use an existing image as a fallback
                    import random
                    import shutil
                    source_image = random.choice(existing_ai_images)
                    logger.info(f"Using fallback: copying existing image {source_image} to {full_path}")
                    shutil.copy(source_image, full_path)
                    return image_path + "#ai-generated"
            except Exception as fallback_error:
                logger.error(f"AI image fallback failed: {fallback_error}")
    
    except Exception as e:
        logger.error(f"Error generating AI image for headline ID {headline_id}: {e}")
    
    logger.warning(f"Using default.jpg for headline: '{headline_text[:50]}...'")
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
