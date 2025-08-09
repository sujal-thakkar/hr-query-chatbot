#!/usr/bin/env python3
"""
Simple test with minimal prompt to see if Gemini works at all
"""
import sys
import os
sys.path.append('../backend')

from dotenv import load_dotenv
load_dotenv('../.env')

from ai_client import get_ai_client

def test_simple_ai():
    try:
        ai_client = get_ai_client()
        
        if ai_client.is_available():
            print(f"Using AI client: {ai_client.__class__.__name__}")
            
            # Try with very simple prompt and higher tokens
            try:
                response = ai_client.generate_response(
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Write one sentence about why someone with Python and ML skills would be good for a healthcare project.",
                    max_tokens=200,  # Lower token count
                    temperature=0.5
                )
                print(f"✅ Simple AI Response: {response}")
                
            except Exception as ai_error:
                print(f"❌ Simple AI test failed: {ai_error}")
                
                # Try even simpler
                try:
                    response = ai_client.generate_response(
                        system_prompt="Be helpful.",
                        user_prompt="Say hello.",
                        max_tokens=50,
                        temperature=0.3
                    )
                    print(f"✅ Ultra-simple response: {response}")
                except Exception as ultra_error:
                    print(f"❌ Even ultra-simple failed: {ultra_error}")
        else:
            print("AI client not available")
            
    except Exception as e:
        print(f"Setup error: {e}")

if __name__ == "__main__":
    test_simple_ai()
