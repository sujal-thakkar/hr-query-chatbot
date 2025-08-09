#!/usr/bin/env python3
"""
Test script for the updated Gemini RAG implementation
"""
import os
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_gemini_client():
    """Test the updated Gemini client"""
    print("🧪 Testing Gemini Client...")
    
    try:
        from ai_client import GeminiClient
        
        # Test client initialization
        client = GeminiClient()
        
        if not client.is_available():
            print("❌ Gemini client not available - check API key")
            return False
        
        print(f"✅ Gemini client initialized with model: {client.current_model}")
        
        # Test text generation
        try:
            # Test without max_tokens first to see if basic generation works
            response = client.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say hello in one sentence"
            )
            print(f"✅ Text generation works: {response[:100]}...")
        except Exception as e:
            print(f"❌ Text generation failed: {e}")
            # Try with explicit max_tokens as fallback
            try:
                response = client.generate_response(
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Say hello",
                    max_tokens=500
                )
                print(f"✅ Text generation works (with max_tokens): {response[:100]}...")
            except Exception as e2:
                print(f"❌ Text generation with max_tokens also failed: {e2}")
                return False
        
        # Test embeddings
        try:
            embedding = client.get_embedding(
                text="This is a test document about software development",
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
            print(f"✅ Embedding generation works - dimension: {len(embedding)}")
            
            # Test batch embeddings
            batch_embeddings = client.get_batch_embeddings(
                texts=["First document", "Second document"],
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
            print(f"✅ Batch embeddings work - {len(batch_embeddings)} embeddings generated")
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini client test failed: {e}")
        return False

def test_gemini_rag():
    """Test the Gemini RAG system"""
    print("\n🧪 Testing Gemini RAG System...")
    
    try:
        # Load test data
        data_path = Path(__file__).parent.parent / "dataset" / "employees.json"
        with open(data_path) as f:
            employees_data = json.load(f)["employees"]
        
        from gemini_rag import GeminiEmployeeRAG
        
        # Initialize Gemini RAG
        print("📚 Initializing Gemini RAG system...")
        rag = GeminiEmployeeRAG(employees_data)
        print("✅ Gemini RAG system initialized")
        
        # Get embedding stats
        stats = rag.get_embedding_stats()
        print(f"📊 Embedding stats: {stats}")
        
        # Test semantic search
        print("\n🔍 Testing semantic search...")
        results = rag.semantic_search("python developer with machine learning experience", top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - Score: {result['similarity_score']:.4f}")
            print(f"   Skills: {', '.join(result['skills'][:3])}...")
        
        # Test enhanced search
        print("\n🚀 Testing enhanced search...")
        enhanced_results = rag.enhanced_search("senior python developer with healthcare experience", top_k=3)
        
        for i, result in enumerate(enhanced_results, 1):
            print(f"{i}. {result.employee['name']} - Score: {result.relevance_score:.4f} - Confidence: {result.confidence:.1f}%")
            print(f"   Match reasons: {', '.join(result.match_reasons[:2])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini RAG test failed: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        import requests
        import time
        
        # Start a test session (assumes the server is running)
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint works")
                health_data = response.json()
                print(f"   RAG system: {health_data.get('rag_system', 'N/A')}")
                print(f"   AI client: {health_data.get('ai_client', {}).get('status', 'N/A')}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ API server not running - start with 'python backend/main.py'")
            return False
        
        # Test RAG status endpoint
        try:
            response = requests.get(f"{base_url}/system/rag-status", timeout=5)
            if response.status_code == 200:
                print("✅ RAG status endpoint works")
                rag_data = response.json()
                print(f"   Type: {rag_data.get('type', 'N/A')}")
                print(f"   Embedding model: {rag_data.get('embedding_model', 'N/A')}")
                print(f"   Search test: {rag_data.get('search_test', 'N/A')}")
            else:
                print(f"❌ RAG status endpoint failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ RAG status endpoint error: {e}")
            return False
        
        # Test chat endpoint
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"query": "Find me a Python developer with machine learning experience", "top_k": 3},
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Chat endpoint works")
                chat_data = response.json()
                print(f"   Found {len(chat_data.get('candidates', []))} candidates")
                if chat_data.get('response'):
                    print(f"   AI response generated: {len(chat_data['response'])} characters")
            else:
                print(f"❌ Chat endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Chat endpoint error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Updated Gemini Implementation")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("❌ No Gemini API key found in environment")
        print("   Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        return False
    
    tests = [
        ("Gemini Client", test_gemini_client),
        ("Gemini RAG", test_gemini_rag),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Gemini implementation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
