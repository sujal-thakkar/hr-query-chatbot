#!/usr/bin/env python3
"""
Simple AI client test without external dependencies
"""
import sys
import os
sys.path.append('./backend')

# Manually set environment variables for testing
os.environ['GEMINI_API_KEY'] = 'AIzaSyD2A7...'  # Your key from the earlier test

def test_ai_client_simple():
    """Test AI client with minimal dependencies"""
    
    try:
        from ai_client import get_ai_client
        print("✅ AI client module imported successfully")
        
        # Get AI client
        ai_client = get_ai_client()
        print(f"AI client created: {type(ai_client)}")
        
        if ai_client and ai_client.is_available():
            status = ai_client.get_status()
            print("AI Client Status:")
            print(f"  Primary: {status.get('primary_client')}")
            print(f"  Fallbacks: {status.get('fallback_clients')}")
            
            # Test actual generation
            print("\nTesting AI generation...")
            try:
                response = ai_client.generate_response(
                    system_prompt="You are a helpful HR assistant.",
                    user_prompt="Say hello briefly.",
                    max_tokens=20,
                    temperature=0.7
                )
                print(f"✅ AI Response: '{response}'")
                
                if response and len(response.strip()) > 0:
                    return True
                else:
                    print("❌ Empty response received")
                    return False
                
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
                return False
        else:
            print("❌ AI client not available")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test AI client: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI client...")
    success = test_ai_client_simple()
    
    if success:
        print("\n✅ AI client is working locally!")
    else:
        print("\n❌ AI client has issues")
