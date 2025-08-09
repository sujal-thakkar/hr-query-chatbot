# backend/main.py
import os, json, uvicorn, time
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from pathlib import Path
from dotenv import load_dotenv

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = ["GEMINI_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Required environment variables not set: {', '.join(missing_vars)}")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Import AI client manager
from ai_client import get_ai_client

# Initialize AI client manager
ai_client = get_ai_client()

# Print AI client status
if ai_client.is_available():
    status = ai_client.get_status()
    print(f"✅ AI client initialized: {status['primary_client']}")
    if status['fallback_clients']:
        print(f"🔄 Fallback clients: {', '.join(status['fallback_clients'])}")
else:
    print("⚠️ No AI clients available. Some features may be limited.")

DATA_PATH = Path(__file__).parent.parent / "dataset" / "employees.json"
with open(DATA_PATH) as f:
    DATA = json.load(f)["employees"]

# Initialize RAG system with Gemini embeddings (preferred) or fallback
rag_system = None
gemini_rag_system = None

# Try to initialize Gemini RAG first
try:
    from gemini_rag import GeminiEmployeeRAG
    gemini_rag_system = GeminiEmployeeRAG(DATA)
    rag_system = gemini_rag_system  # Use Gemini RAG as primary
    print("✅ Gemini RAG system initialized successfully with native embeddings")
    
    # Print embedding stats
    stats = gemini_rag_system.get_embedding_stats()
    print(f"📊 Embedding model: {stats.get('embedding_model', 'N/A')}")
    print(f"📐 Dimension: {stats.get('dimension', 'N/A')}")
    print(f"👥 Employees indexed: {stats.get('total_employees', 'N/A')}")
    
except Exception as e:
    print(f"⚠️ Gemini RAG system failed to initialize: {e}")
    print("Falling back to Sentence Transformers RAG...")
    
    # Fallback to original RAG system
    try:
        from rag import EmployeeRAG
        rag_system = EmployeeRAG(DATA)
        print("✅ Fallback RAG system initialized with Sentence Transformers")
    except ImportError as e:
        print(f"⚠️ Fallback RAG system not available: {e}")
        print("Install sentence-transformers for enhanced search")
    except Exception as e:
        print(f"⚠️ All RAG systems failed to initialize: {e}")
        print("Falling back to keyword search only")

app = FastAPI(title="HR Resource Query Chatbot")

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "https://hr-chatbot-frontend.onrender.com",  # Your exact frontend URL
        "https://*.onrender.com"  # Backup for all Render domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["*"],
)

@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request, detailed: bool = False):
    """Health check endpoint with optional detailed information"""
    if detailed:
        # Detailed health check
        try:
            # Test RAG system
            rag_status = "available" if rag_system else "unavailable"
            if rag_system:
                try:
                    # Quick test search
                    test_results = rag_system.semantic_search("test", 1)
                    rag_status = "operational"
                except Exception as e:
                    rag_status = f"error: {str(e)[:100]}"
            
            # Test AI client
            ai_status = "not_available"
            if ai_client.is_available():
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
                "cache_size": len(getattr(rag_system, '_query_cache', {})) if rag_system else 0,
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
@limiter.limit("5/minute") 
async def debug_employees(request: Request):
    """Debug endpoint to see all employees"""
    return {"total_employees": len(DATA), "employees": DATA[:3]}  # Return first 3 for testing

@app.get("/")
@limiter.limit("30/minute")
async def root_health_check(request: Request):
    return {"status": "healthy", "message": "HR Resource Query Chatbot API is running"}

