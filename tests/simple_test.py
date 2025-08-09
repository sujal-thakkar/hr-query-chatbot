#!/usr/bin/env python3
"""
Simple test for Gemini text generation
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_simple_generation():
    """Test simple text generation"""
    try:
        from ai_client import GeminiClient
        
        client = GeminiClient()
        
        if not client.is_available():
            print("❌ Gemini client not available")
            return False
        
        print(f"✅ Client available with model: {client.current_model}")
        
        # Simple test
        response = client.generate_response(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello World' and nothing else.",
            max_tokens=10
        )
        
        print(f"✅ Response: '{response}'")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Gemini Text Generation Test")
    print("=" * 40)
    success = test_simple_generation()
    sys.exit(0 if success else 1)
