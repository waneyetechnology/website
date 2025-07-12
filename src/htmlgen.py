from datetime import datetime
from .log import logger
import random
import time
from .minify_assets import minify_html

def generate_html(news, policies, econ, forex):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    
    # Generate cache-busting timestamp
    cache_buster = int(time.time())
    
    # Generate random colors for headlines
    def random_color():
        return f"#{random.randint(0, 0xFFFFFF):06x}"

    headline_colors1 = [random_color() for _ in news]
    headline_colors2 = [random_color() for _ in news]

    html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Waneye Financial Overview</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    
    <!-- Cache control meta tags to prevent browser caching -->
    <meta http-equiv='Cache-Control' content='no-cache, no-store, must-revalidate'>
    <meta http-equiv='Pragma' content='no-cache'>
    <meta http-equiv='Expires' content='0'>
    <meta name='last-modified' content='{now}'>
    
    <!-- Performance optimizations for resource loading -->
    <link rel='preconnect' href='https://cdn.jsdelivr.net' crossorigin>
    <link rel='preconnect' href='https://cdn.jsdelivr.net/gh' crossorigin>
    <link rel='dns-prefetch' href='https://cdn.jsdelivr.net'>
    <link rel='dns-prefetch' href='https://cdn.jsdelivr.net/gh'>
    <!-- Indicate to browsers that we'll be lazy-loading images -->
    <meta name='theme-color' content='#eaf6ff'>
    <link rel='icon' type='image/svg+xml' href='favicon.svg?v={cache_buster}'>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css'>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/gh/jellythemes/jelly-bootstrap@main/dist/jelly-bootstrap.min.css'>
    <link rel='stylesheet' href='static/style.css?v={cache_buster}'>
    <!-- Google Analytics 4 (GA4) tag -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-RSJVVBKXLG"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-RSJVVBKXLG');
    </script>
</head>
<body>
    <canvas id='bg-canvas'></canvas>
    <div class='container my-5'>
        <div class='text-center mb-4'>
            <h1 class='display-4 fw-bold'>Waneye Financial Overview</h1>
            <p class='text-muted' id='last-updated'><em>Last updated: {now}</em></p>
        </div>
        <div class='row g-4'>
            <div class='col-12'>
                <div class='card shadow-sm'>
                    <div class='card-header bg-primary text-white'>Top Financial Headlines</div>
                    <div class='card-body px-3 py-4'>
                        <div class='headline-grid'>
"""

    # Generate headline cards
    headline_cards = []
    for index, item in enumerate(news):
        # Check if the item has a local image path
        if item.get("image"):
            # Set loading and fetchpriority based on position
            # First 2-3 images get eager loading and high priority (visible above the fold)
            loading_attr = "eager" if index < 2 else "lazy"
            priority_attr = "high" if index < 2 else "auto"
            
            # Check for different image types/sources
            if "#dynamic" in item["image"]:
                # Use the dynamic image but with the headline as alt text and a special class
                actual_path = item["image"].split("#")[0]  # Remove the flag
                image_html = f"""<img src='{actual_path}' alt="{item["headline"]}" class='headline-image dynamic-image' loading="{loading_attr}" fetchpriority="{priority_attr}">
                <div class='dynamic-badge'>Dynamic</div>"""
            elif "#ai-generated" in item["image"]:
                # AI-generated image with special class - handle both folders
                actual_path = item["image"].split("#")[0]  # Remove the flag
                image_html = f"""<img src='{actual_path}' alt="{item["headline"]}" class='headline-image ai-generated-image' loading="{loading_attr}" fetchpriority="{priority_attr}">
                <div class='ai-badge'>AI</div>"""
            else:
                # Regular web-scraped image
                image_html = f"""<img src='{item["image"]}' alt="{item["headline"]}" class='headline-image' loading="{loading_attr}" fetchpriority="{priority_attr}">"""
        else:
            # Fallback for headlines without images (this should not happen)
            image_html = """<div class='placeholder-content d-flex align-items-center justify-content-center bg-light' style='height:100%'>
                    <div class='text-primary'>No image available</div>
                </div>"""

        card = f"""<div class='headline-card'>
                {image_html}
                <div class='headline-caption'>
                    <a href='{item["url"]}' target='_blank' title="{item["headline"]}">{item["headline"]}</a>
                </div>
            </div>"""
        headline_cards.append(card)

    html += "".join(headline_cards)

    html += f"""
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class='row g-4 mt-2'>
            <div class='col-md-4'>
                <div class='card shadow-sm'>
                    <div class='card-header bg-info text-white'>Central Bank Rates</div>
                    <ul class='list-group list-group-flush'>
"""

    # Generate policy items
    policy_items = []
    for item in policies:
        policy_items.append(f"<li class='list-group-item'><b>{item['bank']}:</b> {item['rate']}</li>")
    html += "".join(policy_items)

    html += f"""
                    </ul>
                </div>
            </div>
            <div class='col-md-4'>
                <div class='card shadow-sm'>
                    <div class='card-header bg-success text-white'>Key Economic Data</div>
                    <ul class='list-group list-group-flush'>
"""

    # Generate economic data items
    econ_items = []
    for item in econ:
        econ_items.append(f"<li class='list-group-item'>{item['event']}: {item['value']} ({item['date']})</li>")
    html += "".join(econ_items)

    html += f"""
                    </ul>
                </div>
            </div>
            <div class='col-md-4'>
                <div class='card shadow-sm'>
                    <div class='card-header bg-warning text-dark'>Forex CFD Quotes</div>
                    <div class='table-responsive'>
                        <table class='table table-bordered mb-0'>
                            <thead class='table-light'><tr><th>Pair</th><th>Bid</th><th>Ask</th></tr></thead>
                            <tbody>
"""

    # Generate forex items
    forex_items = []
    for item in forex:
        forex_items.append(f"<tr><td>{item['pair']}</td><td>{item['bid']}</td><td>{item['ask']}</td></tr>")
    html += "".join(forex_items)

    html += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        <footer class='text-center mt-5 text-muted'>
            <hr>
            <small>Generated by Waneye.com &mdash; Powered by JellyThemes</small>
        </footer>
    </div>
    <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'></script>
    <script src='static/main.js?v={cache_buster}'></script>
</body>
</html>
"""
    return minify_html(html)
