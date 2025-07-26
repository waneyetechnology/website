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

def fetch_reuters_headlines():
    """Fetch Reuters business headlines from RSS feed"""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://www.reuters.com/arc/outboundfeeds/rss/category/business/?outputType=xml"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    publishedAt = None
                    
                    if pubdate_elem is not None:
                        try:
                            publishedAt = parsedate_to_datetime(pubdate_elem.text).isoformat()
                        except Exception:
                            publishedAt = pubdate_elem.text
                    
                    headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"Reuters RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Reuters fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Reuters RSS")
    logger.info(f"Reuters headlines: {headlines}")
    return headlines

def fetch_bloomberg_headlines():
    """Fetch Bloomberg markets headlines from RSS feed"""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://feeds.bloomberg.com/markets/news.rss"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    publishedAt = None
                    
                    if pubdate_elem is not None:
                        try:
                            publishedAt = parsedate_to_datetime(pubdate_elem.text).isoformat()
                        except Exception:
                            publishedAt = pubdate_elem.text
                    
                    headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"Bloomberg RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Bloomberg fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Bloomberg RSS")
    logger.info(f"Bloomberg headlines: {headlines}")
    return headlines

def fetch_cnbc_headlines():
    """Fetch CNBC business headlines from RSS feed"""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://feeds.nbcnews.com/nbcnews/public/business"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    publishedAt = None
                    
                    if pubdate_elem is not None:
                        try:
                            publishedAt = parsedate_to_datetime(pubdate_elem.text).isoformat()
                        except Exception:
                            publishedAt = pubdate_elem.text
                    
                    headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"CNBC RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"CNBC fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from CNBC RSS")
    logger.info(f"CNBC headlines: {headlines}")
    return headlines

def fetch_marketwatch_headlines():
    """Fetch MarketWatch headlines from RSS feed"""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://feeds.marketwatch.com/marketwatch/marketpulse/"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    publishedAt = None
                    
                    if pubdate_elem is not None:
                        try:
                            publishedAt = parsedate_to_datetime(pubdate_elem.text).isoformat()
                        except Exception:
                            publishedAt = pubdate_elem.text
                    
                    headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"MarketWatch RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"MarketWatch fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from MarketWatch RSS")
    logger.info(f"MarketWatch headlines: {headlines}")
    return headlines

def fetch_ft_headlines():
    """Fetch Financial Times FastFT headlines from RSS feed"""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    url = "https://www.ft.com/rss/feed/fastft"
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.ok:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    publishedAt = None
                    
                    if pubdate_elem is not None:
                        try:
                            publishedAt = parsedate_to_datetime(pubdate_elem.text).isoformat()
                        except Exception:
                            publishedAt = pubdate_elem.text
                    
                    headlines.append({"headline": title, "url": link, "publishedAt": publishedAt})
        else:
            logger.warning(f"Financial Times RSS request failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Financial Times fetch error: {e}")
        return []
    logger.info(f"Fetched {len(headlines)} headlines from Financial Times RSS")
    logger.info(f"Financial Times headlines: {headlines}")
    return headlines

def ensure_image_dir():
    img_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "static" / "images" / "headlines"
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir

def ensure_ai_image_dir():
    """Create and return the AI-generated images directory"""
    ai_img_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "static" / "images" / "ai-generated"
    ai_img_dir.mkdir(parents=True, exist_ok=True)
    return ai_img_dir

def ensure_dynamic_image_dir():
    """Create and return the dynamic images directory"""
    dynamic_img_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "static" / "images" / "dynamic"
    dynamic_img_dir.mkdir(parents=True, exist_ok=True)
    return dynamic_img_dir

