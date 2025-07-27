#!/usr/bin/env python3
"""
Test script to verify that dynamic images are regenerated with different patterns
"""

import os
import sys
import hashlib
from pathlib import Path

# Add src directory to path (parent directory contains src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news.news_fetcher import create_dynamic_image

def test_dynamic_regeneration():
    """Test that dynamic images are regenerated with different content"""
    print("Testing dynamic image regeneration...")
    
    # Create first dynamic image
    first_image_path = create_dynamic_image()
    if first_image_path:
        first_full_path = Path(first_image_path)
        if first_full_path.exists():
            with open(first_full_path, 'rb') as f:
                first_hash = hashlib.md5(f.read()).hexdigest()
            print(f"First image path: {first_image_path}")
            print(f"First image hash: {first_hash}")
        else:
            print(f"ERROR: First dynamic image was not created at {first_image_path}!")
            return False
    else:
        print("ERROR: create_dynamic_image() returned None!")
        return False
    
    # Create second dynamic image
    second_image_path = create_dynamic_image()
    if second_image_path:
        second_full_path = Path(second_image_path)
        if second_full_path.exists():
            with open(second_full_path, 'rb') as f:
                second_hash = hashlib.md5(f.read()).hexdigest()
            print(f"Second image path: {second_image_path}")
            print(f"Second image hash: {second_hash}")
        else:
            print(f"ERROR: Second dynamic image was not created at {second_image_path}!")
            return False
    else:
        print("ERROR: create_dynamic_image() returned None!")
        return False
    
    # Check if they are different
    if first_hash != second_hash:
        print("SUCCESS: Dynamic images are being regenerated with different content!")
        print(f"First image: {first_image_path}")
        print(f"Second image: {second_image_path}")
        return True
    else:
        print("WARNING: Dynamic images appear to be identical. This might be due to random chance.")
        return False

if __name__ == "__main__":
    success = test_dynamic_regeneration()
    sys.exit(0 if success else 1)
