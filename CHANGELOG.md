# Changelog

All notable changes to the HR Query Chatbot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-09

### 🚀 Added
- **Gemini 2.5 Flash Integration**: Switched from OpenAI to Google Gemini for improved performance
- **Native Gemini Embeddings**: Enhanced semantic search with `gemini-embedding-001`
- **Multi-AI Client Support**: Fallback system supporting both Gemini and OpenAI
- **Enhanced RAG System**: Context-aware retrieval with improved candidate matching
- **Confidence Scoring**: AI-calculated confidence levels for each match
- **Detailed Match Reasoning**: Explains why candidates fit requirements
- **Comprehensive Health Monitoring**: System status endpoints with detailed diagnostics
- **Rate Limiting**: Configurable API rate limits for production use
- **Security Enhancements**: Input validation, XSS protection, and secure error handling

### 🔧 Changed
- **Primary AI Model**: Now uses `gemini-2.5-flash` for faster, more efficient responses
- **Token Management**: Optimized token limits for different model types
- **Error Handling**: Improved fallback mechanisms and error reporting
- **Response Format**: Enhanced candidate information with scores and reasoning

### 🛠️ Technical Improvements
- **Async Architecture**: Full async support throughout the backend
- **Modular Design**: Separated AI client management from core logic
- **Comprehensive Testing**: Added extensive test suite with multiple scenarios
- **Documentation**: Complete API documentation and developer guides

### 🐛 Fixed
- **Token Limit Issues**: Resolved MAX_TOKENS errors with dynamic token allocation
- **Response Generation**: Fixed AI generation failures with better fallback handling
- **Search Accuracy**: Improved semantic matching with native embeddings

## [1.0.0] - 2024-12-01

### 🚀 Initial Release
- **Basic HR Query System**: Natural language employee search
- **OpenAI Integration**: GPT-3.5-turbo for response generation
- **FastAPI Backend**: RESTful API with automatic documentation
- **Streamlit Frontend**: Interactive chat interface
- **Employee Database**: Structured JSON employee profiles
- **Keyword Search**: Basic skill and experience filtering

### 📁 Core Features
- `/chat` endpoint for conversational queries
- `/employees/search` for direct filtering
- Basic employee matching algorithm
- Simple web interface

---

## Version History

- **v2.1.0** - Current: Gemini AI integration with enhanced features
- **v1.0.0** - Initial: Basic OpenAI-powered HR chatbot

## Upcoming Features

### 🔮 Planned for v2.2.0
- Database integration (PostgreSQL/MongoDB)
- User authentication and role management
- Advanced analytics and reporting
- Bulk candidate import/export
- Custom scoring algorithms

### 🌟 Future Considerations
- Mobile app development
- Integration with HR management systems
- Real-time notifications
- Multi-language support
- Voice interface capabilities

---

For detailed technical changes, see individual commit messages and pull requests.