def create_dynamic_image():
    """Create a unique dynamic image with timestamp - regenerated every time for fresh appearance"""
    import time
    import uuid
    
    dynamic_img_dir = ensure_dynamic_image_dir()
    
    # Generate unique filename with timestamp and UUID
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    filename = f"dynamic_{timestamp}_{unique_id}.jpg"
    dynamic_img_path = dynamic_img_dir / filename
    
    # Always regenerate the dynamic image for fresh, randomized appearance
    try:
        # Create a colorful, visually appealing image with random vivid colors
        from PIL import Image, ImageDraw
        import colorsys
        import math

        # Generate vibrant background color
        def random_vibrant_color():
            # Generate colors with high saturation and brightness
            h = random.random()  # Random hue
            s = 0.7 + random.random() * 0.3  # High saturation (0.7-1.0)
            v = 0.8 + random.random() * 0.2  # High brightness (0.8-1.0)
            # Convert to RGB
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
            return (r, g, b)

        # Create complementary or contrasting colors
        bg_color = random_vibrant_color()

        # Create a different color for the foreground
        fg_hue = (random.random() + 0.5) % 1.0  # Shift hue by 0.5 (180 degrees) for contrast
        fg_s = 0.8 + random.random() * 0.2  # High saturation
        fg_v = 0.7 + random.random() * 0.3  # High brightness
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(fg_hue, fg_s, fg_v)]
        fg_color = (r, g, b)

        # Create a border color that complements the foreground
        border_hue = (fg_hue + 0.1) % 1.0  # Slight hue shift
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(border_hue, fg_s, fg_v * 0.8)]
        border_color = (r, g, b)

        # Create the image
        img = Image.new('RGB', (512, 512), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Choose a random pattern style for variety
        pattern_style = random.randint(1, 4)

        if pattern_style == 1:
            # Concentric rectangles pattern
            for i in range(12):
                # Create gradient effect with multiple rectangles
                inset = i * 20
                draw.rectangle([inset, inset, 512-inset, 512-inset],
                              fill=None,
                              outline=tuple([max(0, c - i*10) for c in fg_color]),
                              width=3)

            # Draw central element
            draw.rectangle([128, 128, 384, 384], fill=fg_color, outline=border_color, width=5)
            draw.rectangle([192, 192, 320, 320], fill=bg_color, outline=border_color, width=3)

        elif pattern_style == 2:
            # Diagonal stripes pattern
            stripe_width = 30
            stripe_color1 = fg_color
            stripe_color2 = tuple([int((c + 255) / 2) for c in fg_color])  # Lighter version

            for i in range(-512, 512, stripe_width * 2):
                draw.polygon([(i, 0), (i + stripe_width, 0), (i + 512 + stripe_width, 512), (i + 512, 512)],
                            fill=stripe_color1)

            # Add an overlaid shape
            center_size = 220
            draw.ellipse([256-center_size, 256-center_size, 256+center_size, 256+center_size],
                        fill=bg_color, outline=border_color, width=5)
            draw.ellipse([256-center_size//2, 256-center_size//2, 256+center_size//2, 256+center_size//2],
                        fill=stripe_color2, outline=border_color, width=3)

        elif pattern_style == 3:
            # Gradient circles
            for i in range(8):
                size = 512 - i * 60
                color = tuple([int(c * (1 - i/10)) for c in fg_color])
                draw.ellipse([256-size//2, 256-size//2, 256+size//2, 256+size//2], fill=color)

            # Add geometric elements
            square_size = 150
            draw.rectangle([256-square_size, 256-square_size, 256+square_size, 256+square_size],
                          fill=None, outline=border_color, width=6)

            for angle in range(0, 360, 45):
                rad = angle * 3.14159 / 180
                x = 256 + int(200 * math.cos(rad))
                y = 256 + int(200 * math.sin(rad))
                draw.ellipse([x-20, y-20, x+20, y+20], fill=bg_color, outline=border_color, width=2)

        else:
            # Abstract financial pattern
            # Draw grid background
            for x in range(0, 512, 32):
                draw.line([(x, 0), (x, 512)], fill=tuple([max(0, c - 40) for c in bg_color]), width=1)
            for y in range(0, 512, 32):
                draw.line([(0, y), (512, y)], fill=tuple([max(0, c - 40) for c in bg_color]), width=1)

            # Draw "chart" lines
            points = []
            for i in range(6):
                x = i * 100
                y = random.randint(150, 350)
                points.append((x, y))

            # Connect points with lines
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=fg_color, width=6)

            # Add some indicator dots
            for x, y in points:
                draw.ellipse([x-10, y-10, x+10, y+10], fill=border_color)

            # Add a central logo-like element
            draw.rectangle([206, 206, 306, 306], fill=fg_color)
            draw.ellipse([156, 156, 356, 356], fill=None, outline=border_color, width=4)

        # Add some text to indicate this is a dynamic image
        try:
            # Try to load a font, falling back to default if necessary
            from PIL import ImageFont
            try:
                # Try to find a system font
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                    '/Library/Fonts/Arial Bold.ttf',  # macOS
                    'C:\\Windows\\Fonts\\Arial.ttf'  # Windows
                ]
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = ImageFont.truetype(path, 30)
                        break

                if font:
                    # Add a semi-transparent text overlay
                    text = "FINANCIAL NEWS"

                    # Handle different versions of PIL for text size measurement
                    try:
                        if hasattr(draw, 'textsize'):
                            text_width, text_height = draw.textsize(text, font=font)
                        elif hasattr(font, 'getsize'):
                            text_width, text_height = font.getsize(text)
                        else:
                            # Newer PIL versions
                            text_width, text_height = font.getbbox(text)[2:]
                    except Exception:
                        # Fallback with estimated size
                        text_width, text_height = 300, 40

                    text_position = ((512 - text_width) // 2, 430)

                    # Create a semi-transparent overlay by creating a new image with alpha
                    from PIL import Image
                    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)

                    # Add a text background for better readability
                    text_bg_padding = 10
                    overlay_draw.rectangle([
                        text_position[0] - text_bg_padding,
                        text_position[1] - text_bg_padding,
                        text_position[0] + text_width + text_bg_padding,
                        text_position[1] + text_height + text_bg_padding
                    ], fill=(0, 0, 0, 128))

                    # Draw the text on the overlay
                    overlay_draw.text(text_position, text, font=font, fill=(255, 255, 255, 255))

                    # Composite the overlay onto the main image
                    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            except Exception as font_err:
                logger.debug(f"Could not load font for dynamic image: {font_err}")
        except ImportError:
            logger.debug("ImageFont not available, skipping text overlay")

        # Save the image at high quality
        img.save(dynamic_img_path, 'JPEG', quality=95)
        logger.info(f"Created new vibrant dynamic image: {filename}")
        
        # Return the relative path to the image
        return f"static/images/dynamic/{filename}"
        
    except Exception as e:
        logger.error(f"Error creating dynamic image: {e}")
        return None

def get_random_ai_image():
    """Get a random AI-generated image from the ai-generated folder as fallback"""
    ai_img_dir = ensure_ai_image_dir()
    
    # Get all image files in the AI-generated directory
    ai_images = [f for f in os.listdir(ai_img_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if ai_images:
        # Select a random AI-generated image
        random_image = random.choice(ai_images)
        relative_path = f"static/images/ai-generated/{random_image}"
        logger.info(f"Using random AI-generated image: {relative_path}")
        return relative_path + "#ai-generated"
    else:
        logger.warning("No AI-generated images available for fallback")
        # Generate a unique dynamic image
        dynamic_image_path = create_dynamic_image()
        if dynamic_image_path:
            return dynamic_image_path + "#dynamic"
        else:
            # Ultimate fallback - this shouldn't happen but just in case
            return "static/images/dynamic/fallback_error.jpg"

def fetch_and_save_image(url, headline_id):
    # Ensure directories exist
    img_dir = ensure_image_dir()
    ai_img_dir = ensure_ai_image_dir()
    
    image_path = f"static/images/headlines/{headline_id}.jpg"
    full_path = img_dir / f"{headline_id}.jpg"
    ai_image_path = f"static/images/ai-generated/{headline_id}.jpg"
    ai_full_path = ai_img_dir / f"{headline_id}.jpg"

    # Don't refetch if we already have a regular web image
    if os.path.exists(full_path):
        logger.info(f"Using existing web image for {headline_id}")
        return image_path

    # Check if we already have an AI-generated image first (preferred)
    if os.path.exists(ai_full_path):
        logger.info(f"Using existing AI-generated image for {headline_id}")
        return ai_image_path + "#ai-generated"

    # Try to fetch the page and extract an image
    try:
        # Enhanced headers to better simulate a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Create a session to maintain cookies and connection state
        session = requests.Session()
        session.headers.update(headers)
        
        # Add a small delay to avoid being flagged as a bot
        import time
        time.sleep(0.5)
        
        response = session.get(url, timeout=15, allow_redirects=True)
        if not response.ok:
            logger.warning(f"Failed to fetch URL {url}: {response.status_code}")
            # Try to generate an AI image instead of returning None
            return generate_ai_image(headline_id)

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Enhanced approach to find images with better news site support
        image_url = None

        # Step 1: Try all common image meta tags using a systematic approach
        meta_image_properties = [
            # Open Graph tags (used by Facebook and many sites)
            'og:image', 'og:image:url', 'og:image:secure_url',
            # Twitter card tags
            'twitter:image', 'twitter:image:src', 'twitter:image:alt',
            # Other common meta image tags
            'image', 'thumbnail', 'msapplication-TileImage',
            # News-specific meta tags
            'article:image', 'sailthru.image.full', 'sailthru.image.thumb'
        ]

        # Check meta tags with 'property' attribute
        for prop in meta_image_properties:
            if image_url:
                break
            meta_tags = soup.find_all('meta', property=prop)
            for meta in meta_tags:
                if meta.get('content'):
                    content = meta.get('content').strip()
                    if content and (re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I) or 
                                  'image' in content):
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
                        content = meta.get('content').strip()
                        if content and (re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I) or
                                      'image' in content):
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
                        content = meta.get('content').strip()
                        if content and (re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', content, re.I) or
                                      'image' in content):
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
                                        image_url = data[img_prop][0] if isinstance(data[img_prop][0], str) else data[img_prop][0].get('url', '')
                                    elif isinstance(data[img_prop], dict):
                                        image_url = data[img_prop].get('url', '')
                                    if image_url:
                                        logger.info(f"Found image in JSON-LD data: {image_url}")
                                        break
                        elif isinstance(data, list):
                            # Handle arrays of JSON-LD objects
                            for item in data:
                                if isinstance(item, dict):
                                    for img_prop in ['image', 'thumbnailUrl', 'contentUrl']:
                                        if img_prop in item and item[img_prop]:
                                            if isinstance(item[img_prop], str):
                                                image_url = item[img_prop]
                                            elif isinstance(item[img_prop], list) and item[img_prop]:
                                                image_url = item[img_prop][0] if isinstance(item[img_prop][0], str) else item[img_prop][0].get('url', '')
                                            elif isinstance(item[img_prop], dict):
                                                image_url = item[img_prop].get('url', '')
                                            if image_url:
                                                logger.info(f"Found image in JSON-LD array data: {image_url}")
                                                break
                                if image_url:
                                    break
                    except Exception as json_err:
                        logger.debug(f"Error parsing JSON-LD: {json_err}")

        # Step 3: Enhanced image element search with news-specific classes and attributes
        if not image_url:
            # Look for article-related image elements with multiple source attributes
            image_attrs = ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-url', 'data-hi-res-src', 
                          'data-srcset', 'data-original-src', 'data-lazy', 'data-image-src']
            
            # Enhanced news-specific class patterns - only headline/article related
            promising_classes = [
                'article-image', 'story-img', 'article-img', 'post-image', 'featured-image', 
                'entry-image', 'hero-image', 'lead-image', 'main-image', 'story-image',
                'content-image', 'headline-image', 'news-image', 'media-image',
                'story-photo', 'article-photo', 'news-photo', 'content-photo',
                # Reuters specific
                'media__image', 'image__picture', 'story-image',
                # Bloomberg specific  
                'media-object', 'hero-media', 'lede-media', 'story-image',
                # CNN specific
                'media__image', 'el__image', 'media-image',
                # Generic news patterns
                'wp-post-image', 'attachment-large', 'size-large'
            ]

            # First try to find images with promising class names (strict content-related only)
            for class_name in promising_classes:
                if image_url:
                    break
                # Use partial matching for class names
                images = soup.find_all('img', class_=lambda x: x and class_name in ' '.join(x) if isinstance(x, list) else class_name in (x or ''))
                for img in images:
                    for attr in image_attrs:
                        if img.get(attr):
                            src = img.get(attr).strip()
                            # Strict filtering to avoid irrelevant images
                            if (src and 
                                not re.search(r'(logo|icon|avatar|banner|small|button|placeholder|ad|advertisement|sponsor|widget|sidebar|footer|header|nav|menu|social|share)', src, re.I)):
                                
                                # Additional check for image context within article
                                img_parent = img.parent
                                parent_classes = ' '.join(img_parent.get('class', [])) if img_parent else ''
                                parent_id = img_parent.get('id', '') if img_parent else ''
                                
                                # Ensure the image is within article content, not in ads or sidebars
                                if not re.search(r'(ad|advertisement|sponsor|sidebar|widget|related|footer|header|nav|menu|comment)', 
                                                parent_classes + ' ' + parent_id, re.I):
                                    
                                    # Handle srcset attributes (take the first/largest image)
                                    if attr == 'data-srcset' or 'srcset' in attr:
                                        srcset_parts = src.split(',')
                                        if srcset_parts:
                                            src = srcset_parts[0].strip().split(' ')[0]
                                    
                                    # Validate minimum dimensions if available
                                    width = img.get('width', '0')
                                    height = img.get('height', '0')
                                    try:
                                        if (int(width) >= 300 and int(height) >= 200) or (width == '0' and height == '0'):
                                            image_url = src
                                            logger.info(f"Found relevant article image with class containing '{class_name}' via {attr}: {image_url}")
                                            break
                                    except (ValueError, TypeError):
                                        # If no dimensions specified, accept if other criteria pass
                                        if re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', src, re.I):
                                            image_url = src
                                            logger.info(f"Found relevant article image with class containing '{class_name}' via {attr}: {image_url}")
                                            break
                    if image_url:
                        break

            # Step 4: Look for images in specific article content containers (not sidebar/ads)
            if not image_url:
                # News-specific container selectors - focus on main content areas only
                news_containers = [
                    'article', '.article-content', '.story-content', '.post-content',
                    '.entry-content', '.main-content', '.article-body', '.story-body',
                    '.article-text', '.post-body', '.content-body', '.news-content',
                    '[data-module="ArticleBody"]', '[data-module="MediaObject"]',
                    '.article-wrapper', '.story-wrapper', '.content-wrapper'
                ]
                
                for container_selector in news_containers:
                    if image_url:
                        break
                    try:
                        containers = soup.select(container_selector)
                        for container in containers:
                            if image_url:
                                break
                            
                            # Skip containers that are clearly not main content
                            container_classes = ' '.join(container.get('class', []))
                            container_id = container.get('id', '')
                            if re.search(r'(sidebar|ad|advertisement|sponsor|widget|related|footer|header|nav|comment)', 
                                       container_classes + ' ' + container_id, re.I):
                                continue
                                
                            images = container.find_all('img')
                            # Get the first meaningful image in the article content
                            for img in images[:2]:  # Check only first 2 images to avoid unrelated content
                                for attr in image_attrs:
                                    src = img.get(attr)
                                    if (src and 
                                        not re.search(r'(logo|icon|avatar|banner|small|button|placeholder|ad|advertisement|sponsor|widget|social|share|comment)', src, re.I)):
                                        
                                        # Prefer larger images that are likely to be article images
                                        width = img.get('width', '0')
                                        height = img.get('height', '0')
                                        alt_text = img.get('alt', '').lower()
                                        
                                        # Check if alt text suggests it's a content image
                                        is_content_image = not re.search(r'(logo|icon|avatar|ad|advertisement|sponsor)', alt_text)
                                        
                                        try:
                                            if ((int(width) >= 300 and int(height) >= 200) or (width == '0' and height == '0')) and is_content_image:
                                                image_url = src.strip()
                                                logger.info(f"Found relevant large image in {container_selector} via {attr}: {image_url}")
                                                break
                                        except (ValueError, TypeError):
                                            # If no dimensions, check file extension and context
                                            if (re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', src, re.I) and 
                                                is_content_image and 
                                                len(src) > 20):  # Avoid tiny tracking pixels
                                                image_url = src.strip()
                                                logger.info(f"Found relevant image in {container_selector} via {attr}: {image_url}")
                                                break
                                if image_url:
                                    break
                    except Exception as e:
                        logger.debug(f"Error searching in container {container_selector}: {e}")

            # Step 5: Final fallback - only large, content-relevant images
            if not image_url:
                images = soup.find_all('img')
                for img in images:
                    # Only consider images that are clearly content images
                    img_parent = img.parent
                    parent_classes = ' '.join(img_parent.get('class', [])) if img_parent else ''
                    parent_id = img_parent.get('id', '') if img_parent else ''
                    alt_text = img.get('alt', '').lower()
                    
                    # Skip images in clearly non-content areas
                    if re.search(r'(sidebar|ad|advertisement|sponsor|widget|related|footer|header|nav|comment|social|share)', 
                               parent_classes + ' ' + parent_id + ' ' + alt_text, re.I):
                        continue
                    
                    # Try multiple source attributes
                    for attr in image_attrs:
                        if image_url:
                            break
                        src = img.get(attr)
                        if (src and 
                            not re.search(r'(logo|icon|avatar|banner|small|button|placeholder|sprite|ad|advertisement|sponsor|widget|social|share|comment)', src, re.I)):
                            
                            src = src.strip()
                            width = img.get('width', '0')
                            height = img.get('height', '0')
                            
                            # Only accept images that are likely to be article content
                            try:
                                area = int(width) * int(height)
                                if area >= 60000:  # Minimum 300x200 or equivalent
                                    image_url = src
                                    logger.info(f"Found large content image via {attr} attribute: {image_url}")
                                    break
                            except (ValueError, TypeError):
                                # If no dimensions, be very strict about file quality indicators
                                if (re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', src, re.I) and
                                    len(src) > 30 and  # Longer URLs usually indicate real content images
                                    not re.search(r'(thumb|small|mini|tiny|1x1|pixel)', src, re.I)):
                                    image_url = src
                                    logger.info(f"Found content image via {attr} attribute: {image_url}")
                                    break

        # If we found an image URL, download it
        if image_url:
            # Handle relative URLs
            if not image_url.startswith(('http://', 'https://')):
                # Extract base URL
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                if image_url.startswith('//'):
                    image_url = f"{parsed_url.scheme}:{image_url}"
                elif image_url.startswith('/'):
                    image_url = f"{base_url}{image_url}"
                else:
                    image_url = f"{base_url}/{image_url}"

            # Download the image using the same session
            try:
                # Add additional headers for image requests
                img_headers = headers.copy()
                img_headers.update({
                    "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Referer": url  # Important for some sites that check referrer
                })
                
                img_response = session.get(image_url, headers=img_headers, timeout=15, stream=True)
                if img_response.ok:
                    # Verify it's actually an image by checking content type and first few bytes
                    content_type = img_response.headers.get('content-type', '').lower()
                    if ('image' in content_type or 
                        any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif'])):
                        
                        # Read the content
                        img_content = img_response.content
                        
                        # Basic validation - check if it looks like an image
                        if len(img_content) > 1000:  # Minimum size for a meaningful image
                            # Check magic bytes for common image formats
                            is_valid_image = (
                                img_content[:2] == b'\xff\xd8' or  # JPEG
                                img_content[:8] == b'\x89PNG\r\n\x1a\n' or  # PNG
                                img_content[:6] in [b'GIF87a', b'GIF89a'] or  # GIF
                                img_content[:4] == b'RIFF' and img_content[8:12] == b'WEBP'  # WebP
                            )
                            
                            if is_valid_image or len(img_content) > 5000:  # Accept if likely image
                                with open(full_path, 'wb') as f:
                                    f.write(img_content)
                                logger.info(f"Saved image for {headline_id} from {image_url}")
                                return image_path
                            else:
                                logger.warning(f"Downloaded content doesn't appear to be a valid image: {image_url}")
                        else:
                            logger.warning(f"Downloaded image too small ({len(img_content)} bytes): {image_url}")
                    else:
                        logger.warning(f"Content type not an image ({content_type}): {image_url}")
                else:
                    logger.warning(f"Failed to download image: {img_response.status_code} from {image_url}")
            except Exception as img_err:
                logger.warning(f"Error downloading image from {image_url}: {img_err}")
        
        # Close the session
        session.close()
        
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

    # No image found or all methods failed, generate AI image instead of using default
    logger.info(f"No web image found for {headline_id}, generating AI image")
    return generate_ai_image(headline_id)

def generate_ai_image(headline_id):
    """
    Generate an image using OpenAI's DALL-E API for headlines that don't have images
    """
    ai_img_dir = ensure_ai_image_dir()
    image_path = f"static/images/ai-generated/{headline_id}.jpg"
    full_path = ai_img_dir / f"{headline_id}.jpg"

    # Check if we already have an AI image for this headline
    if os.path.exists(full_path):
        logger.info(f"Using existing AI-generated image for {headline_id}")
        return image_path + "#ai-generated"

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

    try:
        # Get the OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set or empty.")
            # Try to get a random AI image first, if none available, regenerate default
            fallback_result = get_random_ai_image()
            return fallback_result

        # Configure the OpenAI client - using the updated method we fixed earlier
        openai.api_key = api_key
        client = openai.OpenAI(max_retries=0)  # Disable retries to avoid time-consuming retry attempts

        # Generate prompt for DALL-E - optimized for financial imagery with content safety
        # Focus on the financial aspects rather than specific people or entities
        # Extract key financial terms from the headline
        financial_terms = ["market", "stock", "economy", "finance", "business", 
                          "investment", "trade", "growth", "recession", "inflation",
                          "dollar", "euro", "currency", "bank", "interest rate"]
        
        # Extract any financial terms that appear in the headline
        found_terms = [term for term in financial_terms if term.lower() in headline_text.lower()]
        terms_str = ", ".join(found_terms) if found_terms else "financial news"
        
        # Create a generic prompt focused on financial concepts
        prompt = f"Abstract financial illustration representing {terms_str}. Professional business style with charts, graphs, or symbolic imagery. No text or specific people."

        # Generate the image with DALL-E 2 at the optimal size for cost vs. quality
        try:
            logger.info(f"Generating AI image for headline: '{headline_text[:50]}...'")
            response = client.images.generate(
                model="dall-e-2",  # DALL-E 2 is more cost-effective than DALL-E 3
                prompt=prompt,
                size="512x512",  # Best balance between cost and quality (512x512 is mid-tier for DALL-E 2)
                n=1
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
            
            # Try a more simplified prompt as a fallback
            try:
                logger.info("Attempting with simplified fallback prompt...")
                # Use an extremely simplified, generic prompt that's unlikely to trigger filters
                # Choose one of several generic financial concepts
                fallback_concepts = [
                    "Stock market chart with rising trend",
                    "Financial data visualization with blue background",
                    "Business graph showing economic growth",
                    "Abstract financial data dashboard",
                    "Currency exchange concept with minimal design"
                ]
                fallback_prompt = random.choice(fallback_concepts)
                
                fallback_response = client.images.generate(
                    model="dall-e-2",
                    prompt=fallback_prompt,
                    size="512x512",
                    n=1
                )
                
                # Get image URL from fallback response
                fallback_image_url = fallback_response.data[0].url
                logger.info(f"Successfully generated AI image with fallback prompt")
                
                # Download the generated image
                img_response = requests.get(fallback_image_url, timeout=10)
                if img_response.ok:
                    with open(full_path, 'wb') as f:
                        f.write(img_response.content)
                    logger.info(f"Generated AI image for headline ID: {headline_id} with fallback prompt")
                    # Return the path with a flag that this is an AI-generated image
                    return image_path + "#ai-generated"
            except Exception as fallback_error:
                logger.error(f"Fallback OpenAI API attempt also failed: {fallback_error}")
            
            # When all AI generation attempts fail, try existing AI images first
            logger.warning(f"AI image generation failed, trying existing AI images for headline: '{headline_text[:50]}...'")
            fallback_result = get_random_ai_image()
            if fallback_result and "#ai-generated" in fallback_result:
                return fallback_result
            # If no AI images available, generate a new dynamic image
            dynamic_image_path = create_dynamic_image()
            if dynamic_image_path:
                return dynamic_image_path + "#dynamic"
            else:
                return "static/images/dynamic/fallback_error.jpg"

    except Exception as e:
        logger.error(f"Error generating AI image for headline ID {headline_id}: {e}")

    # Final fallback - try existing AI images first, then regenerate default
    logger.warning(f"Using fallback image for headline: '{headline_text[:50]}...'")
    fallback_result = get_random_ai_image()
    if fallback_result and "#ai-generated" in fallback_result:
        return fallback_result
    # If no AI images available, generate a new dynamic image
    dynamic_image_path = create_dynamic_image()
    if dynamic_image_path:
        return dynamic_image_path + "#dynamic"
    else:
        return "static/images/dynamic/fallback_error.jpg"

def fetch_financial_headlines():
    """
    Fetches financial headlines from multiple sources/APIs, applies a random weight to each source,
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
        fetch_yahoo_finance_headlines,
        fetch_reuters_headlines,
        fetch_bloomberg_headlines,
        fetch_cnbc_headlines,
        fetch_marketwatch_headlines,
        fetch_ft_headlines
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