@app.get("/system/rag-status")
@limiter.limit("10/minute")
async def get_rag_status(request: Request):
    """Get detailed RAG system status and embedding information"""
    try:
        if not rag_system:
            return {
                "status": "unavailable",
                "message": "RAG system not initialized",
                "fallback": "keyword search only"
            }
        
        # Get basic RAG status
        status = {
            "status": "available",
            "type": "Gemini RAG" if gemini_rag_system else "Sentence Transformers RAG",
            "employees_indexed": len(DATA),
            "cache_size": len(getattr(rag_system, '_query_cache', {}))
        }
        
        # Get embedding statistics if using Gemini RAG
        if gemini_rag_system:
            try:
                embedding_stats = gemini_rag_system.get_embedding_stats()
                status.update({
                    "embedding_model": embedding_stats.get("embedding_model"),
                    "embedding_dimension": embedding_stats.get("dimension"),
                    "task_type": embedding_stats.get("task_type"),
                    "normalization": embedding_stats.get("normalization"),
                    "embedding_shape": embedding_stats.get("embedding_shape")
                })
            except Exception as e:
                status["embedding_error"] = str(e)
        
        # Test search functionality
        try:
            test_results = rag_system.semantic_search("python developer", 1)
            status["search_test"] = "passed"
            status["test_similarity"] = test_results[0].get('similarity_score', 'N/A') if test_results else "no_results"
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
        if v < 1:
            raise ValueError("top_k must be at least 1")
        if v > 20:
            raise ValueError("top_k cannot exceed 20")
        return v

# Simple keyword search endpoint
@app.get("/employees/search")
@limiter.limit("10/minute")
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

