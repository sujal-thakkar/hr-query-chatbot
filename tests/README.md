# Tests Directory

This directory contains all test files, debug scripts, and development utilities for the HR Query Chatbot project.

## Test Files

### Core Testing
- `test_security.py` - Security feature tests (rate limiting, validation, etc.)
- `test_gemini_implementation.py` - Gemini API integration tests
- `test_enhanced_system.py` - Enhanced RAG system tests
- `test_api.py` - API endpoint tests
- `test_search.py` - Search functionality tests

### AI & Generation Testing
- `test_ai_generation.py` - Direct AI client generation testing with detailed error analysis
- `test_simple_ai.py` - Simple AI generation tests with minimal prompts
- `check_ai_client.py` - AI client initialization and configuration verification
- `test_detailed_flow.py` - Complete API flow testing with detailed health checks

### Debug & Development
- `debug_gemini.py` - Debug script for Gemini response structure
- `direct_api_test.py` - Direct Gemini API testing without wrappers
- `simple_test.py` - Basic functionality tests

### Utilities
- `api_client.py` - Robust API client with retry mechanisms (used by tests)

## Running Tests

### Core System Tests
```bash
cd tests
python test_enhanced_system.py  # Complete system functionality
python test_api.py              # API endpoint testing
python test_search.py           # Search functionality
```

### AI & Gemini Tests
```bash
cd tests
python test_gemini_implementation.py  # Gemini API integration
python test_ai_generation.py          # AI generation with error details
python test_simple_ai.py              # Basic AI generation test
python check_ai_client.py             # AI client configuration check
```

### Security Tests
```bash
cd tests
python test_security.py  # Rate limiting and validation
```

### Debug & Development
```bash
cd tests
python test_detailed_flow.py    # Full API flow with health checks
python debug_gemini.py          # Gemini response debugging
python direct_api_test.py       # Direct API testing
python simple_test.py           # Basic functionality
```

## Test Categories

### 🔧 **Configuration & Setup Tests**
- `check_ai_client.py` - Verifies AI client setup and environment variables
- Health check endpoints via `test_detailed_flow.py`

### 🤖 **AI Generation Tests**
- `test_ai_generation.py` - Comprehensive AI generation testing with error handling
- `test_simple_ai.py` - Basic AI response generation
- `test_gemini_implementation.py` - Gemini-specific API integration

### 🔍 **Search & RAG Tests**
- `test_search.py` - Search functionality and relevance
- `test_enhanced_system.py` - Complete RAG system testing
- RAG status endpoint via `test_detailed_flow.py`

### 🛡️ **Security & Performance Tests**
- `test_security.py` - Rate limiting, input validation, XSS prevention
- API endpoint security via `test_api.py`

### 🐛 **Debug & Troubleshooting**
- `debug_gemini.py` - Gemini response structure analysis
- `direct_api_test.py` - Raw API testing without application layers
- `test_detailed_flow.py` - End-to-end flow analysis with detailed logging

## Prerequisites

### Required Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here  # Required for AI features
OPENAI_API_KEY=your_openai_key_here      # Optional fallback
```

### Setup
1. Ensure the backend server is running: `python backend/main.py`
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Set environment variables in `.env` file at project root

### Dependencies
- `requests` - For API testing
- `google-genai` - For Gemini API integration
- `python-dotenv` - For environment variable management
- Backend dependencies as listed in `backend/requirements.txt`

## Testing Strategy

### 🚀 **Quick Health Check**
```bash
python test_detailed_flow.py  # Comprehensive system status
```

### 🔍 **AI Generation Debugging**
If AI responses aren't working:
1. `python check_ai_client.py` - Verify AI client setup
2. `python test_simple_ai.py` - Test basic generation
3. `python test_ai_generation.py` - Detailed error analysis

### 🛠️ **Development Workflow**
1. Run `test_api.py` after backend changes
2. Run `test_enhanced_system.py` after RAG modifications
3. Run `test_security.py` before production deployment

## Notes

- **Network Connectivity**: Some tests require internet access for Gemini API calls
- **Server Dependency**: Most API tests require the backend server to be running
- **Token Limits**: AI generation tests may hit token limits with complex prompts
- **Rate Limiting**: Security tests will trigger rate limits intentionally
- **Environment**: Tests load environment variables from project root `.env` file

## Troubleshooting

### Common Issues
- **"AI client not available"**: Check `GEMINI_API_KEY` in environment
- **"Connection refused"**: Ensure backend server is running on port 8000
- **"MAX_TOKENS" errors**: Use `test_simple_ai.py` to verify basic functionality
- **Rate limit errors**: Expected behavior for security tests

### Debug Commands
```bash
python check_ai_client.py           # Check AI setup
python test_detailed_flow.py        # Full system status
python test_simple_ai.py           # Basic AI test
```
