# backend/shared_models.py
"""
Shared data models and types used across the RAG implementations
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SearchResult:
    """Unified search result structure used by all RAG implementations"""
    employee: Dict[str, Any]
    relevance_score: float
    match_reasons: List[str]
    confidence: float

@dataclass 
class ProcessedQuery:
    """Processed query structure from query processor"""
    original: str
    cleaned: str
    keywords: List[str]
    skill_terms: List[str]
    experience_requirements: Dict[str, int]
    domain_context: List[str]
    priority_score: float

# Common constants
DEFAULT_EMBEDDING_DIMENSION = 768
DEFAULT_CACHE_SIZE_LIMIT = 100
DEFAULT_TOP_K = 5

# Skill synonyms mapping (shared across implementations)
SKILL_SYNONYMS = {
    'ml': ['machine learning', 'ai', 'artificial intelligence'],
    'js': ['javascript', 'ecmascript'],
    'ts': ['typescript'],
    'py': ['python'],
    'react': ['reactjs', 'react.js'],
    'node': ['nodejs', 'node.js'],
    'db': ['database', 'databases'],
    'api': ['rest api', 'restful api', 'web api'],
    'cloud': ['aws', 'azure', 'gcp', 'google cloud'],
    'mobile': ['ios', 'android', 'react native', 'flutter'],
    'data': ['data science', 'data analysis', 'analytics'],
    'backend': ['server-side', 'server side'],
    'frontend': ['client-side', 'client side', 'ui', 'user interface']
}

# Domain keywords mapping (shared across implementations)
DOMAIN_KEYWORDS = {
    'healthcare': ['medical', 'health', 'patient', 'clinical', 'diagnosis', 'hipaa', 'ehr', 'emr'],
    'fintech': ['financial', 'banking', 'payment', 'cryptocurrency', 'blockchain', 'trading'],
    'ecommerce': ['retail', 'shopping', 'marketplace', 'commerce', 'store', 'cart'],
    'education': ['learning', 'educational', 'academic', 'student', 'course', 'training'],
    'gaming': ['game', 'gaming', 'unity', 'unreal', 'graphics', 'entertainment'],
    'iot': ['internet of things', 'sensors', 'embedded', 'hardware', 'device']
}
