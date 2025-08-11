# backend/rag.py
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from abc import ABC, abstractmethod

# Local application imports
from query_processor import QueryProcessor, ProcessedQuery
from shared_models import Employee, SearchResult, DEFAULT_EMBEDDING_DIMENSION, DEFAULT_CACHE_SIZE_LIMIT
from config import (
    QUERY_CACHE_TTL_SECONDS,
    EMBEDDING_CACHE_ENABLED,
    EMBEDDING_CACHE_DIR,
    EMBEDDING_CACHE_FILE,
    EMBEDDING_META_FILE,
    FAISS_ENABLED,
    FAISS_INDEX_FILE,
    FAISS_META_FILE,
    FAISS_METRIC,
)
from cache import get_cache

# Attempt to import AI and embedding clients
try:
    from ai_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Optional FAISS
try:
    import faiss  # type: ignore
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

# --- Embedding Strategy Interface ---
class EmbeddingStrategy(ABC):
    """Abstract interface for different embedding strategies."""
    @abstractmethod
    def prepare_embeddings(self, texts: List[str]) -> np.ndarray:
        pass

    @abstractmethod
    def create_query_embedding(self, text: str) -> np.ndarray:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass

# --- Gemini Embedding Strategy ---
class GeminiEmbedding(EmbeddingStrategy):
    """Embedding strategy using Google Gemini."""
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Gemini client is not available.")
        self.client = GeminiClient(api_key)
        if not self.client.is_available():
            raise ConnectionError("Gemini client failed to initialize.")
        self.dimension = DEFAULT_EMBEDDING_DIMENSION
        self.logger = logging.getLogger(__name__)

    def prepare_embeddings(self, texts: List[str]) -> np.ndarray:
        self.logger.info("Generating embeddings with Gemini...")
        embeddings_list = self.client.get_batch_embeddings(
            texts=texts,
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=self.dimension
        )
        return np.array(embeddings_list)

    def create_query_embedding(self, text: str) -> np.ndarray:
        embedding_list = self.client.get_embedding(
            text=text,
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=self.dimension
        )
        return np.array(embedding_list).reshape(1, -1)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "embedding_model": "gemini-embedding-001",
            "dimension": self.dimension,
            "task_type": "RETRIEVAL_DOCUMENT/QUERY",
            "normalization": "Applied for dimensions < 3072"
        }

