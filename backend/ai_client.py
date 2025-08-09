import os
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

# AI Provider imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIClientInterface(ABC):
    """Abstract interface for AI clients"""
    
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         max_tokens: int = 600, temperature: float = 0.7) -> str:
        """Generate AI response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI client is available and configured"""
        pass

class OpenAIClient(AIClientInterface):
    """OpenAI client implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        # Secure API key validation
        if not self.api_key and not api_key:
            logger.warning("⚠️ OpenAI API key not found in environment variables")
        
        if self.api_key and OPENAI_AVAILABLE:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("⚠️ OpenAI library not available")
            if not self.api_key:
                logger.warning("⚠️ OpenAI API key not found")
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         max_tokens: int = 600, temperature: float = 0.7) -> str:
        """Generate response using OpenAI"""
        if not self.client:
            raise Exception("OpenAI client not available")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def is_available(self) -> bool:
        return self.client is not None

class GeminiClient(AIClientInterface):
    """Google Gemini client implementation using latest Google GenAI SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.current_model = None
        
        # Secure API key validation
        if not self.api_key and not api_key:
            raise ValueError("GEMINI_API_KEY environment variable required. Please set your Gemini API key.")
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                # Initialize the new Google GenAI client
                self.client = genai.Client(api_key=self.api_key)
                
                # Try different Gemini models in order of preference (optimized for this use case)
                model_names = [
                    'gemini-2.5-flash',    # Recommended for general text tasks (no thinking overhead)
                    'gemini-1.5-flash',    # Stable fallback
                    'gemini-1.5-pro',      # Stable fallback
                    'gemini-2.5-pro'       # Pro model (uses thinking tokens, so last choice)
                ]
                
                for model_name in model_names:
                    try:
                        # Test if model is available by making a simple request
                        test_response = self.client.models.generate_content(
                            model=model_name,
                            contents="Hello",
                            config=types.GenerateContentConfig(
                                max_output_tokens=10,
                                temperature=0.1
                            )
                        )
                        self.current_model = model_name
                        logger.info(f"✅ Gemini client initialized successfully with {model_name}")
                        break
                    except Exception as model_e:
                        logger.warning(f"⚠️ Model {model_name} failed: {model_e}")
                        continue
                
                if not self.current_model:
                    raise Exception("No Gemini models available")
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("⚠️ Google GenAI library not available")
            if not self.api_key:
                logger.warning("⚠️ Gemini API key not found")
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         max_tokens: int = 600, temperature: float = 0.7) -> str:
        """Generate response using Gemini with latest SDK"""
        if not self.client or not self.current_model:
            raise Exception("Gemini client not available")
        
        try:
            # Combine system and user prompts for Gemini
            combined_prompt = f"""Role and Instructions:
{system_prompt}

User Request:
{user_prompt}

Please provide a comprehensive response following the instructions above."""
            
            # Configure generation parameters using the new SDK
            # For Gemini 2.5-flash, use standard token limits (no thinking overhead)
            # For Gemini 2.5-pro, we need significantly more tokens due to thinking overhead
            if self.current_model == "gemini-2.5-pro":
                # Gemini 2.5-pro model needs much higher token limits due to thinking process
                effective_max_tokens = max(max_tokens * 3, 1500)  # At least 3x the requested tokens
            else:
                # For all other models (including 2.5-flash), use the requested amount with reasonable minimum
                effective_max_tokens = max(max_tokens, 400)
            
            generation_config = types.GenerateContentConfig(
                max_output_tokens=effective_max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=40
            )
            
            # Add thinking config only for 2.5-pro model (it requires thinking mode)
            if self.current_model == "gemini-2.5-pro":
                # Pro model requires thinking mode - set a reasonable budget
                generation_config.thinking_config = types.ThinkingConfig(thinking_budget=10000)
            
            response = self.client.models.generate_content(
                model=self.current_model,
                contents=combined_prompt,
                config=generation_config
            )
            
            # Handle response properly - check if response has content
            text_content = None
            
            # Debug logging
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response has text attr: {hasattr(response, 'text')}")
            
            # Method 1: Try response.text first
            try:
                if response and hasattr(response, 'text') and response.text:
                    text_content = response.text
                    if text_content and text_content.strip():
                        return text_content.strip()
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")
            
            # Method 2: Try extracting from candidates
            if response and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Check finish reason for debugging
                finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                logger.debug(f"Candidate finish reason: {finish_reason}")
                
                if hasattr(candidate, 'content') and candidate.content:
                    # Check if content has parts
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        parts_text = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                parts_text.append(part.text)
                        if parts_text:
                            return " ".join(parts_text).strip()
                    # Alternative way to get text from content
                    elif hasattr(candidate.content, 'text') and candidate.content.text:
                        return candidate.content.text.strip()
                    else:
                        logger.warning(f"Content exists but no parts found. Parts: {getattr(candidate.content, 'parts', 'NO_PARTS')}")
                else:
                    logger.warning(f"Candidate has no content. Finish reason: {finish_reason}")
            
            # Method 3: Check if response has direct content
            if response and hasattr(response, 'content'):
                if hasattr(response.content, 'parts') and response.content.parts:
                    for part in response.content.parts:
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
            
            # Fallback if no content found - provide debugging information
            logger.error(f"No text content found. Response type: {type(response)}")
            logger.error(f"Response.text: {repr(getattr(response, 'text', 'NO_TEXT_ATTR'))}")
            logger.error(f"Has candidates: {hasattr(response, 'candidates')}")
            
            if hasattr(response, 'candidates') and response.candidates:
                logger.error(f"Candidates count: {len(response.candidates)}")
                candidate = response.candidates[0]
                logger.error(f"First candidate content: {getattr(candidate, 'content', 'NO_CONTENT')}")
                logger.error(f"Finish reason: {getattr(candidate, 'finish_reason', 'NO_FINISH_REASON')}")
                
                # Check for safety ratings that might have blocked the response
                if hasattr(candidate, 'safety_ratings'):
                    logger.error(f"Safety ratings: {candidate.safety_ratings}")
                
                # Check for other blocking reasons
                if hasattr(response, 'prompt_feedback'):
                    logger.error(f"Prompt feedback: {response.prompt_feedback}")
            
            # Provide a more specific error message
            error_msg = "No text content in response"
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', None)
                if finish_reason:
                    error_msg += f" (finish_reason: {finish_reason})"
            
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def is_available(self) -> bool:
        return self.client is not None and self.current_model is not None
    
    def get_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT", 
                     output_dimensionality: int = 768) -> List[float]:
        """Generate embeddings using Gemini's native embedding model"""
        if not self.client:
            raise Exception("Gemini client not available")
        
        try:
            result = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=output_dimensionality
                )
            )
            
            # Normalize embedding for smaller dimensions (as per official docs)
            if output_dimensionality < 3072:
                import numpy as np
                embedding_values = np.array(result.embeddings[0].values)
                normalized_embedding = embedding_values / np.linalg.norm(embedding_values)
                return normalized_embedding.tolist()
            else:
                return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            raise
    
    def get_batch_embeddings(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT",
                           output_dimensionality: int = 768) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        if not self.client:
            raise Exception("Gemini client not available")
        
        try:
            result = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=output_dimensionality
                )
            )
            
            embeddings = []
            for embedding_obj in result.embeddings:
                if output_dimensionality < 3072:
                    import numpy as np
                    embedding_values = np.array(embedding_obj.values)
                    normalized_embedding = embedding_values / np.linalg.norm(embedding_values)
                    embeddings.append(normalized_embedding.tolist())
                else:
                    embeddings.append(embedding_obj.values)
            
            return embeddings
        except Exception as e:
            logger.error(f"Gemini batch embedding error: {e}")
            raise

