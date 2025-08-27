#!/usr/bin/env python3
"""
Detailed AI client test to debug the issue
"""
import sys
import os
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv('./backend/.env')

def test_ai_client_detailed():
    """Test AI client with detailed error reporting"""
    
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
            print(f"  Available: {status.get('available_clients')}")
            
            # Test actual generation
            print("\nTesting AI generation...")
            try:
                response = ai_client.generate_response(
                    system_prompt="You are a helpful HR assistant.",
                    user_prompt="Say hello and confirm you're working.",
                    max_tokens=50,
                    temperature=0.7
                )
                print(f"✅ AI Response: {response}")
                return True
                
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
                print(f"Error type: {type(e)}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ AI client not available")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test AI client: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing AI client in detail...")
    success = test_ai_detailed()
    
    if success:
        print("\n✅ AI client is working!")
    else:
        print("\n❌ AI client has issues - check errors above")
