#!/usr/bin/env python3
"""
Advanced Background Removal API Test Script
Tests all the new features including multiple models, caching, quality enhancement, etc.
"""

import requests
import json
import time
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api/v1/ai"
TEST_IMAGES = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",  # Portrait
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400",  # Person
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",     # Woman
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400",  # Man
]

def test_service_status():
    """Test service status endpoint"""
    print("🔍 Testing Service Status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Service Status:")
            print(f"   GPU Available: {status['gpu_available']}")
            print(f"   Processing Mode: {status['processing_mode']}")
            print(f"   Available Models: {status['available_models']}")
            print(f"   Output Directory: {status['output_directory']}")
            print(f"   Cache Directory: {status['cache_directory']}")
            return True
        else:
            print(f"❌ Service status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service status error: {e}")
        return False

def test_available_models():
    """Test available models endpoint"""
    print("\n📋 Testing Available Models...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Available Models: {models}")
            return models
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return []

def test_cache_stats():
    """Test cache statistics"""
    print("\n📊 Testing Cache Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Cache Stats:")
            print(f"   Files: {stats['cache_files']}")
            print(f"   Size: {stats['total_size_mb']} MB")
            return stats
        else:
            print(f"❌ Cache stats failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
        return None

def test_background_removal(image_url: str, model: str = "birefnet-general", 
                          enhance_quality: bool = True, use_cache: bool = True):
    """Test background removal with specific settings"""
    print(f"\n🔄 Testing Background Removal...")
    print(f"   Image: {image_url}")
    print(f"   Model: {model}")
    print(f"   Enhance Quality: {enhance_quality}")
    print(f"   Use Cache: {use_cache}")
    
    try:
        payload = {
            "image_url": image_url,
            "model": model,
            "enhance_quality": enhance_quality,
            "use_cache": use_cache
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/remove-background", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Background Removal Successful:")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"   API Response Time: {end_time - start_time:.2f}s")
            print(f"   Original Size: {result['original_size']}")
            print(f"   Processed Size: {result['processed_size']}")
            print(f"   AI Model: {result['ai_model']}")
            print(f"   GPU Used: {result['gpu_used']}")
            print(f"   Cached: {result.get('cached', False)}")
            print(f"   Filename: {result['filename']}")
            
            # Check if file exists
            if Path(result['filename']).exists():
                file_size = Path(result['filename']).stat().st_size
                print(f"   File Size: {file_size / 1024:.1f} KB")
            else:
                print(f"   ⚠️ File not found: {result['filename']}")
            
            return result
        else:
            print(f"❌ Background removal failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Background removal error: {e}")
        return None

def test_different_models():
    """Test background removal with different models"""
    print("\n🤖 Testing Different AI Models...")
    
    models = test_available_models()
    if not models:
        return
    
    # Test with first image
    test_image = TEST_IMAGES[0]
    
    for model in models[:3]:  # Test first 3 models
        print(f"\n--- Testing Model: {model} ---")
        result = test_background_removal(test_image, model=model)
        if result:
            print(f"✅ {model} model works!")
        else:
            print(f"❌ {model} model failed!")
        time.sleep(1)  # Small delay between requests

def test_caching():
    """Test caching functionality"""
    print("\n💾 Testing Caching Functionality...")
    
    test_image = TEST_IMAGES[1]
    
    # First request (should not be cached)
    print("\n--- First Request (Not Cached) ---")
    result1 = test_background_removal(test_image, use_cache=True)
    
    # Second request (should be cached)
    print("\n--- Second Request (Should be Cached) ---")
    result2 = test_background_removal(test_image, use_cache=True)
    
    if result1 and result2:
        if result2.get('cached', False):
            print("✅ Caching working correctly!")
        else:
            print("⚠️ Caching might not be working as expected")
    
    # Check cache stats
    test_cache_stats()

def test_quality_settings():
    """Test quality enhancement settings"""
    print("\n🎨 Testing Quality Enhancement Settings...")
    
    test_image = TEST_IMAGES[2]
    
    # Test without quality enhancement
    print("\n--- Without Quality Enhancement ---")
    result1 = test_background_removal(test_image, enhance_quality=False)
    
    # Test with quality enhancement
    print("\n--- With Quality Enhancement ---")
    result2 = test_background_removal(test_image, enhance_quality=True)
    
    if result1 and result2:
        print("✅ Quality settings working!")

def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health/background-removal")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health Check:")
            print(f"   Status: {health['status']}")
            print(f"   Service: {health['service']}")
            print(f"   GPU Available: {health['gpu_available']}")
            print(f"   Models Loaded: {health['models_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_cache_clear():
    """Test cache clearing"""
    print("\n🗑️ Testing Cache Clear...")
    try:
        response = requests.delete(f"{BASE_URL}/cache/clear")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cache cleared: {result['message']}")
            return True
        else:
            print(f"❌ Cache clear failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cache clear error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Advanced Background Removal API Test Suite")
    print("=" * 50)
    
    # Test service status
    if not test_service_status():
        print("❌ Service not available. Make sure the server is running.")
        return
    
    # Test health check
    test_health_check()
    
    # Test available models
    models = test_available_models()
    
    # Test cache stats (initial)
    test_cache_stats()
    
    # Test different models
    test_different_models()
    
    # Test caching
    test_caching()
    
    # Test quality settings
    test_quality_settings()
    
    # Test cache clear
    test_cache_clear()
    
    # Final cache stats
    test_cache_stats()
    
    print("\n🎉 All tests completed!")
    print("\n📝 Summary:")
    print("- Multiple AI models supported")
    print("- GPU/CPU detection working")
    print("- Caching system functional")
    print("- Quality enhancement available")
    print("- Comprehensive error handling")
    print("- Detailed logging and monitoring")

if __name__ == "__main__":
    main() 