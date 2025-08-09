#!/usr/bin/env python3
"""
Test direct Gemini API usage without our wrapper
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_direct_api():
    """Test direct API usage"""
    try:
        from google import genai
        from google.genai import types
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No API key found")
            return False
        
        client = genai.Client(api_key=api_key)
        
        print("🔍 Testing direct API call...")
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents="Say hello briefly",
            config=types.GenerateContentConfig(
                max_output_tokens=20,
                temperature=0.1
            )
        )
        
        print(f"✅ Direct API response: {response.text}")
        print(f"📋 Response candidates: {len(response.candidates) if response.candidates else 0}")
        
        if response.candidates:
            candidate = response.candidates[0]
            print(f"📋 Finish reason: {getattr(candidate, 'finish_reason', 'N/A')}")
            print(f"📋 Content parts: {getattr(candidate.content, 'parts', 'N/A') if candidate.content else 'NO_CONTENT'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Direct Gemini API Test")
    print("=" * 30)
    test_direct_api()
