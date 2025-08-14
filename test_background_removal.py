#!/usr/bin/env python3
"""
Test script for background removal API
"""

import requests
import json
import base64
from PIL import Image
from io import BytesIO

def test_background_removal():
    """Test the background removal endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/ai/remove-background"
    
    # Test image URL (person with background)
    test_image_url = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500"
    
    # Request payload
    payload = {
        "image_url": test_image_url
    }
    
    print("🧪 Testing Background Removal API")
    print("=" * 50)
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
                
                # Save the result image
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(result["image_base64"])
                    image = Image.open(BytesIO(image_data))
                    
                    # Save to file
                    output_filename = "background_removed.png"
                    image.save(output_filename)
                    print(f"💾 Saved result as: {output_filename}")
                    
                except Exception as e:
                    print(f"❌ Error saving image: {e}")
                
            else:
                print(f"❌ Background removal failed: {result['error']}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for first run as models load)")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoints():
    """Test health endpoints"""
    
    print("\n🏥 Testing Health Endpoints")
    print("=" * 30)
    
    endpoints = [
        ("Hello", "http://localhost:8000/api/v1/hello"),
        ("Health", "http://localhost:8000/api/v1/health"),
        ("Background Service", "http://localhost:8000/api/v1/ai/health/background-removal")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

if __name__ == "__main__":
    print("🚀 SparkIQ AI Image Enhancement API Test")
    print("=" * 50)
    
    # Test health endpoints first
    test_health_endpoints()
    
    # Test background removal
    test_background_removal()
    
    print("\n📖 API Documentation: http://localhost:8000/docs")
    print("🎨 Try the interactive docs to test more features!") 