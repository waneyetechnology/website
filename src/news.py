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
            # Always create a colorful new default image instead of copying an existing one
            # This ensures we get our vibrant, randomized design
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

                # Add some text to indicate this is a default image
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
                        logger.debug(f"Could not load font for default image: {font_err}")
                except ImportError:
                    logger.debug("ImageFont not available, skipping text overlay")

                # Save the image at high quality
                img.save(default_img_path, 'JPEG', quality=95)
                logger.info("Created new vibrant default.jpg image")
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
            
            # When all AI generation attempts fail, use default.jpg
            logger.warning(f"AI image generation failed, using default.jpg for headline: '{headline_text[:50]}...'")
            return "static/images/headlines/default.jpg"

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