def _get_enhanced_fallback_message(top_candidates, query_text):
    """Generate an enhanced fallback message when AI generation fails"""
    if not top_candidates:
        return "No matching candidates found for your query. Please try different search terms."
    
    candidate_count = len(top_candidates)
    top_skills = list(set([skill for candidate in top_candidates for skill in candidate['skills']]))[:5]
    return f"""I found {candidate_count} excellent candidate{'s' if candidate_count != 1 else ''} for your requirements.
                
These candidates collectively bring expertise in {', '.join(top_skills)} and have proven experience in relevant projects. Each has been carefully matched based on your specific needs.

The top candidate, {top_candidates[0]['name']}, has {top_candidates[0]['experience_years']} years of experience and shows strong alignment with your requirements.

Would you like me to provide more details about their specific project experience or help arrange initial conversations?"""

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: Request, query: ChatQuery):
    try:
        print(f"🔍 Received query: '{query.query}'")
        print(f"📊 Enhanced RAG system available: {rag_system is not None}")
        
        # Use the enhanced RAG system if available
        if rag_system:
            print("🚀 Using enhanced RAG system...")
            
            # Try the new enhanced search first
            try:
                search_results = rag_system.enhanced_search(query.query, query.top_k)
                print(f"📈 Enhanced search found {len(search_results)} candidates")
                
                # Convert SearchResult objects to candidate dictionaries
                top_candidates = []
                for result in search_results:
                    candidate = result.employee.copy()
                    candidate['final_score'] = result.relevance_score
                    candidate['match_reasons'] = result.match_reasons
                    candidate['confidence'] = result.confidence
                    top_candidates.append(candidate)
                    
            except Exception as e:
                print(f"⚠️ Enhanced search failed: {e}, falling back to hybrid search")
                top_candidates = rag_system.hybrid_search(query.query, query.top_k)
                print(f"📈 Hybrid search found {len(top_candidates)} candidates")
        else:
            print("🔄 Using fallback search...")
            return chat_fallback(query)
        
        # Generate response using AI client if available
        if ai_client.is_available() and top_candidates:
            system = """You are an expert HR consultant with deep knowledge of candidate assessment. 
            Your responses should be:
            - Conversational and engaging
            - Specific about why each candidate fits the role
            - Highlight unique strengths and relevant experience
            - Professional yet personable
            - Include specific project examples when relevant
            - End with a helpful next step or question

            Format your response as a cohesive narrative, not bullet points."""
            
            # Create rich context with detailed candidate information
            context_parts = []
            for i, candidate in enumerate(top_candidates):
                # Basic information
                name = candidate['name']
                years = candidate['experience_years']
                score = candidate.get('final_score', 0)
                availability = candidate['availability']
                
                # Skills breakdown
                skills = candidate['skills']
                projects = candidate['projects']
                
                # Enhanced candidate description
                candidate_desc = f"""Candidate {i+1}: {name}
Experience: {years} years | Match Score: {score:.2f} | Status: {availability}
Technical Skills: {', '.join(skills)}
Key Projects: {', '.join(projects)}"""
                
                # Add match reasons with more detail
                if 'match_reasons' in candidate and candidate['match_reasons']:
                    reasons = candidate['match_reasons']
                    candidate_desc += f"\nWhy they're a great fit: {' • '.join(reasons)}"
                
                # Add confidence score context
                if 'confidence' in candidate:
                    confidence = candidate['confidence']
                    candidate_desc += f"\nConfidence Level: {confidence:.0f}%"
                
                context_parts.append(candidate_desc)
            
            context = "\n\n".join(context_parts)
            
            # Create an enhanced prompt for more descriptive responses
            prompt = f"""User Query: "{query.query}"

Candidate Information:
{context}

Please provide a comprehensive response that:
1. Starts with a brief acknowledgment of their requirements
2. Introduces each candidate with specific details about why they're suitable
3. Highlights unique strengths and relevant project experience  
4. Mentions their availability and practical next steps
5. Ends with an engaging question or suggestion

Make it sound like a knowledgeable recruiter who has personally reviewed these profiles."""
            
            try:
                ai_message = ai_client.generate_response(
                    system_prompt=system,
                    user_prompt=prompt,
                    max_tokens=1000,  # Increased for Gemini 2.5 models
                    temperature=0.7
                )
            except Exception as e:
                print(f"AI API error: {e}")
                # Check if it's a MAX_TOKENS issue and suggest a retry
                if "MAX_TOKENS" in str(e):
                    print("⚠️ Response was truncated due to token limit. Trying with simpler prompt...")
                    # Try with a much simpler prompt
                    simple_prompt = f"""User is looking for: {query.query}
                    
Top candidate found: {top_candidates[0]['name']} with {top_candidates[0]['experience_years']} years experience.
Skills: {', '.join(top_candidates[0]['skills'])}
Projects: {', '.join(top_candidates[0]['projects'])}

Write a brief, helpful response about why this candidate is a good match."""
                    
                    try:
                        ai_message = ai_client.generate_response(
                            system_prompt="You are a helpful HR assistant. Keep responses concise and focused.",
                            user_prompt=simple_prompt,
                            max_tokens=400,
                            temperature=0.5
                        )
                        print("✅ Retry with simpler prompt succeeded")
                    except Exception as retry_e:
                        print(f"⚠️ Retry also failed: {retry_e}")
                        ai_message = _get_enhanced_fallback_message(top_candidates, query.query)
                else:
                    ai_message = _get_enhanced_fallback_message(top_candidates, query.query)
                
            return {"candidates": top_candidates, "message": ai_message}
        else:
            # Enhanced fallback message without AI clients
            if top_candidates:
                # Create a more engaging fallback response
                candidate_count = len(top_candidates)
                
                message = f"I've identified {candidate_count} excellent candidate{'s' if candidate_count != 1 else ''} for your requirements:\n\n"
                
                for i, candidate in enumerate(top_candidates, 1):
                    name = candidate['name']
                    years = candidate['experience_years']
                    skills = candidate['skills']
                    projects = candidate['projects']
                    availability = candidate['availability']
                    
                    score_text = f" (Match Score: {candidate.get('final_score', 0):.2f})" if 'final_score' in candidate else ""
                    availability_emoji = "🟢" if availability == "available" else "🟡" if availability == "on_notice" else "🔴"
                    
                    message += f"{i}. **{name}** - {years} years experience{score_text}\n"
                    message += f"   {availability_emoji} Status: {availability.replace('_', ' ').title()}\n"
                    message += f"   🔧 Skills: {', '.join(skills)}\n"
                    message += f"   📂 Projects: {', '.join(projects)}\n"
                    
                    # Add match reasons if available
                    if 'match_reasons' in candidate and candidate['match_reasons']:
                        message += f"   ✅ Why they fit: {'; '.join(candidate['match_reasons'])}\n"
                    
                    # Add confidence if available
                    if 'confidence' in candidate:
                        confidence = candidate['confidence']
                        message += f"   📊 Match Confidence: {confidence:.0f}%\n"
                    
                    message += "\n"
                
                # Add helpful closing
                message += f"These candidates have been ranked by relevance to your query. "
                if candidate_count > 1:
                    message += f"The top candidate, {top_candidates[0]['name']}, shows the strongest alignment with your requirements. "
                message += "Would you like more specific information about any of these candidates?"
                
            else:
                message = """I wasn't able to find candidates that closely match your specific requirements. 

This could be because:
• The skills or experience level you're looking for aren't available in our current database
• The search terms might be too specific or use different terminology

Suggestions:
• Try broader search terms (e.g., 'developer' instead of 'senior full-stack developer')
• Look for related skills (e.g., 'JavaScript' instead of 'React')
• Consider adjusting experience requirements
• Check spelling and try alternative terminology

Would you like me to help you refine your search criteria?"""
                
            return {"candidates": top_candidates, "message": message}
    
    except Exception as e:
        # Ultimate fallback to keyword search
        print(f"❌ RAG system error: {e}, using keyword fallback")
        return chat_fallback(query)

