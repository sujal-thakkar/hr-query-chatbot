# backend/api_client.py
import requests
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from functools import wraps

@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    status_code: Optional[int]
    retry_count: int = 0

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs, retry_count=attempt)
                except (requests.exceptions.ConnectionError, 
                       requests.exceptions.Timeout,
                       requests.exceptions.RequestException) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(f"All {max_retries + 1} attempts failed: {e}")
            
            raise last_exception
        return wrapper
    return decorator

class RobustAPIClient:
    """Robust API client with retry mechanisms and better error handling"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def health_check(self, retry_count: int = 0) -> APIResponse:
        """Check if the API is healthy with retry mechanism"""
        try:
            response = requests.get(
                f"{self.base_url}/health", 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return APIResponse(
                    success=True,
                    data=response.json(),
                    error=None,
                    status_code=response.status_code,
                    retry_count=retry_count
                )
            else:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"Health check failed with status {response.status_code}",
                    status_code=response.status_code,
                    retry_count=retry_count
                )
                
        except requests.exceptions.Timeout:
            error_msg = f"Health check timeout after {self.timeout}s (attempt {retry_count + 1})"
            self.logger.warning(error_msg)
            raise requests.exceptions.Timeout(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection failed: {str(e)} (attempt {retry_count + 1})"
            self.logger.warning(error_msg)
            raise requests.exceptions.ConnectionError(error_msg)
    
    @retry_on_failure(max_retries=2, delay=0.5, backoff=1.5)
    def search_candidates(self, query: str, top_k: int = 5, retry_count: int = 0) -> APIResponse:
        """Search for candidates with retry mechanism"""
        try:
            payload = {"query": query, "top_k": top_k}
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse(
                    success=True,
                    data=data,
                    error=None,
                    status_code=response.status_code,
                    retry_count=retry_count
                )
            else:
                error_data = None
                try:
                    error_data = response.json()
                except:
                    pass
                    
                return APIResponse(
                    success=False,
                    data=error_data,
                    error=f"Search failed with status {response.status_code}: {response.text[:200]}",
                    status_code=response.status_code,
                    retry_count=retry_count
                )
                
        except requests.exceptions.Timeout:
            error_msg = f"Search timeout after {self.timeout}s (attempt {retry_count + 1})"
            self.logger.warning(error_msg)
            raise requests.exceptions.Timeout(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Search connection failed: {str(e)} (attempt {retry_count + 1})"
            self.logger.warning(error_msg)
            raise requests.exceptions.ConnectionError(error_msg)
    
    def get_debug_info(self) -> APIResponse:
        """Get debug information from the API"""
        try:
            response = requests.get(
                f"{self.base_url}/debug/employees",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return APIResponse(
                    success=True,
                    data=response.json(),
                    error=None,
                    status_code=response.status_code
                )
            else:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"Debug info failed with status {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                error=f"Debug info error: {str(e)}",
                status_code=None
            )
