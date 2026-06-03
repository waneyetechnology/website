#!/usr/bin/env python3
"""
Comprehensive test of the new browser automation image extraction functionality
"""

import sys
import os
import hashlib
from pathlib import Path

# Add the project root to path 
sys.path.append(os.getcwd())

def test_image_extraction_integration():
    """Test the complete image extraction workflow"""
    import src.news as news
    
    print("=== Testing Browser Automation Image Extraction ===\n")
    
    # Test URLs that should have good images
    test_cases = [
        {
            "url": "https://www.nbcnews.com/business",
            "name": "NBC News Business",
            "expected": "Should find OG image or main article images"
        },
        {
            "url": "https://finance.yahoo.com/news/",
            "name": "Yahoo Finance News", 
            "expected": "Should find featured article images"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Generate unique headline ID for this test
        headline_id = f"test_{hashlib.md5(test_case['url'].encode()).hexdigest()[:8]}"
        
        try:
            # Test browser automation method
            print("   Testing browser automation...")
            result_browser = news.fetch_image_with_browser_automation(test_case['url'], headline_id + "_browser")
            print(f"   Browser result: {result_browser}")
            
            # Test traditional method for comparison
            print("   Testing traditional method...")
            result_traditional = news.fetch_and_save_image_traditional(test_case['url'], headline_id + "_traditional")
            print(f"   Traditional result: {result_traditional}")
            
            # Test main function (which combines both methods)
            print("   Testing main function...")
            result_main = news.fetch_and_save_image(test_case['url'], headline_id + "_main")
            print(f"   Main function result: {result_main}")
            
            # Check if actual image files were created
            images_dir = Path("static/images/headlines")
            browser_image = images_dir / f"{headline_id}_browser.jpg"
            traditional_image = images_dir / f"{headline_id}_traditional.jpg"  
            main_image = images_dir / f"{headline_id}_main.jpg"
            
            print("   File results:")
            print(f"   - Browser automation: {'✓' if browser_image.exists() else '✗'} ({browser_image})")
            print(f"   - Traditional method: {'✓' if traditional_image.exists() else '✗'} ({traditional_image})")
            print(f"   - Main function: {'✓' if main_image.exists() else '✗'} ({main_image})")
            
            # Show file sizes if they exist
            for name, path in [("Browser", browser_image), ("Traditional", traditional_image), ("Main", main_image)]:
                if path.exists():
                    size = path.stat().st_size
                    print(f"     {name} image size: {size:,} bytes")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("   " + "="*50)
        print()

def test_headline_integration():
    """Test browser automation with actual news headlines"""
    import src.news as news
    
    print("=== Testing with Real Headlines ===\n")
    
    # First test getting some headlines from RSS feeds (these don't require API keys)
    print("1. Fetching real headlines...")
    
    try:
        # Test with RSS feeds that don't need API keys
        yahoo_headlines = news.fetch_yahoo_finance_headlines()
        reuters_headlines = news.fetch_reuters_headlines()
        
        print(f"   Yahoo Finance headlines: {len(yahoo_headlines)}")
        print(f"   Reuters headlines: {len(reuters_headlines)}")
        
        # Take first headline from each source for testing
        test_headlines = []
        if yahoo_headlines:
            test_headlines.append(("Yahoo Finance", yahoo_headlines[0]))
        if reuters_headlines:
            test_headlines.append(("Reuters", reuters_headlines[0]))
        
        print("\n2. Testing image extraction for real headlines:")
        
        for source, headline in test_headlines:
            print(f"\n   Testing {source} headline:")
            print(f"   Title: {headline['headline'][:80]}...")
            print(f"   URL: {headline['url']}")
            
            headline_id = hashlib.md5(headline['url'].encode()).hexdigest()
            
            try:
                # Test with our new browser automation
                result = news.fetch_and_save_image(headline['url'], headline_id)
                print(f"   Image result: {result}")
                
                # Check if image was actually saved
                if result and not result.endswith("#ai-generated") and not result.endswith("#dynamic"):
                    image_path = Path(result)
                    if image_path.exists():
                        size = image_path.stat().st_size
                        print(f"   ✓ Successfully saved image: {size:,} bytes")
                    else:
                        print(f"   ✗ Image path returned but file not found: {image_path}")
                elif result and result.endswith("#ai-generated"):
                    print(f"   ○ Fallback to AI-generated image")
                elif result and result.endswith("#dynamic"):
                    print(f"   ○ Fallback to dynamic image")
                else:
                    print(f"   ✗ No image result")
                    
            except Exception as e:
                print(f"   ❌ Error extracting image: {e}")
    
    except Exception as e:
        print(f"❌ Error fetching headlines: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting comprehensive browser automation test...\n")
    
    # Ensure image directories exist
    for dir_name in ["headlines", "ai-generated", "dynamic"]:
        Path(f"static/images/{dir_name}").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    test_image_extraction_integration()
    test_headline_integration()
    
    print("\n=== Test Summary ===")
    print("Browser automation image extraction testing completed!")
    print("Check the static/images/headlines/ directory for extracted images.")
