# 🤖 HR Query Chatbot

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini API](https://img.shields.io/badge/Gemini%20API-2.5--flash-blue.svg)](https://ai.google.dev/)

An intelligent HR assistant powered by **Google Gemini AI** that helps HR teams find the perfect candidates using natural language queries. The system combines semantic search with AI-generated insights to match candidates based on skills, experience, and project history.

## 🚀 What's New (v2+ Enhancements)

Recent improvements (reflected in code, newly documented here):

- SQLite persistence layer with automatic one-time seeding from `dataset/employees.json`
- Smart seeding guarded by `meta` table sentinel (`key='seeded'`)
- Optional Redis cache (query + AI summary) with `CACHE_BACKEND=auto|redis|memory`
- Prometheus metrics at `/metrics` (counters + latency histogram)
- Request ID middleware adds `X-Request-ID` header to every response
- Detailed RAG diagnostics endpoint `/system/rag-status`
- Debug dataset endpoint `/debug/employees` (truncated preview)
- Configurable per-endpoint rate limits via environment variables (SlowAPI)
- Pluggable embedding & FAISS vector index toggles (`FAISS_ENABLED`)
- Safer chat input validation & basic XSS guard
- Multi-provider AI client fallback logic (`ai_client.py`)

> These make the project more production-ready (observability, resilience, persistence) while retaining simple local setup.

## ✨ Features

### 🔍 **Intelligent Search**
- **Semantic Search**: Powered by Gemini embeddings for context-aware candidate matching
- **Natural Language Queries**: Ask questions like "Find someone with ML experience for healthcare"
- **Multi-factor Scoring**: Combines skill matching, experience, and domain relevance

### 🤖 **AI-Powered Insights**
- **Gemini 2.5 Flash**: Lightning-fast AI responses with detailed candidate analysis
- **Personalized Recommendations**: AI explains why each candidate is a perfect fit
- **Conversational Interface**: Natural, recruiter-like responses

### 🛡️ **Enterprise-Ready**
- **Rate Limiting**: Configurable API rate limits for production use
- **Input Validation**: XSS protection and secure input handling
- **Error Handling**: Graceful fallbacks and detailed error reporting
- **Health Monitoring**: Comprehensive system health endpoints

### 📊 **Advanced Analytics**
- **Match Confidence**: AI-calculated confidence scores for each match
- **Detailed Reasoning**: Explains why candidates match your requirements
- **Performance Metrics**: Track search accuracy and response times

## 🏗️ Architecture

```mermaid
graph TB
    A[👤 User] --> B[🎨 Streamlit Frontend]
    B --> C[⚡ FastAPI Backend]
    C --> D[🧠 Gemini AI Client]
    C --> E[🔍 RAG System]
    E --> F[📊 Gemini Embeddings]
    E --> G[👥 Employee Dataset]
    D --> H[🤖 Gemini 2.5 Flash]
    
    style A fill:#e1f5fe,color:#0d1117
    style B fill:#f3e5f5,color:#0d1117
    style C fill:#e8f5e8,color:#0d1117
    style D fill:#fff3e0,color:#0d1117
    style E fill:#fce4ec,color:#0d1117
    style F fill:#f1f8e9,color:#0d1117
    style G fill:#e3f2fd,color:#0d1117
    style H fill:#fff8e1,color:#0d1117
```

### 🔧 **Core Components**

- **🎨 Streamlit Frontend**: Interactive chat interface with real-time responses
- **⚡ FastAPI Backend**: High-performance async API with automatic documentation
- **🧠 AI Engine**: Google Gemini 2.5 Flash for intelligent candidate analysis
- **🔍 RAG System**: Retrieval-Augmented Generation with semantic search
- **📊 Embeddings**: Gemini embeddings for context-aware similarity matching
- **👥 Data Layer**: Structured employee profiles with skills and projects

### �️ Data Storage & Caching

| Layer | Default | Notes |
|-------|---------|-------|
| Employee records | SQLite (`/app/data/employees.db`) | Auto-created & seeded if empty |
| Seed source | `dataset/employees.json` | Used only when DB empty & not yet seeded |
| Query / AI summary cache | Memory or Redis | `CACHE_BACKEND` + `REDIS_URL` control selection |
| Embedding cache | Local files | `EMBEDDING_CACHE_DIR` + file names configurable |
| Vector index | FAISS (optional) | Enable with `FAISS_ENABLED=true` |

Inspect DB (Docker):
```bash
docker compose exec backend sh -c "sqlite3 /app/data/employees.db 'SELECT COUNT(*) FROM employees;'"
```

Force re-seed (dev): delete the DB file or run `DELETE FROM meta WHERE key='seeded';` then restart.

## �🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- [Google Gemini API key](https://ai.google.dev/) (free tier available)

### 1️⃣ **Clone & Setup**
```bash
git clone https://github.com/your-username/hr-query-chatbot.git
cd hr-query-chatbot
pip install -r requirements.txt
```

### 2️⃣ **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
```

### 3️⃣ **Start the Backend**
```bash
python backend/main.py
```
The API will be available at `http://localhost:8000`

### 4️⃣ **Launch the Frontend**
```bash
streamlit run frontend/app.py
```
Open `http://localhost:8501` in your browser

## 💬 Usage Examples

### Natural Language Queries
```
"Find someone with machine learning experience for a healthcare project"
"I need a Python developer with 5+ years experience"
"Who has worked on mobile apps and is currently available?"
"Find candidates with both React and Node.js skills"
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Chat query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Find ML engineers", "top_k": 3}'

# Direct search
curl "http://localhost:8000/employees/search?skill=Python&min_experience=3"

# RAG status diagnostics
curl http://localhost:8000/system/rag-status

# Prometheus metrics
curl http://localhost:8000/metrics

# Debug (preview first 3 employees)
curl http://localhost:8000/debug/employees
```
## 🔧 Development

### 📁 **Project Structure**
```
hr-query-chatbot/
├── 🎨 frontend/
│   └── app.py                  # Streamlit chat interface
├── ⚡ backend/
│   ├── main.py                 # FastAPI server & endpoints
│   ├── ai_client.py            # Multi-AI client manager
│   ├── gemini_rag.py           # Gemini-powered RAG system
│   ├── query_processor.py      # Query enhancement
│   └── shared_models.py        # Data models
├── 🧪 tests/
│   ├── test_enhanced_system.py # Complete system tests
│   ├── test_gemini_implementation.py # AI integration tests
│   └── test_security.py        # Security & validation tests
├── 📊 dataset/
│   └── employees.json          # Employee database
└── 📝 docs/                    # Documentation files
```

### 🧪 **Testing**
```bash
# Run all system tests
cd tests
python test_enhanced_system.py

# Test AI integration
python test_gemini_implementation.py

# Test security features
python test_security.py

# Quick health check
python test_detailed_flow.py
```

### 🔍 **API Documentation**

#### **POST /chat**
Intelligent conversational search with AI analysis
```json
{
  "query": "Find ML engineers for healthcare",
  "top_k": 5
}
```

#### **GET /employees/search** 
Direct search with filters
```bash
?skill=Python&min_experience=3&availability=available
```

#### **GET /health**
System health and status monitoring
```bash
?detailed=true  # For comprehensive system status
```

## 🛠️ **Configuration**

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here    # Fallback AI provider
HOST=0.0.0.0                           # Server host
PORT=8000                              # Server port
LOG_LEVEL=INFO                         # Logging level
ALLOWED_ORIGINS=http://localhost:8501  # Comma-separated list of allowed origins

# Rate limits (SlowAPI format)
CHAT_RATE_LIMIT=5/minute
HEALTH_RATE_LIMIT=30/minute
ROOT_RATE_LIMIT=30/minute
RAG_STATUS_RATE_LIMIT=10/minute
SEARCH_RATE_LIMIT=10/minute
DEBUG_EMPLOYEES_RATE_LIMIT=5/minute

# Query bounds
MIN_TOP_K=1
MAX_TOP_K=20

# Caching (RAG and AI summaries)
QUERY_CACHE_TTL_SECONDS=300
AI_SUMMARY_CACHE_TTL_SECONDS=600
CACHE_BACKEND=auto                     # auto|redis|memory
REDIS_URL=redis://redis:6379/0         # Provided by docker-compose

# Embedding / vector settings
EMBEDDING_CACHE_ENABLED=true
EMBEDDING_CACHE_DIR=/app/backend/.cache
EMBEDDING_CACHE_FILE=employee_embeddings.npy
EMBEDDING_META_FILE=employee_embeddings.json
FAISS_ENABLED=true
FAISS_INDEX_FILE=employee_faiss.index
FAISS_META_FILE=employee_faiss.json
FAISS_METRIC=ip                        # ip or l2

# Database & dataset
DB_DIR=/app/data
DB_FILE=employees.db
DATASET_JSON_PATH=/app/dataset/employees.json
```
> Omit any variable to use defaults. Boolean values accept: `true|false|1|0|yes|no`.

### Advanced Settings
- **Rate Limiting**: Configured in `backend/main.py`
- **Model Selection**: Set in `backend/ai_client.py`
- **Search Parameters**: Tunable in `backend/gemini_rag.py`

## 📈 **Performance & Scaling**

### Current Capabilities
- **Response Time**: < 2 seconds for typical queries
- **Concurrent Users**: 50+ simultaneous requests
- **Search Accuracy**: 85%+ relevance for complex queries
- **Uptime**: 99.9% with proper deployment

### Optimization Tips
- Use environment-specific configurations
- Enable response caching for repeated queries
- Monitor API quotas for Gemini usage
- Scale horizontally with load balancers

## 🚀 **Deployment**

### Docker Deployment
```bash
# Build and run with Docker
docker build -t hr-chatbot .
docker run -p 8000:8000 -p 8501:8501 hr-chatbot
```

### Docker Compose (Recommended)
Includes backend, frontend, Redis, volumes.
```bash
docker compose up -d --build
docker compose logs -f backend
```
Services:
- Backend: http://localhost:8000 (Swagger UI: /docs, Metrics: /metrics)
- Frontend: http://localhost:8501
- Redis: localhost:6379 (if enabled)

Persistent volumes:
- backend-data -> SQLite DB
- redis-data -> Redis persistence

Tear down (removes volumes):
```bash
docker compose down -v
```

### Cloud Deployment
- **Heroku**: Ready for Heroku with Procfile
- **AWS/GCP**: Compatible with container services
- **Railway**: One-click deployment ready

### Render Blueprint Deployment (Recommended for this repo)

This repository includes a `render.yaml` that defines two Docker services (backend + frontend).

Steps:
1. Fork or push the repo to your own GitHub account (avoid storing real secrets).
2. Remove any accidental committed secrets. The file `backend/.env` should NOT exist (use `backend/.env.example`).
3. In the Render dashboard choose: New > Blueprint > select the repo.
4. Render parses `render.yaml`. It will create services named `backend` and `frontend`.
5. Before first deploy, set the environment variables for each service:
  - `GEMINI_API_KEY` (required for AI features)
  - `OPENAI_API_KEY` (optional fallback)
  - Any overrides (`CACHE_BACKEND`, `REDIS_URL`, etc.)
6. Trigger the deploy. Watch build logs. (Expected build time: ~1–2 min on free tier.)
7. Verify the backend health endpoint:
  - `https://<backend-service>.onrender.com/health` should return `{"status":"healthy"}`
8. Open the frontend URL. Chat should function; if AI keys missing you'll see a degraded mode warning in backend logs.

Common Issues & Fixes:
| Problem | Cause | Resolution |
|---------|-------|-----------|
| `chown: invalid user 'app:app'` | Dockerfile attempted chown before user creation | Fixed by creating user first (already updated) |
| `dockerfile parse error unknown instruction` | Multi-line RUN broken by newline without `\` | Fixed in backend Dockerfile |
| Healthcheck failing | curl missing in slim image | Added `curl` to backend Dockerfile |
| FAISS import error | Missing `libgomp` | Added `libgomp1` to backend Dockerfile |
| Missing API keys warning | Keys not set in Render env | Add them via Render dashboard > Environment |

Re-deploy: push to `main` or click Manual Deploy in the service menu.

Local `.env` setup:
```
cp backend/.env.example backend/.env
```
Fill values; never commit the populated file.

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Google Gemini AI** for powerful language models and embeddings
- **FastAPI** for the excellent async web framework
- **Streamlit** for the intuitive frontend framework
- **Open Source Community** for inspiration and tools

## 📞 **Support**

- **Documentation**: Check the `/docs` endpoint when running the API
- **Issues**: Report bugs or request features in [GitHub Issues](../../issues)
- **Discussions**: Join conversations in [GitHub Discussions](../../discussions)

---

⭐ **Star this repo** if you find it helpful! ⭐

**Example:**
```
GET /employees/search?skill=Python&min_experience=4&availability=available
```

## AI Development Process

### AI Tools Used
- **GitHub Copilot**: ~40% of code generation, especially boilerplate FastAPI endpoints and Pydantic models
- **ChatGPT**: ~30% for architecture planning, documentation, and complex logic design
- **Manual Development**: ~30% for business logic, data structure design, and integration

### AI Assistance Breakdown
- **Code Generation**: Copilot helped with FastAPI route definitions, error handling, and type annotations
- **Architecture Decisions**: ChatGPT assisted in choosing FastAPI + Streamlit stack and API design patterns
- **Documentation**: AI-generated initial README structure and API documentation
- **Debugging**: Manual debugging for OpenAI API integration and CORS issues
- **Data Creation**: Manual creation of realistic employee dataset

### AI Limitations Encountered
- **Complex Business Logic**: Employee scoring algorithm required manual implementation
- **Integration Issues**: CORS configuration and environment variable handling needed manual fixes
- **OpenAI API Updates**: Had to manually update from deprecated API format to new client structure

## Technical Decisions

### Technology Choices
- **FastAPI vs Flask**: Chose FastAPI for automatic API documentation, type hints, and async support
- **OpenAI vs Local Models**: Used OpenAI for reliable performance and quick development; local models would require more setup
- **Streamlit vs React**: Streamlit for rapid prototyping and minimal frontend complexity
- **JSON vs Database**: JSON for simplicity in this prototype; PostgreSQL would be better for production

### Trade-offs
- **Performance vs Simplicity**: Keyword matching is fast but less sophisticated than semantic embeddings
- **Cost vs Quality**: OpenAI API costs money but provides high-quality responses
- **Development Speed vs Scalability**: Current architecture prioritizes quick development over enterprise scalability

## Future Improvements

### Technical Enhancements
- **Vector Embeddings**: Implement FAISS or Pinecone for semantic similarity search
- **Advanced RAG**: Add document chunking and retrieval ranking
- **Database Upgrade**: Optionally move from SQLite to PostgreSQL for heavy write workloads
- **Caching Extensions**: Expand Redis usage (session memory, per-user contexts)
- **Testing**: Comprehensive unit and integration test suite

### Features
- **User Authentication**: Add login/logout and user-specific queries
- **Advanced Filtering**: Date-based availability, location, salary ranges
- **Analytics Dashboard**: Query patterns and employee utilization insights
- **Email Integration**: Direct employee contact through the platform
- **Mobile App**: React Native or Flutter mobile interface

### AI Improvements
- **Fine-tuning**: Custom model training on HR-specific data
- **Multi-modal**: Support for resume parsing and image analysis
- **Conversation Memory**: Context-aware multi-turn conversations
- **Feedback Learning**: System that improves based on user feedback

## 🔍 Observability & Operations

- Metrics: scrape `/metrics` (Prometheus exposition format)
- Key series: `http_requests_total{method,path,status}` & `http_request_duration_seconds_bucket`
- Trace correlation: `X-Request-ID` header appears in responses & logs
- Health: `/health` (basic) and `/health?detailed=true` (AI + RAG diagnostics)
- RAG diagnostics: `/system/rag-status` performs a quick test search

## ✏️ Adding / Updating Employees

No write endpoint yet. Options:
1. Edit `dataset/employees.json`, delete `/app/data/employees.db`, restart to re-seed.
2. Python REPL inside container: import `upsert_employees` from `db.py`.
3. Direct SQL via `sqlite3` inside container.

If you need RESTful CRUD (`POST /employees`), open an issue / PR.

## 🔐 Security Notes

- Basic XSS filtering on chat queries
- Per-endpoint rate limits (env-configurable)
- CORS restricted by `ALLOWED_ORIGINS` (tighten in production)
- Recommend adding auth (API keys / OAuth) before public exposure

## ✅ Deployment Verification Checklist

```text
1. GET /health -> {"status":"healthy"}
2. GET /system/rag-status -> status available or fallback string
3. GET /employees/search?skill=Python -> returns expected count
4. GET /metrics -> Prometheus metrics visible
5. Logs show AI client initialized OR graceful warning
6. sqlite3 /app/data/employees.db 'SELECT COUNT(*) FROM employees;' shows rows
```

## Demo

### Sample Queries
1. "Find React developers with mobile experience"
2. "Who has worked on healthcare projects?"
3. "Suggest someone for a machine learning role"
4. "Find AWS experts available immediately"

### Screenshots

#### Chat Interface (Desktop + Mobile)

<table>
  <tr>
    <td align="center" width="66%" valign="top">
      <img src="https://github.com/user-attachments/assets/a20ba77e-a163-4a58-bd7f-e1c6d47e6d3d" alt="Chat interface — desktop view" title="Chat interface — desktop view" width="100%" />
      <br />
      <sub>Desktop — Clean, intuitive Streamlit UI</sub>
    </td>
    <td align="center" width="34%" valign="top">
      <img src="https://github.com/user-attachments/assets/d182f0df-7aaa-4bf7-a402-63558af72972" alt="Chat interface — mobile conversation view" title="Chat interface — mobile conversation view" width="48%" />
      <img src="https://github.com/user-attachments/assets/3d8d673c-0ff6-40ef-8f3a-b1a3d0ffc18c" alt="Chat interface — mobile results view" title="Chat interface — mobile results view" width="48%" />
      <br />
      <sub>Mobile — Conversation and results</sub>
    </td>
  </tr>
  
</table>

#### API Documentation (Grid)

<table>
  <tr>
    <td align="center" width="50%" valign="top">
  <img src="https://github.com/user-attachments/assets/f6c1f328-e975-4251-8c45-9aa19613460d" alt="Swagger UI — API docs overview" title="Swagger UI — API docs overview" width="100%" />
      <br />
      <sub>API docs — Overview</sub>
    </td>
    <td align="center" width="50%" valign="top">
  <img src="https://github.com/user-attachments/assets/ebe10617-1790-4f2c-9880-6c01e3741e04" alt="Swagger UI — Endpoint list and try-out" title="Swagger UI — Endpoint list and Try it out" width="100%" />
      <br />
      <sub>API docs — Endpoint list & Try it out</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top">
  <img src="https://github.com/user-attachments/assets/452d599a-2bd7-468a-bd86-825822511e00" alt="Swagger UI — Endpoint details" title="Swagger UI — Endpoint details" width="100%" />
      <br />
      <sub>API docs — Endpoint details</sub>
    </td>
    <td align="center" width="50%" valign="top">
  <img src="https://github.com/user-attachments/assets/ff070cd9-adf5-4f42-b36b-01d50ecb3705" alt="Swagger UI — Schemas and models" title="Swagger UI — Schemas and models" width="100%" />
      <br />
      <sub>API docs — Schemas & Models</sub>
    </td>
  </tr>
</table>

#### Search Results (Desktop)

<p align="center">
  <img src="https://github.com/user-attachments/assets/aeaf8d00-47fe-4130-b033-827bab84abbb" alt="Search results — structured employee profiles with skills and experience" title="Search results — structured employee profiles with skills and experience" width="85%" />
  <br />
  <sub>Desktop — Structured employee profiles with skills, projects, and experience</sub>
</p>


## Development Notes
- Built in 2 days following rapid prototyping principles
- Focused on core functionality over UI polish
- Designed for easy extension and modification
- Emphasizes practical HR use cases and realistic data

## License
MIT License - Open for educational and commercial use.
