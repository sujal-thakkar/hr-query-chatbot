#!/usr/bin/env python3
"""
Test script to verify Gemini API key functionality
"""
import os
import sys

# Add backend to path
sys.path.append('./backend')

def test_gemini_api():
    """Test Gemini API key and client initialization"""
    
    # Check environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"GEMINI_API_KEY found: {'Yes' if gemini_key else 'No'}")
    if gemini_key:
        print(f"Key starts with: {gemini_key[:10]}...")
    
    # Test import
    try:
        from google import genai
        print("✅ Google GenAI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google GenAI: {e}")
        return False
    
    # Test client initialization
    if not gemini_key:
        print("❌ No API key found")
        return False
    
    try:
        client = genai.Client(api_key=gemini_key)
        print("✅ Gemini client created successfully")
        
        # Test simple request
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Say hello",
            config=genai.types.GenerateContentConfig(
                max_output_tokens=10,
                temperature=0.1
            )
        )
        
        # Handle response properly
        response_text = None
        if hasattr(response, 'text') and response.text:
            response_text = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            if response.candidates[0].content and response.candidates[0].content.parts:
                response_text = response.candidates[0].content.parts[0].text
        
        print(f"✅ Test response: {response_text}")
        print(f"Raw response type: {type(response)}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('./backend/.env')
    
    print("Testing Gemini API configuration...")
    success = test_gemini_api()
    
    if success:
        print("\n✅ Gemini API is working correctly!")
    else:
        print("\n❌ Gemini API test failed. Check your API key and configuration.")
