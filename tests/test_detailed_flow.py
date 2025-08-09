#!/usr/bin/env python3
"""
Test the exact flow to see what's happening with AI generation
"""
import requests
import json

def test_detailed_api():
    base_url = "http://127.0.0.1:8000"
    
    # Test with detailed health check first
    try:
        health_resp = requests.get(f"{base_url}/health?detailed=true", timeout=5)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            print("=== DETAILED HEALTH CHECK ===")
            print(json.dumps(health_data, indent=2))
            print()
        else:
            print(f"Health check failed: {health_resp.status_code}")
            return
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test RAG system status  
    try:
        rag_resp = requests.get(f"{base_url}/system/rag-status", timeout=5)
        if rag_resp.status_code == 200:
            rag_data = rag_resp.json()
            print("=== RAG SYSTEM STATUS ===")
            print(json.dumps(rag_data, indent=2))
            print()
        else:
            print(f"RAG status check failed: {rag_resp.status_code}")
    except Exception as e:
        print(f"RAG status check failed: {e}")
    
    # Test chat endpoint
    query = {
        "query": "I need someone experienced with machine learning for a healthcare project",
        "top_k": 3
    }
    
    try:
        resp = requests.post(f"{base_url}/chat", json=query, timeout=30)
        print("=== CHAT API RESPONSE ===")
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Print just the message first to see AI response
            print("\n=== AI MESSAGE ===")
            print(data.get('message', 'No message'))
            
            # Then print candidate details
            print(f"\n=== CANDIDATES ({len(data.get('candidates', []))}) ===")
            for i, candidate in enumerate(data.get('candidates', [])[:2]):  # Just first 2
                print(f"\nCandidate {i+1}:")
                print(f"  Name: {candidate.get('name')}")
                print(f"  Skills: {candidate.get('skills')}")
                print(f"  Experience: {candidate.get('experience_years')} years")
                print(f"  Match Score: {candidate.get('final_score', 'N/A')}")
                print(f"  Confidence: {candidate.get('confidence', 'N/A')}%")
                if 'match_reasons' in candidate:
                    print(f"  Reasons: {candidate['match_reasons']}")
        else:
            print(f"Error: {resp.text}")
            
    except Exception as e:
        print(f"Chat API failed: {e}")

if __name__ == "__main__":
    test_detailed_api()
