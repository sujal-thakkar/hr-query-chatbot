# backend/main.py
import os, json, uvicorn, time
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from pathlib import Path
from dotenv import load_dotenv
from config import CHAT_RATE_LIMIT, HEALTH_RATE_LIMIT, ROOT_RATE_LIMIT, RAG_STATUS_RATE_LIMIT, SEARCH_RATE_LIMIT, DEBUG_EMPLOYEES_RATE_LIMIT, MIN_TOP_K, MAX_TOP_K, ALLOWED_ORIGINS
from logging_config import setup_logging

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Initialize logging early
setup_logging()

# Soft-check for environment variables (don't crash if missing)
if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ GEMINI_API_KEY not set. AI features may be limited; the app will run in degraded mode.")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Import AI client manager
from ai_client import get_ai_client

# Initialize AI client manager safely
try:
    ai_client = get_ai_client()
except Exception as e:
    print(f"⚠️ Failed to initialize AI client manager: {e}")
    ai_client = None

# Print AI client status
if ai_client and ai_client.is_available():
    status = ai_client.get_status()
    print(f"✅ AI client initialized: {status['primary_client']}")
    if status['fallback_clients']:
        print(f"🔄 Fallback clients: {', '.join(status['fallback_clients'])}")
else:
    print("⚠️ No AI clients available. Some features may be limited.")

DATA_PATH = Path("/app/dataset/employees.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)["employees"]

# Initialize RAG system
from rag import EmployeeRAG
try:
    rag_system = EmployeeRAG(DATA)
    if rag_system.is_active():
        stats = rag_system.get_embedding_stats()
        print(f"✅ RAG system initialized successfully with {stats.get('embedding_model')}")
        print(f"📊 Embedding dimension: {stats.get('dimension')}")
    else:
        print("⚠️ RAG system failed to initialize. Using keyword search only.")
except Exception as e:
    print(f"❌ RAG system initialization error: {e}")
    rag_system = None

app = FastAPI(title="HR Resource Query Chatbot")

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

@app.get("/health")
@limiter.limit(HEALTH_RATE_LIMIT)
async def health_check(request: Request, detailed: bool = False):
    """Health check endpoint with optional detailed information"""
    if detailed:
        # Detailed health check
        try:
            # Test RAG system
            rag_status = "available" if rag_system else "unavailable"
            if rag_system:
                try:
                    # Quick test search (use enhanced_search, not semantic_search)
                    test_results = rag_system.enhanced_search("test", 1)
                    rag_status = "operational"
                except Exception as e:
                    rag_status = f"error: {str(e)[:100]}"
            
            # Test AI client
            ai_status = "not_available"
            if ai_client and ai_client.is_available():
                try:
                    ai_status = ai_client.get_status()
                    ai_status['status'] = "ready"
                except Exception as e:
                    ai_status = f"error: {str(e)[:100]}"
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "employees_count": len(DATA),
                "rag_system": rag_status,
                "ai_client": ai_status,
                "cache_size": rag_system.get_cache_size() if rag_system else 0,
                "version": "2.1",
                "features": ["enhanced_search", "query_processing", "retry_mechanisms", "multi_ai_support"]
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": time.time()
            }
    else:
        # Simple health check
        return {"status": "healthy", "service": "HR Query Chatbot API"}

@app.get("/debug/employees")
@limiter.limit(DEBUG_EMPLOYEES_RATE_LIMIT) 
async def debug_employees(request: Request):
    """Debug endpoint to see all employees"""
    return {"total_employees": len(DATA), "employees": DATA[:3]}  # Return first 3 for testing

@app.get("/")
@limiter.limit(ROOT_RATE_LIMIT)
async def root_health_check(request: Request):
    return {"status": "healthy", "message": "HR Resource Query Chatbot API is running"}

@app.get("/system/rag-status")
@limiter.limit(RAG_STATUS_RATE_LIMIT)
async def get_rag_status(request: Request):
    """Get detailed RAG system status and embedding information"""
    try:
        if not rag_system or not rag_system.is_active():
            return {
                "status": "unavailable",
                "message": "RAG system not initialized or inactive",
                "fallback": "keyword search only"
            }
        
        # Get RAG status and embedding statistics
        try:
            status = rag_system.get_embedding_stats()
            status["status"] = "available"
            status["cache_size"] = rag_system.get_cache_size()
        except Exception as e:
            return {"status": "error", "message": f"Could not retrieve RAG stats: {e}"}
        
        # Test search functionality
        try:
            # Use a simple, common query for testing
            test_results = rag_system.enhanced_search("python developer", 1)
            status["search_test"] = "passed"
            if test_results:
                status["test_similarity"] = test_results[0].relevance_score
            else:
                status["test_similarity"] = "no_results"
        except Exception as e:
            status["search_test"] = f"failed: {str(e)[:100]}"
        
        return status
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }
class SearchParams(BaseModel):
    skill: str = None
    min_experience: int = 0
    availability: str = None
    q: str = None

class ChatQuery(BaseModel):
    query: str
    top_k: int = 5
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Query must be at least 3 characters")
        if len(v) > 500:
            raise ValueError("Query too long (maximum 500 characters)")
        # Basic XSS prevention
        forbidden_chars = ['<', '>', 'script', 'javascript:', 'data:']
        v_lower = v.lower()
        if any(char in v_lower for char in forbidden_chars):
            raise ValueError("Query contains forbidden characters")
        return v.strip()
    
    @field_validator('top_k')
    @classmethod
    def validate_top_k(cls, v):
        if v < MIN_TOP_K:
            raise ValueError(f"top_k must be at least {MIN_TOP_K}")
        if v > MAX_TOP_K:
            raise ValueError(f"top_k cannot exceed {MAX_TOP_K}")
        return v

# Simple keyword search endpoint
@app.get("/employees/search")
@limiter.limit(SEARCH_RATE_LIMIT)
async def search_employees(request: Request, skill: str = None, min_experience: int = 0, availability: str = None, q: str = None):
    results = DATA
    if skill:
        skill_l = skill.lower()
        results = [e for e in results if any(skill_l == s.lower() or skill_l in s.lower() for s in e["skills"])]
    if min_experience:
        results = [e for e in results if e["experience_years"] >= min_experience]
    if availability:
        results = [e for e in results if e["availability"].lower() == availability.lower()]
    if q:
        ql = q.lower()
        results = [e for e in results if ql in e["name"].lower() or ql in " ".join(e["skills"]).lower() or ql in " ".join(e["projects"]).lower()]
    return {"count": len(results), "results": results}

from response_generator import ResponseGenerator

# Initialize response generator
response_generator = ResponseGenerator(ai_client)

@app.post("/chat")
@limiter.limit(CHAT_RATE_LIMIT)
async def chat(request: Request, query: ChatQuery):
    try:
        print(f"🔍 Received query: '{query.query}'")
        
        if not rag_system.is_active():
            print("🔄 RAG system inactive, using keyword fallback.")
            # This can be enhanced to use a simpler keyword search if needed
            return {"candidates": [], "message": "The search system is currently offline. Please try again later."}

        print("🚀 Using enhanced RAG system...")
        search_results = rag_system.enhanced_search(query.query, query.top_k)
        print(f"📈 Found {len(search_results)} candidates")

        # Generate the final response using the dedicated generator
        response = response_generator.generate_response(query.query, search_results)
        return response

    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        # Provide a generic error response
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
