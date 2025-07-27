#!/usr/bin/env python3
"""
Simple test for browser automation image extraction
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, '/home/avo/Start/waneye/website')

def test_playwright_basic():
    """Test basic Playwright functionality"""
    try:
        from playwright.sync_api import sync_playwright
        
        print("Testing basic Playwright functionality...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Test with a simple page
            page.goto("https://www.nbcnews.com/business", timeout=30000)
            title = page.title()
            print(f"Page title: {title}")
            
            # Try to extract meta og:image
            og_image = page.evaluate("""() => {
                const meta = document.querySelector('meta[property="og:image"]');
                return meta ? meta.content : null;
            }""")
            
            if og_image:
                print(f"Found OG image: {og_image}")
            else:
                print("No OG image found")
            
            # Try to find any images
            images = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                return imgs.slice(0, 5).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.width,
                    height: img.height
                }));
            }""")
            
            print(f"Found {len(images)} images:")
            for img in images:
                print(f"  - {img['src'][:100]}... (alt: {img['alt'][:50]}, {img['width']}x{img['height']})")
            
            browser.close()
            
        print("Playwright test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    test_playwright_basic()
