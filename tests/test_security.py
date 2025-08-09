#!/usr/bin/env python3
"""
Security Test Script for HR Query Chatbot
Tests the implemented security features
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_rate_limiting():
    """Test rate limiting on /chat endpoint (5 requests per minute)"""
    print("🔒 Testing Rate Limiting...")
    
    test_query = {"query": "python developer", "top_k": 3}
    
    # Make 6 requests quickly to trigger rate limit
    for i in range(6):
        try:
            response = requests.post(f"{BASE_URL}/chat", json=test_query)
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("✅ Rate limiting working - request blocked!")
                return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("⚠️ Rate limiting may not be triggered or limit is higher")
    return False

def test_input_validation():
    """Test input validation on query field"""
    print("\n🛡️ Testing Input Validation...")
    
    test_cases = [
        # Valid cases
        {"query": "python developer", "top_k": 3, "should_pass": True},
        {"query": "machine learning engineer with 5 years experience", "top_k": 5, "should_pass": True},
        
        # Invalid cases
        {"query": "ab", "top_k": 3, "should_pass": False, "reason": "Too short"},
        {"query": "a" * 501, "top_k": 3, "should_pass": False, "reason": "Too long"},
        {"query": "<script>alert('xss')</script>", "top_k": 3, "should_pass": False, "reason": "XSS attempt"},
        {"query": "javascript:alert(1)", "top_k": 3, "should_pass": False, "reason": "XSS attempt"},
        {"query": "python developer", "top_k": 0, "should_pass": False, "reason": "Invalid top_k"},
        {"query": "python developer", "top_k": 25, "should_pass": False, "reason": "top_k too high"},
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases):
        try:
            test_data = {k: v for k, v in case.items() if k not in ['should_pass', 'reason']}
            response = requests.post(f"{BASE_URL}/chat", json=test_data)
            
            if case["should_pass"]:
                if response.status_code == 200:
                    print(f"✅ Test {i+1}: Valid input accepted")
                    passed += 1
                else:
                    print(f"❌ Test {i+1}: Valid input rejected - {response.status_code}")
            else:
                if response.status_code == 422:  # Validation error
                    print(f"✅ Test {i+1}: Invalid input rejected ({case.get('reason', 'Unknown')})")
                    passed += 1
                else:
                    print(f"❌ Test {i+1}: Invalid input accepted - {response.status_code} ({case.get('reason', 'Unknown')})")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Test {i+1}: Request failed - {e}")
    
    print(f"\n📊 Validation Tests: {passed}/{total} passed")
    return passed == total

def test_cors_headers():
    """Test CORS configuration"""
    print("\n🌐 Testing CORS Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        # Check if CORS headers are present
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-credentials': response.headers.get('access-control-allow-credentials'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
        }
        
        print("CORS Headers:")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
        
        # Check if origin is restricted (not *)
        if cors_headers['access-control-allow-origin'] != '*':
            print("✅ CORS origin is restricted (not allowing all origins)")
            return True
        else:
            print("⚠️ CORS allows all origins - consider restricting in production")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🏥 Testing Health Endpoints...")
    
    endpoints = ["/", "/health", "/system/rag-status"]
    passed = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                passed += 1
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Request failed - {e}")
    
    return passed == len(endpoints)

def main():
    print("🔐 HR Query Chatbot Security Test Suite")
    print("=" * 50)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            return
        print("✅ Server is running")
        
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not accessible")
        print("Please start the server with: python main.py")
        return
    
    # Run security tests
    tests_results = []
    tests_results.append(("Rate Limiting", test_rate_limiting()))
    tests_results.append(("Input Validation", test_input_validation()))
    tests_results.append(("CORS Configuration", test_cors_headers()))
    tests_results.append(("Health Endpoints", test_health_endpoints()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Security Test Results:")
    passed_tests = 0
    for test_name, result in tests_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall: {passed_tests}/{len(tests_results)} tests passed")
    
    if passed_tests == len(tests_results):
        print("🎉 All security tests passed!")
    else:
        print("⚠️ Some security tests failed - review implementation")

if __name__ == "__main__":
    main()
