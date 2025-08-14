#!/usr/bin/env python3
"""
Test script to call the background removal API and save the result as PNG
"""

import requests
import base64
from PIL import Image
from io import BytesIO
import json

def test_and_save_image():
    """Test the API and save the result image"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/ai/remove-background"
    
    # Test image URL (you can change this to any image URL)
    test_image_url = "https://15buttons.in/cdn/shop/files/IMG_20240606_115219_fb4fdea1-99b1-44eb-b2e9-16cf15277a74_2048x2048.jpg?v=1720450153"
    
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
                
                # Convert base64 to image and save
                try:
                    # Decode base64 image
                    print("🔄 Converting base64 to image...")
                    image_data = base64.b64decode(result["image_base64"])
                    image = Image.open(BytesIO(image_data))
                    
                    # Save to file
                    output_filename = "background_removed_result.png"
                    image.save(output_filename, format='PNG')
                    print(f"💾 Saved result as: {output_filename}")
                    
                    # Show image info
                    print(f"📊 Image saved with size: {image.size}")
                    print(f"🎨 Image mode: {image.mode}")
                    
                    # Also save as JPEG for comparison
                    jpeg_filename = "background_removed_result.jpg"
                    if image.mode == 'RGBA':
                        # Convert RGBA to RGB for JPEG
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                        rgb_image.save(jpeg_filename, format='JPEG', quality=95)
                    else:
                        image.save(jpeg_filename, format='JPEG', quality=95)
                    print(f"💾 Also saved as JPEG: {jpeg_filename}")
                    
                except Exception as e:
                    print(f"❌ Error saving image: {e}")
                
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

def test_with_custom_url():
    """Test with a custom image URL"""
    print("\n🎯 Test with Custom Image URL")
    print("=" * 40)
    
    # You can change this URL to any image you want to test
    custom_url = input("Enter image URL (or press Enter for default): ").strip()
    
    if not custom_url:
        custom_url = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500"
        print(f"Using default URL: {custom_url}")
    
    # API endpoint
    url = "http://localhost:8000/api/v1/ai/remove-background"
    
    payload = {
        "image_url": custom_url
    }
    
    try:
        print("🔄 Processing custom image...")
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                # Save the result
                image_data = base64.b64decode(result["image_base64"])
                image = Image.open(BytesIO(image_data))
                
                output_filename = "custom_background_removed.png"
                image.save(output_filename, format='PNG')
                print(f"✅ Custom image processed and saved as: {output_filename}")
                
            else:
                print(f"❌ Failed: {result['error']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 SparkIQ AI Image Enhancement - Image Saver")
    print("=" * 60)
    
    # Test with the default image
    test_and_save_image()
    
    # Ask if user wants to test with custom URL
    print("\n" + "=" * 60)
    choice = input("Do you want to test with a custom image URL? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes']:
        test_with_custom_url()
    
    print("\n📁 Check your current directory for the saved images!")
    print("📖 API Documentation: http://localhost:8000/docs") 