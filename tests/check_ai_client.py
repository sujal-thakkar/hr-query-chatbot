#!/usr/bin/env python3
"""
Check if AI client is working properly
"""
import os, sys
sys.path.append('../backend')

from dotenv import load_dotenv
load_dotenv('../.env')

print('Environment check:')
print(f'GEMINI_API_KEY set: {bool(os.getenv("GEMINI_API_KEY"))}')
print(f'OPENAI_API_KEY set: {bool(os.getenv("OPENAI_API_KEY"))}')

# Check AI client initialization
try:
    from ai_client import get_ai_client
    ai_client = get_ai_client()
    print(f'AI client available: {ai_client.is_available()}')
    if ai_client.is_available():
        status = ai_client.get_status()
        print(f'Status: {status}')
        
        # Try to generate a simple response
        try:
            response = ai_client.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say hello briefly.",
                max_tokens=50,
                temperature=0.5
            )
            print(f'Test response: {response}')
        except Exception as e:
            print(f'Generation error: {e}')
    else:
        print('AI client not available')
except Exception as e:
    print(f'AI client error: {e}')
