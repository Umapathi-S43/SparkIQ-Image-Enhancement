#!/usr/bin/env python3
"""
Test script for background removal API with local file saving
"""

import requests
import json
import os

def test_background_removal():
    """Test the background removal API with local file saving"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/ai/remove-background"
    
    # Test image URL
    test_image_url = "https://15buttons.in/cdn/shop/files/IMG_20240606_115219_fb4fdea1-99b1-44eb-b2e9-16cf15277a74_2048x2048.jpg?v=1720450153"
    
    # Request payload
    payload = {
        "image_url": test_image_url
    }
    
    print("🧪 Testing Background Removal API (Local Save)")
    print("=" * 60)
    print(f"📷 Test Image: {test_image_url}")
    print(f"🌐 API Endpoint: {url}")
    print()
    
    try:
        # Make request
        print("🔄 Sending request...")
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                print("✅ Background removal successful!")
                print(f"📏 Original size: {result['original_size']}")
                print(f"📏 Processed size: {result['processed_size']}")
                print(f"📄 Format: {result['format']}")
                print(f"💾 Saved as: {result['filename']}")
                
                # Check if file exists
                if os.path.exists(result['filename']):
                    file_size = os.path.getsize(result['filename'])
                    print(f"📊 File size: {file_size:,} bytes")
                    print(f"✅ File saved successfully!")
                else:
                    print(f"❌ File not found: {result['filename']}")
                
            else:
                print(f"❌ Background removal failed: {result['error']}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_processed_images():
    """List all processed images in the output directory"""
    print("\n📁 Listing Processed Images")
    print("=" * 40)
    
    output_dir = "processed_images"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"Found {len(files)} processed images:")
            for file in sorted(files):
                filepath = os.path.join(output_dir, file)
                size = os.path.getsize(filepath)
                print(f"  📄 {file} ({size:,} bytes)")
        else:
            print("No processed images found.")
    else:
        print("Output directory not found.")

if __name__ == "__main__":
    print("🚀 SparkIQ AI Image Enhancement - Local File Save Test")
    print("=" * 70)
    
    # Test the API
    test_background_removal()
    
    # List processed images
    list_processed_images()
    
    print("\n📖 API Documentation: http://localhost:8000/docs")
    print("📁 Check the 'processed_images' folder for saved files!") 