class AIClientManager:
    """Manages multiple AI clients with fallback support"""
    
    def __init__(self):
        self.clients = {}
        self.primary_client = None
        self.fallback_clients = []
        
        # Initialize available clients
        self._initialize_clients()
        self._setup_priority()
    
    def _initialize_clients(self):
        """Initialize all available AI clients"""
        # Try to initialize Gemini first (better limits)
        gemini_client = GeminiClient()
        if gemini_client.is_available():
            self.clients['gemini'] = gemini_client
            logger.info("🤖 Gemini client ready")
        
        # Try to initialize OpenAI as fallback
        openai_client = OpenAIClient()
        if openai_client.is_available():
            self.clients['openai'] = openai_client
            logger.info("🤖 OpenAI client ready")
    
    def _setup_priority(self):
        """Setup client priority (Gemini first, OpenAI as fallback)"""
        if 'gemini' in self.clients:
            self.primary_client = self.clients['gemini']
            logger.info("🚀 Using Gemini as primary AI client")
            
            if 'openai' in self.clients:
                self.fallback_clients.append(self.clients['openai'])
                logger.info("🔄 OpenAI available as fallback")
        elif 'openai' in self.clients:
            self.primary_client = self.clients['openai']
            logger.info("🚀 Using OpenAI as primary AI client")
        else:
            logger.warning("⚠️ No AI clients available")
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         max_tokens: int = 600, temperature: float = 0.7) -> str:
        """Generate response with automatic fallback"""
        
        # Try primary client first
        if self.primary_client:
            try:
                response = self.primary_client.generate_response(
                    system_prompt, user_prompt, max_tokens, temperature
                )
                return response
            except Exception as e:
                logger.warning(f"Primary client failed: {e}")
        
        # Try fallback clients
        for fallback_client in self.fallback_clients:
            try:
                response = fallback_client.generate_response(
                    system_prompt, user_prompt, max_tokens, temperature
                )
                logger.info("✅ Fallback client succeeded")
                return response
            except Exception as e:
                logger.warning(f"Fallback client failed: {e}")
                continue
        
        # If all clients fail, provide a helpful fallback response
        logger.error("❌ All AI clients failed - providing fallback response")
        return """Based on the search results, I found several matching candidates for your query. 
        
While I cannot provide detailed AI analysis at the moment due to API limitations, the search system has identified candidates that match your requirements based on their skills, experience, and project background.

Please review the candidate details below to evaluate their suitability for your role. Each candidate has been scored based on how well they match your search criteria."""
    
    def is_available(self) -> bool:
        """Check if any AI client is available"""
        return self.primary_client is not None or len(self.fallback_clients) > 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all AI clients"""
        status = {
            "available_clients": list(self.clients.keys()),
            "primary_client": type(self.primary_client).__name__ if self.primary_client else None,
            "fallback_clients": [type(client).__name__ for client in self.fallback_clients],
            "total_clients": len(self.clients)
        }
        return status

# Global AI client manager instance
ai_manager = AIClientManager()

def get_ai_client() -> AIClientManager:
    """Get the global AI client manager"""
    return ai_manager