def chat_fallback(query: ChatQuery):
    """Fallback chat function using simple keyword matching"""
    q = query.query.lower()
    top_k = query.top_k
    candidates = []
    
    print(f"🔍 Searching for: '{q}'")  # Debug print
    
    for e in DATA:
        score = 0
        # Check for ML/Machine Learning keywords
        ml_keywords = ['ml', 'machine learning', 'tensorflow', 'pytorch', 'scikit-learn', 'sklearn', 'pandas']
        for keyword in ml_keywords:
            if keyword in q:
                for skill in e["skills"]:
                    if keyword.lower() in skill.lower() or skill.lower() in ['ml', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas']:
                        score += 3
                        print(f"✅ ML match for {e['name']}: {skill}")
        
        # Check for healthcare keywords
        healthcare_keywords = ['healthcare', 'medical', 'health', 'patient', 'clinical', 'diagnosis', 'hipaa']
        for keyword in healthcare_keywords:
            if keyword in q:
                for project in e["projects"]:
                    if keyword.lower() in project.lower() or any(hw in project.lower() for hw in healthcare_keywords):
                        score += 2
                        print(f"✅ Healthcare match for {e['name']}: {project}")
                for skill in e["skills"]:
                    if keyword.lower() in skill.lower():
                        score += 2
                        print(f"✅ Healthcare skill match for {e['name']}: {skill}")
        
        # General skill matching
        for s in e["skills"]:
            if s.lower() in q:
                score += 2
                print(f"✅ Skill match for {e['name']}: {s}")
        
        # Project keyword matching
        for p in e["projects"]:
            words_in_query = q.split()
            words_in_project = p.lower().split()
            for word in words_in_query:
                if word in words_in_project and len(word) > 2:  # Ignore short words
                    score += 1
                    print(f"✅ Project match for {e['name']}: {p}")
        
        if score > 0:
            candidates.append((score, e))
            print(f"📊 {e['name']} scored: {score}")
    
    print(f"📈 Found {len(candidates)} candidates before sorting")
    
    # Fallback: if no candidates via keywords, try broader matching
    if not candidates:
        print("🔄 No direct matches, trying broader search...")
        for e in DATA:
            # Check if any skill word appears in query
            for skill in e["skills"]:
                skill_words = skill.lower().split()
                query_words = q.split()
                if any(sw in query_words for sw in skill_words if len(sw) > 2):
                    candidates.append((1, e))
                    print(f"✅ Broad match for {e['name']}: {skill}")
                    break
    
    candidates.sort(key=lambda x: (-x[0], -x[1]["experience_years"]))
    top = [c[1] for c in candidates[:top_k]]
    
    print(f"🎯 Returning {len(top)} top candidates")
    
    if top:
        message = f"I found {len(top)} candidate(s) matching your query. Top picks:\n"
        for t in top:
            message += f"- {t['name']} ({t['experience_years']} yrs): {', '.join(t['skills'])}. Projects: {', '.join(t['projects'])}\n"
    else:
        message = "No candidates found matching your criteria. Please try different keywords or check your search terms."
    
    return {"candidates": top, "message": message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
