#!/usr/bin/env python3
"""
Verify deployment functionality
"""
import requests
import json

def test_backend_health(backend_url):
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{backend_url}/health?detailed=true", timeout=10)
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Health check response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_chat_endpoint(backend_url):
    """Test chat endpoint"""
    try:
        payload = {
            "query": "Find Python developers",
            "top_k": 2
        }
        
        response = requests.post(
            f"{backend_url}/chat", 
            json=payload,
            timeout=30
        )
        
        print(f"Chat endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Chat response preview:")
            print(f"Response length: {len(data.get('response', ''))}")
            print(f"Candidates found: {len(data.get('candidates', []))}")
            
            # Check if it's using AI or fallback
            response_text = data.get('response', '')
            if 'cannot provide detailed AI analysis' in response_text:
                print("⚠️ Using fallback mode - AI not working")
                return False
            else:
                print("✅ AI analysis working")
                return True
        else:
            print(f"Chat endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return False

def test_head_method(backend_url):
    """Test HEAD method for UptimeRobot"""
    try:
        response = requests.head(f"{backend_url}/", timeout=10)
        print(f"HEAD method status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"HEAD method error: {e}")
        return False

if __name__ == "__main__":
    # Test your deployed backend
    BACKEND_URL = "https://backend-aohf.onrender.com"
    
    print(f"Testing deployment at: {BACKEND_URL}")
    print("=" * 50)
    
    # Test HEAD method first
    print("1. Testing HEAD method (UptimeRobot compatibility):")
    head_ok = test_head_method(BACKEND_URL)
    print()
    
    # Test health endpoint
    print("2. Testing health endpoint:")
    health_ok = test_backend_health(BACKEND_URL)
    print()
    
    # Test chat functionality
    print("3. Testing chat endpoint:")
    chat_ok = test_chat_endpoint(BACKEND_URL)
    print()
    
    # Summary
    print("=" * 50)
    print("SUMMARY:")
    print(f"HEAD method: {'✅' if head_ok else '❌'}")
    print(f"Health check: {'✅' if health_ok else '❌'}")
    print(f"AI functionality: {'✅' if chat_ok else '❌'}")
    
    if all([head_ok, health_ok, chat_ok]):
        print("\n🎉 All tests passed! Deployment is working correctly.")
    else:
        print("\n⚠️ Some issues detected. Check the logs above.")
