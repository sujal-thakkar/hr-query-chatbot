# HR Resource Query Chatbot

## Overview
An intelligent HR assistant chatbot that helps HR teams find employees using natural language processing and retrieval techniques. The system allows users to search for employees by skills, experience, and project history using both keyword search and conversational AI queries powered by OpenAI's GPT-3.5-turbo.

## Features
- **REST API Endpoints**: `/chat` for conversational queries and `/employees/search` for direct filtering
- **Vector Search**: Keyword-based scoring system for employee matching
- **LLM Generation**: OpenAI integration for natural language responses with intelligent fallback
- **Frontend Interface**: Streamlit-based chat interface for easy interaction
- **Comprehensive Dataset**: 15+ employee profiles with skills, experience, projects, and availability

## Architecture
- **FastAPI Backend**: Asynchronous REST API with automatic documentation
- **Retrieval System**: Keyword matching with experience-based scoring
- **LLM Integration**: OpenAI GPT-3.5-turbo for natural language generation
- **Streamlit Frontend**: Simple chat interface with real-time search results
- **Data Layer**: JSON-based employee database with structured profiles

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │    │   FastAPI       │    │   OpenAI API    │
│   (Frontend)    │───▶│   (Backend)     │───▶│   (LLM)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Employee Dataset│
                       │   (JSON)        │
                       └─────────────────┘
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Installation Steps

1. **Clone and navigate to the project:**
```bash
cd hr-query-chatbot
```

2. **Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the backend server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

5. **Run the frontend (in a new terminal):**
```bash
cd frontend
streamlit run app.py
```

6. **Access the application:**
- Frontend: http://localhost:8501
- Backend API Docs: http://localhost:8000/docs

## API Documentation

### Endpoints

#### POST /chat
Conversational HR query endpoint with AI-powered responses.

**Request:**
```json
{
  "query": "Find Python developers with 3+ years experience in healthcare",
  "top_k": 5
}
```

**Response:**
```json
{
  "candidates": [
    {
      "id": 3,
      "name": "Dr. Sarah Chen",
      "skills": ["Python", "TensorFlow", "PyTorch", "ML"],
      "experience_years": 6,
      "projects": ["Medical Diagnosis Platform", "X-ray Analysis"],
      "availability": "available"
    }
  ],
  "message": "Based on your requirements for Python expertise in healthcare..."
}
```

#### GET /employees/search
Direct employee search with query parameters.

**Parameters:**
- `skill`: Filter by specific skill
- `min_experience`: Minimum years of experience
- `availability`: Filter by availability status
- `q`: General keyword search

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
- **Database Integration**: Replace JSON with PostgreSQL for better performance
- **Caching**: Add Redis for query caching and session management
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

## Demo

### Sample Queries
1. "Find React developers with mobile experience"
2. "Who has worked on healthcare projects?"
3. "Suggest someone for a machine learning role"
4. "Find AWS experts available immediately"

### Screenshots
- Chat Interface: Clean, intuitive Streamlit UI
- API Documentation: Automatic FastAPI docs with interactive testing
- Search Results: Structured employee profiles with skills and experience

## Development Notes
- Built in 2 days following rapid prototyping principles
- Focused on core functionality over UI polish
- Designed for easy extension and modification
- Emphasizes practical HR use cases and realistic data

## License
MIT License - Open for educational and commercial use.