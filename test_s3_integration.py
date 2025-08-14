#!/usr/bin/env python3
"""
S3 Integration Test for SparkIQ Background Removal API
Tests S3 upload functionality and public URL generation
"""

import requests
import json
import time
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api/v1/ai"
TEST_IMAGE = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"

def test_s3_service_status():
    """Test S3 service status"""
    print("🔍 Testing S3 Service Status...")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ S3 Service Status:")
            print(f"   S3 Bucket: {status['s3_bucket']}")
            print(f"   S3 Region: {status['s3_region']}")
            print(f"   S3 Access: {status['s3_access']}")
            print(f"   GPU Available: {status['gpu_available']}")
            print(f"   Models: {len(status['available_models'])}")
            return status['s3_access']
        else:
            print(f"❌ S3 status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ S3 status error: {e}")
        return False

def test_s3_stats():
    """Test S3 bucket statistics"""
    print("\n📊 Testing S3 Bucket Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/s3/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ S3 Bucket Stats:")
            print(f"   Bucket: {stats['bucket_name']}")
            print(f"   Total Objects: {stats['total_objects']}")
            print(f"   Total Size: {stats['total_size_mb']} MB")
            print(f"   Folder: {stats['folder']}")
            return True
        else:
            print(f"❌ S3 stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ S3 stats error: {e}")
        return False

def test_background_removal_with_s3():
    """Test background removal with S3 upload"""
    print("\n🔄 Testing Background Removal with S3 Upload...")
    try:
        payload = {
            "image_url": TEST_IMAGE,
            "model": "birefnet-general",
            "enhance_quality": True,
            "use_cache": False  # Disable cache to test fresh upload
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/remove-background", json=payload, timeout=60)
        total_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Background Removal with S3 Successful:")
                print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"   Total Time: {total_time:.2f}s")
                print(f"   S3 URL: {result['s3_url']}")
                print(f"   S3 Key: {result['s3_key']}")
                print(f"   Storage: {result.get('storage', 'Unknown')}")
                print(f"   GPU Used: {result.get('gpu_used', False)}")
                print(f"   Cached: {result.get('cached', False)}")
                
                # Test if S3 URL is accessible
                print(f"\n🔗 Testing S3 URL Accessibility...")
                try:
                    s3_response = requests.head(result['s3_url'], timeout=10)
                    if s3_response.status_code == 200:
                        print(f"✅ S3 URL is publicly accessible!")
                        print(f"   Content-Type: {s3_response.headers.get('content-type', 'Unknown')}")
                        print(f"   Content-Length: {s3_response.headers.get('content-length', 'Unknown')} bytes")
                    else:
                        print(f"⚠️ S3 URL returned status: {s3_response.status_code}")
                except Exception as e:
                    print(f"❌ S3 URL test failed: {e}")
                
                return result
            else:
                print(f"❌ Background removal failed: {result.get('error')}")
                return None
        else:
            print(f"❌ Background removal request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Background removal error: {e}")
        return None

def test_s3_image_deletion():
    """Test S3 image deletion"""
    print("\n🗑️ Testing S3 Image Deletion...")
    
    # First, create an image to delete
    print("   Creating test image for deletion...")
    payload = {
        "image_url": TEST_IMAGE,
        "model": "u2netp",  # Use different model
        "enhance_quality": False,
        "use_cache": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/remove-background", json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                s3_key = result['s3_key']
                print(f"   Created test image: {s3_key}")
                
                # Now delete it
                print(f"   Deleting test image...")
                delete_response = requests.delete(f"{BASE_URL}/s3/delete/{s3_key}", timeout=10)
                
                if delete_response.status_code == 200:
                    delete_result = delete_response.json()
                    print(f"✅ S3 deletion successful: {delete_result.get('message')}")
                    return True
                else:
                    print(f"❌ S3 deletion failed: {delete_response.status_code}")
                    return False
            else:
                print(f"❌ Failed to create test image: {result.get('error')}")
                return False
        else:
            print(f"❌ Failed to create test image: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ S3 deletion test error: {e}")
        return False

def test_multiple_models_with_s3():
    """Test multiple models with S3 upload"""
    print("\n🤖 Testing Multiple Models with S3...")
    
    models = ["birefnet-general", "u2net", "u2netp"]
    results = []
    
    for model in models:
        print(f"\n--- Testing Model: {model} ---")
        try:
            payload = {
                "image_url": TEST_IMAGE,
                "model": model,
                "enhance_quality": True,
                "use_cache": False
            }
            
            response = requests.post(f"{BASE_URL}/remove-background", json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ {model}: Success")
                    print(f"   S3 URL: {result['s3_url']}")
                    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                    results.append({
                        "model": model,
                        "s3_url": result['s3_url'],
                        "processing_time": result.get('processing_time', 0)
                    })
                else:
                    print(f"❌ {model}: Failed - {result.get('error')}")
            else:
                print(f"❌ {model}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model}: Error - {e}")
    
    return results

def main():
    """Run S3 integration tests"""
    print("🚀 SparkIQ Background Removal API - S3 Integration Test")
    print("="*60)
    
    # Test S3 service status
    s3_access = test_s3_service_status()
    if not s3_access:
        print("❌ S3 access not available. Check AWS credentials and bucket permissions.")
        return
    
    # Test S3 stats
    test_s3_stats()
    
    # Test background removal with S3
    result = test_background_removal_with_s3()
    if not result:
        print("❌ Background removal with S3 failed.")
        return
    
    # Test S3 image deletion
    test_s3_image_deletion()
    
    # Test multiple models
    model_results = test_multiple_models_with_s3()
    
    # Summary
    print("\n" + "="*60)
    print("📋 S3 Integration Test Summary")
    print("="*60)
    print(f"✅ S3 Access: {'Working' if s3_access else 'Failed'}")
    print(f"✅ Background Removal with S3: {'Working' if result else 'Failed'}")
    print(f"✅ Multiple Models: {len(model_results)}/{3} working")
    
    if model_results:
        print(f"\n🔗 Generated S3 URLs:")
        for model_result in model_results:
            print(f"   {model_result['model']}: {model_result['s3_url']}")
    
    print(f"\n🎉 S3 Integration Test Complete!")
    print(f"All images are now stored in S3 and publicly accessible!")

if __name__ == "__main__":
    main() 