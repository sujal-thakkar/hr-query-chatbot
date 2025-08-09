#!/usr/bin/env python3
"""
Quick debug script to test Gemini response structure
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def debug_gemini_response():
    """Debug the Gemini response structure"""
    print("🔍 Debugging Gemini Response Structure...")
    
    try:
        from ai_client import GeminiClient
        
        client = GeminiClient()
        if not client.is_available():
            print("❌ Gemini client not available")
            return
        
        print(f"✅ Using model: {client.current_model}")
        
        # Make a simple request
        try:
            response = client.client.models.generate_content(
                model=client.current_model,
                contents="Say hello in one sentence."
            )
            
            print(f"📋 Response type: {type(response)}")
            print(f"📋 Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            
            if hasattr(response, 'text'):
                print(f"📋 response.text: {response.text}")
            
            if hasattr(response, 'candidates'):
                print(f"📋 response.candidates: {len(response.candidates) if response.candidates else 'None'}")
                if response.candidates:
                    candidate = response.candidates[0]
                    print(f"📋 candidate type: {type(candidate)}")
                    print(f"📋 candidate attributes: {[attr for attr in dir(candidate) if not attr.startswith('_')]}")
                    
                    if hasattr(candidate, 'content'):
                        print(f"📋 candidate.content: {candidate.content}")
                        if candidate.content and hasattr(candidate.content, 'parts'):
                            print(f"📋 content.parts: {len(candidate.content.parts) if candidate.content.parts else 'None'}")
                            if candidate.content.parts:
                                part = candidate.content.parts[0]
                                print(f"📋 part type: {type(part)}")
                                print(f"📋 part attributes: {[attr for attr in dir(part) if not attr.startswith('_')]}")
                                if hasattr(part, 'text'):
                                    print(f"📋 part.text: {part.text}")
            
            # Try using our client method
            print("\n🔧 Testing client generate_response method...")
            result = client.generate_response("You are helpful", "Say hello", max_tokens=20)
            print(f"✅ Client method result: {result}")
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gemini_response()