# --- Sentence Transformer Embedding Strategy ---
class SentenceTransformerEmbedding(EmbeddingStrategy):
    """Embedding strategy using Sentence Transformers."""
    def __init__(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence Transformers library not installed.")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.logger = logging.getLogger(__name__)

    def prepare_embeddings(self, texts: List[str]) -> np.ndarray:
        self.logger.info("Generating embeddings with Sentence Transformers...")
        return self.model.encode(texts)

    def create_query_embedding(self, text: str) -> np.ndarray:
        return self.model.encode([text])

    def get_stats(self) -> Dict[str, Any]:
        return {
            "embedding_model": "all-MiniLM-L6-v2",
            "dimension": self.model.get_sentence_embedding_dimension()
        }

# --- Unified Employee RAG System ---
class EmployeeRAG:
    """Unified RAG system with selectable embedding strategies."""
    def __init__(self, employees_data: List[Dict[str, Any]], api_key: Optional[str] = None):
        self.employees: List[Employee] = [Employee(**emp) for emp in employees_data]
        self.query_processor = QueryProcessor()
        self.logger = logging.getLogger(__name__)
        self.embedding_strategy = self._initialize_strategy(api_key)

        self.employee_embeddings: Optional[np.ndarray] = None
        self.employee_texts: Optional[List[str]] = None
        # In-memory/Redis cache backend (prefix-separated)
        self._cache = get_cache(prefix="rag:query", default_ttl=QUERY_CACHE_TTL_SECONDS)
        self._cache_size_limit = DEFAULT_CACHE_SIZE_LIMIT

        # FAISS
        self._faiss_index = None
        self._faiss_metric = (FAISS_METRIC or "ip").lower()
        self._faiss_active = False

        if self.embedding_strategy:
            self._prepare_documents_and_embeddings()
        else:
            self.logger.warning("No embedding strategy available. RAG system will be inactive.")

    def _initialize_strategy(self, api_key: Optional[str]) -> Optional[EmbeddingStrategy]:
        """Initialize the best available embedding strategy."""
        try:
            if GEMINI_AVAILABLE:
                self.logger.info("Attempting to initialize Gemini embedding strategy.")
                return GeminiEmbedding(api_key)
        except (ImportError, ConnectionError) as e:
            self.logger.warning(f"Gemini strategy failed: {e}")

        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.logger.info("Falling back to Sentence Transformer embedding strategy.")
                return SentenceTransformerEmbedding()
        except ImportError as e:
            self.logger.error(f"Sentence Transformer strategy failed: {e}")
        
        return None

    def is_active(self) -> bool:
        return self.embedding_strategy is not None and self.employee_embeddings is not None

    def _prepare_documents_and_embeddings(self):
        """Create text representations for employees and generate embeddings."""
        self.employee_texts = [self._create_employee_text(emp) for emp in self.employees]
        # Try load from cache
        if EMBEDDING_CACHE_ENABLED and self._load_embeddings_from_cache():
            # Initialize FAISS if available
            self._init_faiss_index()
            return
        try:
            self.employee_embeddings = self.embedding_strategy.prepare_embeddings(self.employee_texts)
            self.logger.info(f"Successfully generated embeddings for {len(self.employees)} employees.")
            # Save to cache
            if EMBEDDING_CACHE_ENABLED:
                self._save_embeddings_to_cache()
            # Initialize FAISS if available
            self._init_faiss_index()
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            self.employee_embeddings = None

    def _dataset_fingerprint(self) -> Dict[str, Any]:
        import hashlib, json as _json
        # Hash essential employee fields to detect dataset changes
        data = [
            {
                "id": e.id,
                "name": e.name,
                "exp": e.experience_years,
                "skills": sorted(e.skills),
                "projects": sorted(e.projects),
                "availability": e.availability,
            }
            for e in self.employees
        ]
        raw = _json.dumps(data, separators=(",", ":"))
        return {
            "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "count": len(self.employees),
        }

    def _cache_paths(self) -> tuple[str, str]:
        import os
        os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)
        return (
            os.path.join(EMBEDDING_CACHE_DIR, EMBEDDING_CACHE_FILE),
            os.path.join(EMBEDDING_CACHE_DIR, EMBEDDING_META_FILE),
        )

    def _faiss_paths(self) -> Tuple[str, str]:
        import os
        os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)
        return (
            os.path.join(EMBEDDING_CACHE_DIR, FAISS_INDEX_FILE),
            os.path.join(EMBEDDING_CACHE_DIR, FAISS_META_FILE),
        )

    def _load_embeddings_from_cache(self) -> bool:
        try:
            import os, json
            cache_path, meta_path = self._cache_paths()
            if not (os.path.exists(cache_path) and os.path.exists(meta_path)):
                return False
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # Validate model/dimension and dataset fingerprint
            stats = self.embedding_strategy.get_stats()
            current_fp = self._dataset_fingerprint()
            if (
                meta.get("embedding_model") == stats.get("embedding_model")
                and meta.get("dimension") == stats.get("dimension")
                and meta.get("dataset_fp") == current_fp
            ):
                self.employee_embeddings = np.load(cache_path)
                self.logger.info("Loaded embeddings from cache (%s)", cache_path)
                return True
            return False
        except Exception as e:
            self.logger.warning("Failed to load embedding cache: %s", e)
            return False

    def _save_embeddings_to_cache(self) -> None:
        try:
            import json
            cache_path, meta_path = self._cache_paths()
            np.save(cache_path, self.employee_embeddings)
            meta = self.embedding_strategy.get_stats().copy()
            meta["dataset_fp"] = self._dataset_fingerprint()
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f)
            self.logger.info("Saved embeddings to cache (%s)", cache_path)
        except Exception as e:
            self.logger.warning("Failed to save embedding cache: %s", e)

    def _ensure_normalized_embeddings(self):
        """L2-normalize in-memory embeddings for cosine/IP similarity consistency."""
        if self.employee_embeddings is None:
            return
        norms = np.linalg.norm(self.employee_embeddings, axis=1, keepdims=True) + 1e-12
        self.employee_embeddings = self.employee_embeddings / norms

    def _init_faiss_index(self):
        """Initialize FAISS index if enabled/available, with file persistence."""
        if not (FAISS_ENABLED and FAISS_AVAILABLE and self.employee_embeddings is not None):
            self._faiss_active = False
            return
        try:
            # Try load existing index
            if self._load_faiss_index():
                self._faiss_active = True
                self.logger.info("FAISS index loaded and active (metric=%s)", self._faiss_metric)
                return

            # Build new index
            dim = self.employee_embeddings.shape[1]
            if self._faiss_metric == "ip":
                self._ensure_normalized_embeddings()
                index = faiss.IndexFlatIP(dim)
                index.add(self.employee_embeddings.astype(np.float32))
            else:
                # l2
                index = faiss.IndexFlatL2(dim)
                index.add(self.employee_embeddings.astype(np.float32))

            self._faiss_index = index
            self._faiss_active = True
            # Persist
            self._save_faiss_index()
            self.logger.info("FAISS index built (%d vectors) and saved", len(self.employees))
        except Exception as e:
            self._faiss_index = None
            self._faiss_active = False
            self.logger.warning("FAISS initialization failed: %s", e)

    def _load_faiss_index(self) -> bool:
        try:
            import os, json
            index_path, meta_path = self._faiss_paths()
            if not (os.path.exists(index_path) and os.path.exists(meta_path)):
                return False
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            stats = self.embedding_strategy.get_stats()
            current_fp = self._dataset_fingerprint()
            # Validate
            if not (
                meta.get("embedding_model") == stats.get("embedding_model")
                and meta.get("dimension") == stats.get("dimension")
                and meta.get("dataset_fp") == current_fp
                and meta.get("metric") == self._faiss_metric
                and meta.get("count") == len(self.employees)
            ):
                return False
            # Load
            self._faiss_index = faiss.read_index(index_path)
            return True
        except Exception as e:
            self.logger.debug("FAISS load failed: %s", e)
            return False

    def _save_faiss_index(self) -> None:
        try:
            import json
            index_path, meta_path = self._faiss_paths()
            faiss.write_index(self._faiss_index, index_path)
            meta = self.embedding_strategy.get_stats().copy()
            meta["dataset_fp"] = self._dataset_fingerprint()
            meta["metric"] = self._faiss_metric
            meta["count"] = len(self.employees)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f)
        except Exception as e:
            self.logger.debug("FAISS save failed: %s", e)

    def _create_employee_text(self, emp: Employee) -> str:
        """Creates a comprehensive text representation for an employee."""
        text_parts = [
            f"Employee: {emp.name}",
            f"Technical Skills: {', '.join(emp.skills)}",
            f"Professional Experience: {emp.experience_years} years",
            f"Project Portfolio: {', '.join(emp.projects)}",
            f"Current Status: {emp.availability}"
        ]
        skill_context = self._generate_skill_context(emp)
        if skill_context:
            text_parts.append(f"Specialization Areas: {skill_context}")
        domain_context = self._generate_domain_context(emp)
        if domain_context:
            text_parts.append(f"Domain Expertise: {domain_context}")
        return " | ".join(text_parts)

    def enhanced_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Performs an enhanced search using the active embedding strategy."""
        if not self.is_active():
            self.logger.warning("RAG system is not active. Cannot perform search.")
            return []

        cache_key = f"{query.lower().strip()}_{top_k}"
        cached = self._cache.get(cache_key)
        if cached:
            self.logger.info(f"Cache hit for query: '{query}'")
            # Convert dicts to SearchResult if needed
            try:
                results: List[SearchResult] = []
                for item in cached:
                    if isinstance(item, SearchResult):
                        results.append(item)
                    else:
                        results.append(SearchResult(**item))
                return results
            except Exception:
                # If cache content invalid, ignore
                pass

        processed_query = self.query_processor.process_query(query)
        semantic_results = self._semantic_search(processed_query, top_k * 2)
        filtered_results = self._apply_advanced_filtering(semantic_results, processed_query)

        detailed_results = []
        for emp_data in filtered_results[:top_k]:
            result = SearchResult(
                employee=emp_data,
                relevance_score=emp_data.get('final_score', 0),
                match_reasons=self._generate_match_reasons(emp_data, processed_query),
                confidence=self._calculate_confidence(emp_data, processed_query)
            )
            detailed_results.append(result)

        # Soft capacity only applies to memory cache; Redis handles TTL eviction
        try:
            self._cache.set(cache_key, [r.model_dump() for r in detailed_results])
        except Exception:
            pass

        return detailed_results

    def _semantic_search(self, processed_query: ProcessedQuery, top_k: int) -> List[Dict[str, Any]]:
        """Core semantic search logic. Returns dicts with score for sorting."""
        search_query = self._create_search_query_text(processed_query)
        query_embedding = self.embedding_strategy.create_query_embedding(search_query)

        # If FAISS active, use it
        if self._faiss_active and self._faiss_index is not None:
            q = query_embedding.astype(np.float32)
            if self._faiss_metric == "ip":
                # Ensure normalized for IP
                q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
            distances, indices = self._faiss_index.search(q, top_k)
            inds = indices[0]
            dists = distances[0]
            results = []
            for idx, dist in zip(inds, dists):
                if idx < 0:
                    continue
                emp = self.employees[int(idx)]
                emp_dict = emp.dict()
                sim = float(dist) if self._faiss_metric == "ip" else float(-dist)
                emp_dict['similarity_score'] = sim
                results.append(emp_dict)
            return results

        # NumPy fallback
        similarities = np.dot(query_embedding, self.employee_embeddings.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            emp = self.employees[idx]
            emp_dict = emp.dict()
            emp_dict['similarity_score'] = float(similarities[idx])
            results.append(emp_dict)
        return results

    def _create_search_query_text(self, processed_query: ProcessedQuery) -> str:
        """Creates a comprehensive search query string from a processed query."""
        search_components = [processed_query.cleaned]
        if processed_query.skill_terms:
            search_components.append(f"Required skills: {', '.join(processed_query.skill_terms)}")
        if processed_query.domain_context:
            search_components.append(f"Domain experience: {', '.join(processed_query.domain_context)}")
        if processed_query.experience_requirements.get('min_years'):
            search_components.append(f"Minimum {processed_query.experience_requirements['min_years']} years experience")
        return " | ".join(search_components)

    # --- Filtering, Scoring, and Helper Methods (largely unchanged) ---
    def _apply_advanced_filtering(self, candidates: List[Dict[str, Any]], processed_query: ProcessedQuery) -> List[Dict[str, Any]]:
        for emp in candidates:
            score = emp['similarity_score']
            exp_req = processed_query.experience_requirements
            if exp_req.get('min_years') and emp['experience_years'] < exp_req['min_years']:
                score -= 0.5
            else:
                score += 0.3
            
            skill_matches = sum(1 for skill in processed_query.skill_terms if any(skill.lower() in s.lower() for s in emp['skills']))
            score += skill_matches * 0.4
            emp['skill_match_count'] = skill_matches

            emp['final_score'] = score
        
        return sorted(candidates, key=lambda x: x['final_score'], reverse=True)

    def _generate_match_reasons(self, employee: Dict[str, Any], processed_query: ProcessedQuery) -> List[str]:
        reasons = []
        for skill in processed_query.skill_terms:
            if any(skill.lower() in s.lower() for s in employee['skills']):
                reasons.append(f"Has skill: {skill}")
        if processed_query.experience_requirements.get('min_years') and employee['experience_years'] >= processed_query.experience_requirements['min_years']:
            reasons.append(f"Meets experience: {employee['experience_years']} years")
        return reasons

    def _calculate_confidence(self, employee: Dict[str, Any], processed_query: ProcessedQuery) -> float:
        confidence = min(employee.get('similarity_score', 0) * 100, 45)
        skill_ratio = employee.get('skill_match_count', 0) / max(len(processed_query.skill_terms), 1)
        confidence += skill_ratio * 30
        if processed_query.experience_requirements.get('min_years') and employee['experience_years'] >= processed_query.experience_requirements['min_years']:
            confidence += 20
        else:
            confidence += 10
        return min(confidence, 100.0)

    def _generate_skill_context(self, employee: Employee) -> str:
        skills = {s.lower() for s in employee.skills}
        contexts = []
        if {'tensorflow', 'pytorch', 'scikit-learn'} & skills:
            contexts.append("artificial intelligence")
        if {'python', 'javascript', 'react', 'django'} & skills:
            contexts.append("full-stack web developer")
        return ", ".join(contexts)

    def _generate_domain_context(self, employee: Employee) -> str:
        projects_text = " ".join(employee.projects).lower()
        domains = []
        if 'health' in projects_text or 'medical' in projects_text:
            domains.append("healthcare")
        if 'finance' in projects_text or 'banking' in projects_text:
            domains.append("fintech")
        return ", ".join(domains)

    def get_embedding_stats(self) -> Dict[str, Any]:
        if not self.is_active():
            return {"status": "RAG system inactive"}
        stats = self.embedding_strategy.get_stats()
        stats["total_employees"] = len(self.employees)
        stats["embedding_shape"] = self.employee_embeddings.shape
        stats["faiss"] = {
            "enabled": bool(self._faiss_active),
            "available": bool(FAISS_AVAILABLE),
            "metric": self._faiss_metric if self._faiss_active else None,
            "index_size": len(self.employees) if self._faiss_active else 0,
        }
        return stats

    def get_cache_size(self) -> int:
        try:
            size = self._cache.size()
            return int(size) if size is not None else 0
        except Exception:
            return 0