#!/usr/bin/env python3
"""
Production Readiness Check for SparkIQ Background Removal API
Comprehensive testing of all production-critical features
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AI_BASE_URL = f"{BASE_URL}/ai"
TEST_IMAGE = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"

class ProductionReadinessChecker:
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        self.results[test_name] = {
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        print(f"{'✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'} {test_name}: {details}")
    
    def test_basic_connectivity(self):
        """Test basic server connectivity"""
        print("\n🔌 Testing Basic Connectivity...")
        try:
            response = requests.get(f"{BASE_URL}/hello", timeout=5)
            if response.status_code == 200:
                self.log_result("Basic Connectivity", "PASS", "Server is responding")
                return True
            else:
                self.log_result("Basic Connectivity", "FAIL", f"Server returned {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Basic Connectivity", "FAIL", f"Connection failed: {e}")
            return False
    
    def test_health_endpoints(self):
        """Test all health check endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Test main health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Main Health Check", "PASS", "Main health endpoint working")
            else:
                self.log_result("Main Health Check", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Main Health Check", "FAIL", f"Error: {e}")
        
        # Test AI service status
        try:
            response = requests.get(f"{AI_BASE_URL}/status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                self.log_result("AI Service Status", "PASS", 
                              f"GPU: {status['gpu_available']}, Models: {len(status['available_models'])}")
            else:
                self.log_result("AI Service Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AI Service Status", "FAIL", f"Error: {e}")
        
        # Test AI health check
        try:
            response = requests.get(f"{AI_BASE_URL}/health/background-removal", timeout=10)
            if response.status_code == 200:
                health = response.json()
                self.log_result("AI Health Check", "PASS", f"Status: {health.get('status', 'unknown')}")
            else:
                self.log_result("AI Health Check", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AI Health Check", "FAIL", f"Error: {e}")
    
    def test_background_removal_functionality(self):
        """Test core background removal functionality"""
        print("\n🔄 Testing Background Removal Functionality...")
        
        try:
            payload = {
                "image_url": TEST_IMAGE,
                "model": "birefnet-general",
                "enhance_quality": True,
                "use_cache": True
            }
            
            start_time = time.time()
            response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Background Removal", "PASS", 
                                  f"Success in {processing_time:.2f}s, GPU: {result.get('gpu_used')}")
                    
                    # Check if file was created
                    filename = result.get("filename")
                    if filename and Path(filename).exists():
                        file_size = Path(filename).stat().st_size
                        self.log_result("File Creation", "PASS", f"File created: {file_size/1024:.1f} KB")
                    else:
                        self.log_result("File Creation", "FAIL", "Output file not found")
                else:
                    self.log_result("Background Removal", "FAIL", f"Processing failed: {result.get('error')}")
            else:
                self.log_result("Background Removal", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Background Removal", "FAIL", f"Error: {e}")
    
    def test_model_variety(self):
        """Test different AI models"""
        print("\n🤖 Testing AI Model Variety...")
        
        try:
            response = requests.get(f"{AI_BASE_URL}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                self.log_result("Model Discovery", "PASS", f"Found {len(models)} models: {models}")
                
                # Test a few different models
                test_models = models[:2]  # Test first 2 models
                for model in test_models:
                    try:
                        payload = {
                            "image_url": TEST_IMAGE,
                            "model": model,
                            "enhance_quality": False,
                            "use_cache": False
                        }
                        
                        response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                self.log_result(f"Model {model}", "PASS", "Working correctly")
                            else:
                                self.log_result(f"Model {model}", "FAIL", f"Failed: {result.get('error')}")
                        else:
                            self.log_result(f"Model {model}", "FAIL", f"HTTP {response.status_code}")
                    except Exception as e:
                        self.log_result(f"Model {model}", "FAIL", f"Error: {e}")
            else:
                self.log_result("Model Discovery", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Model Discovery", "FAIL", f"Error: {e}")
    
    def test_caching_system(self):
        """Test caching functionality"""
        print("\n💾 Testing Caching System...")
        
        try:
            # Test cache stats
            response = requests.get(f"{AI_BASE_URL}/cache/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_result("Cache Stats", "PASS", f"Files: {stats['cache_files']}, Size: {stats['total_size_mb']} MB")
            else:
                self.log_result("Cache Stats", "FAIL", f"HTTP {response.status_code}")
            
            # Test cache clearing
            response = requests.delete(f"{AI_BASE_URL}/cache/clear", timeout=10)
            if response.status_code == 200:
                self.log_result("Cache Clear", "PASS", "Cache cleared successfully")
            else:
                self.log_result("Cache Clear", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Caching System", "FAIL", f"Error: {e}")
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        print("\n🛡️ Testing Error Handling...")
        
        # Test invalid image URL
        try:
            payload = {"image_url": "https://invalid-url-that-does-not-exist.com/image.jpg"}
            response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=10)
            if response.status_code == 400:
                self.log_result("Invalid URL Handling", "PASS", "Properly rejected invalid URL")
            else:
                self.log_result("Invalid URL Handling", "FAIL", f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid URL Handling", "FAIL", f"Error: {e}")
        
        # Test invalid model
        try:
            payload = {
                "image_url": TEST_IMAGE,
                "model": "invalid-model-name"
            }
            response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Invalid Model Handling", "PASS", "Gracefully fell back to default model")
                else:
                    self.log_result("Invalid Model Handling", "FAIL", "Failed to handle invalid model")
            else:
                self.log_result("Invalid Model Handling", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Model Handling", "FAIL", f"Error: {e}")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n⚡ Testing Concurrent Requests...")
        
        def make_request(request_id):
            try:
                payload = {
                    "image_url": TEST_IMAGE,
                    "model": "birefnet-general",
                    "enhance_quality": False,
                    "use_cache": True
                }
                
                start_time = time.time()
                response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=30)
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return f"Request {request_id}: Success in {processing_time:.2f}s"
                    else:
                        return f"Request {request_id}: Failed - {result.get('error')}"
                else:
                    return f"Request {request_id}: HTTP {response.status_code}"
            except Exception as e:
                return f"Request {request_id}: Error - {e}"
        
        # Make 3 concurrent requests
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            results = [future.result() for future in as_completed(futures)]
        
        success_count = sum(1 for r in results if "Success" in r)
        if success_count >= 2:  # At least 2 out of 3 should succeed
            self.log_result("Concurrent Requests", "PASS", f"{success_count}/3 requests succeeded")
        else:
            self.log_result("Concurrent Requests", "FAIL", f"Only {success_count}/3 requests succeeded")
    
    def test_performance_metrics(self):
        """Test performance under normal load"""
        print("\n📊 Testing Performance Metrics...")
        
        try:
            # Test processing time
            payload = {
                "image_url": TEST_IMAGE,
                "model": "birefnet-general",
                "enhance_quality": True,
                "use_cache": False
            }
            
            start_time = time.time()
            response = requests.post(f"{AI_BASE_URL}/remove-background", json=payload, timeout=30)
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    processing_time = result.get("processing_time", 0)
                    
                    # Performance thresholds
                    if processing_time < 5.0:  # Should complete within 5 seconds
                        self.log_result("Processing Performance", "PASS", f"Completed in {processing_time:.2f}s")
                    else:
                        self.log_result("Processing Performance", "WARN", f"Slow processing: {processing_time:.2f}s")
                    
                    if total_time < 10.0:  # Total request time should be under 10 seconds
                        self.log_result("Response Performance", "PASS", f"Total time: {total_time:.2f}s")
                    else:
                        self.log_result("Response Performance", "WARN", f"Slow response: {total_time:.2f}s")
                else:
                    self.log_result("Performance Test", "FAIL", "Processing failed")
            else:
                self.log_result("Performance Test", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Performance Test", "FAIL", f"Error: {e}")
    
    def test_system_resources(self):
        """Check system resource usage"""
        print("\n💻 Testing System Resources...")
        
        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            if memory_usage < 80:
                self.log_result("Memory Usage", "PASS", f"Memory usage: {memory_usage:.1f}%")
            else:
                self.log_result("Memory Usage", "WARN", f"High memory usage: {memory_usage:.1f}%")
            
            # Check disk space
            disk = psutil.disk_usage('.')
            disk_usage = (disk.used / disk.total) * 100
            if disk_usage < 90:
                self.log_result("Disk Usage", "PASS", f"Disk usage: {disk_usage:.1f}%")
            else:
                self.log_result("Disk Usage", "WARN", f"High disk usage: {disk_usage:.1f}%")
            
            # Check if output directories exist and are writable
            output_dir = Path("processed_images")
            cache_dir = Path("cache")
            
            if output_dir.exists() and os.access(output_dir, os.W_OK):
                self.log_result("Output Directory", "PASS", "Writable output directory")
            else:
                self.log_result("Output Directory", "FAIL", "Output directory not writable")
            
            if cache_dir.exists() and os.access(cache_dir, os.W_OK):
                self.log_result("Cache Directory", "PASS", "Writable cache directory")
            else:
                self.log_result("Cache Directory", "FAIL", "Cache directory not writable")
                
        except Exception as e:
            self.log_result("System Resources", "FAIL", f"Error: {e}")
    
    def generate_report(self):
        """Generate comprehensive production readiness report"""
        print("\n" + "="*60)
        print("🏭 PRODUCTION READINESS REPORT")
        print("="*60)
        
        # Count results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        warning_tests = sum(1 for r in self.results.values() if r["status"] == "WARN")
        
        print(f"\n📈 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Warnings: {warning_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Production readiness assessment
        if failed_tests == 0 and warning_tests <= 2:
            readiness = "🟢 PRODUCTION READY"
            recommendation = "Server is ready for production deployment"
        elif failed_tests <= 2 and warning_tests <= 3:
            readiness = "🟡 PRODUCTION READY WITH MINOR ISSUES"
            recommendation = "Fix minor issues before deployment"
        else:
            readiness = "🔴 NOT PRODUCTION READY"
            recommendation = "Fix critical issues before deployment"
        
        print(f"\n🎯 Production Readiness: {readiness}")
        print(f"💡 Recommendation: {recommendation}")
        
        # Detailed results
        print(f"\n📋 Detailed Test Results:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"   {status_icon} {test_name}: {result['details']}")
        
        # Recommendations
        print(f"\n🔧 Recommendations:")
        if failed_tests > 0:
            print("   - Fix all failed tests before deployment")
        if warning_tests > 0:
            print("   - Address warnings for optimal performance")
        print("   - Set up monitoring and alerting")
        print("   - Configure proper logging levels")
        print("   - Set up backup and recovery procedures")
        print("   - Configure rate limiting and security measures")
        
        return readiness, recommendation

def main():
    """Run production readiness check"""
    print("🚀 SparkIQ Background Removal API - Production Readiness Check")
    print("="*70)
    
    checker = ProductionReadinessChecker()
    
    # Run all tests
    checker.test_basic_connectivity()
    checker.test_health_endpoints()
    checker.test_background_removal_functionality()
    checker.test_model_variety()
    checker.test_caching_system()
    checker.test_error_handling()
    checker.test_concurrent_requests()
    checker.test_performance_metrics()
    checker.test_system_resources()
    
    # Generate report
    readiness, recommendation = checker.generate_report()
    
    print(f"\n🎉 Production Readiness Check Complete!")
    print(f"Final Status: {readiness}")
    print(f"Next Steps: {recommendation}")

if __name__ == "__main__":
    main() 