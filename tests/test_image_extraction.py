#!/usr/bin/env python3
"""
Test script for the new browser automation image extraction functionality.
"""

import os
import sys
import hashlib
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_image_extraction():
    """Test image extraction with browser automation on a known news site"""
    from src.news import fetch_image_with_browser_automation, fetch_and_save_image_traditional, fetch_and_save_image
    
    # Test URLs that should have images
    test_urls = [
        "https://www.nbcnews.com/business",  # NBC News business section
        "https://finance.yahoo.com/",        # Yahoo Finance
        "https://www.cnbc.com/business/",    # CNBC Business
    ]
    
    print("Testing browser automation image extraction...")
    
    for url in test_urls:
        print(f"\n--- Testing URL: {url} ---")
        
        # Generate a test headline ID
        headline_id = hashlib.md5(url.encode()).hexdigest()
        
        try:
            # Test browser automation
            print("1. Testing browser automation method...")
            result_browser = fetch_image_with_browser_automation(url, headline_id + "_browser")
            print(f"   Browser automation result: {result_browser}")
            
            # Test traditional method for comparison
            print("2. Testing traditional method...")
            result_traditional = fetch_and_save_image_traditional(url, headline_id + "_traditional")
            print(f"   Traditional method result: {result_traditional}")
            
            # Test the main function (which tries browser first, then traditional)
            print("3. Testing main fetch_and_save_image function...")
            result_main = fetch_and_save_image(url, headline_id + "_main")
            print(f"   Main function result: {result_main}")
            
        except Exception as e:
            print(f"   Error testing {url}: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_image_extraction()
