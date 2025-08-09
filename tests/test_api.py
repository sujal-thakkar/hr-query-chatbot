#!/usr/bin/env python3
"""
Test the API directly to see what's happening
"""
import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {health_resp.status_code} - {health_resp.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test chat endpoint
    query = {
        "query": "I need someone experienced with machine learning for a healthcare project",
        "top_k": 5
    }
    
    try:
        resp = requests.post(f"{base_url}/chat", json=query, timeout=30)
        print(f"Chat API Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {resp.text}")
            
    except Exception as e:
        print(f"Chat API failed: {e}")

if __name__ == "__main__":
    test_api()
