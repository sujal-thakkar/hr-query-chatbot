import os


def _get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


# Rate limits (SlowAPI format, e.g., "5/minute")
CHAT_RATE_LIMIT = _get_env("CHAT_RATE_LIMIT", "5/minute")
HEALTH_RATE_LIMIT = _get_env("HEALTH_RATE_LIMIT", "30/minute")
ROOT_RATE_LIMIT = _get_env("ROOT_RATE_LIMIT", "30/minute")
RAG_STATUS_RATE_LIMIT = _get_env("RAG_STATUS_RATE_LIMIT", "10/minute")
SEARCH_RATE_LIMIT = _get_env("SEARCH_RATE_LIMIT", "10/minute")
DEBUG_EMPLOYEES_RATE_LIMIT = _get_env("DEBUG_EMPLOYEES_RATE_LIMIT", "5/minute")

# Query bounds
MIN_TOP_K = int(os.getenv("MIN_TOP_K", "1"))
MAX_TOP_K = int(os.getenv("MAX_TOP_K", "20"))

# CORS
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",") if o.strip()]

# Cache TTL (seconds) for RAG query results
QUERY_CACHE_TTL_SECONDS = int(os.getenv("QUERY_CACHE_TTL_SECONDS", "300"))

# Redis cache configuration (optional)
REDIS_URL = os.getenv("REDIS_URL", "")  # e.g., redis://localhost:6379/0
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "auto")  # auto|redis|memory

# AI summary cache TTL (seconds)
AI_SUMMARY_CACHE_TTL_SECONDS = int(os.getenv("AI_SUMMARY_CACHE_TTL_SECONDS", "600"))

# Embedding cache configuration
EMBEDDING_CACHE_ENABLED = os.getenv("EMBEDDING_CACHE_ENABLED", "true").lower() in ("1", "true", "yes")
EMBEDDING_CACHE_DIR = os.getenv("EMBEDDING_CACHE_DIR", str(os.path.join(os.path.dirname(__file__), ".cache")))
EMBEDDING_CACHE_FILE = os.getenv("EMBEDDING_CACHE_FILE", "employee_embeddings.npy")
EMBEDDING_META_FILE = os.getenv("EMBEDDING_META_FILE", "employee_embeddings.json")

# FAISS vector index configuration (optional)
FAISS_ENABLED = os.getenv("FAISS_ENABLED", "true").lower() in ("1", "true", "yes")
FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE", "employee_faiss.index")
FAISS_META_FILE = os.getenv("FAISS_META_FILE", "employee_faiss.json")
FAISS_METRIC = os.getenv("FAISS_METRIC", "ip")  # ip (inner product) or l2

# SQLite database configuration
DB_DIR = os.getenv("DB_DIR", "/app/data")
DB_FILE = os.getenv("DB_FILE", "employees.db")
DB_PATH = os.path.join(DB_DIR, DB_FILE)

# JSON dataset fallback path
DATASET_JSON_PATH = os.getenv("DATASET_JSON_PATH", "/app/dataset/employees.json")
