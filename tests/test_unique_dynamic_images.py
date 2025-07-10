#!/usr/bin/env python3
"""
Test script to verify that dynamic images are now saved with unique filenames
"""

import os
import sys
import hashlib
from pathlib import Path

# Add src directory to path (parent directory contains src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news import create_dynamic_image, get_random_ai_image

def test_unique_dynamic_images():
    """Test that dynamic images are saved with unique filenames"""
    print("Testing unique dynamic image filenames...")
    
    # Test direct creation
    print("\n1. Testing direct create_dynamic_image() calls:")
    
    images_created = []
    for i in range(3):
        image_path = create_dynamic_image()
        if image_path:
            images_created.append(image_path)
            print(f"   Created: {image_path}")
        else:
            print(f"   ERROR: create_dynamic_image() returned None on attempt {i+1}")
    
    # Check that all paths are different
    if len(set(images_created)) == len(images_created):
        print("   SUCCESS: All dynamic images have unique filenames!")
    else:
        print("   ERROR: Some dynamic images have duplicate filenames!")
        return False
    
    # Test through get_random_ai_image fallback
    print("\n2. Testing get_random_ai_image() fallback:")
    
    ai_fallback_images = []
    for i in range(3):
        result = get_random_ai_image()
        if result and "#dynamic" in result:
            path = result.split("#")[0]
            ai_fallback_images.append(path)
            print(f"   Created via fallback: {path}")
        else:
            print(f"   Result: {result} (not a dynamic image)")
    
    # Check that fallback images are also unique
    if len(set(ai_fallback_images)) == len(ai_fallback_images):
        print("   SUCCESS: All fallback dynamic images have unique filenames!")
    else:
        print("   ERROR: Some fallback dynamic images have duplicate filenames!")
        return False
    
    # Check that all files actually exist
    print("\n3. Verifying files exist:")
    all_images = images_created + ai_fallback_images
    for image_path in all_images:
        if os.path.exists(image_path):
            print(f"   ✓ {image_path}")
        else:
            print(f"   ✗ {image_path} (MISSING)")
            return False
    
    print(f"\n4. Summary:")
    print(f"   Total unique dynamic images created: {len(all_images)}")
    print(f"   Dynamic images directory: static/images/dynamic/")
    
    # List all files in the dynamic directory
    dynamic_dir = Path("static/images/dynamic")
    if dynamic_dir.exists():
        files = list(dynamic_dir.glob("*.jpg"))
        print(f"   Files in dynamic directory: {len(files)}")
        for file in files:
            print(f"     - {file.name}")
    
    return True

if __name__ == "__main__":
    success = test_unique_dynamic_images()
    if success:
        print("\n✅ All tests passed! Dynamic images are now saved with unique filenames.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
