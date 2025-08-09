# Contributing to HR Query Chatbot

Thank you for your interest in contributing to the HR Query Chatbot project! We welcome contributions from everyone.

## How to Contribute

### 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Relevant logs or error messages

### 💡 Suggesting Features

1. Check existing [Issues](../../issues) and [Discussions](../../discussions)
2. Create a new issue with:
   - Clear feature description
   - Use case and benefits
   - Possible implementation approach

### 🔧 Code Contributions

#### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/hr-query-chatbot.git
   cd hr-query-chatbot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run Tests**
   ```bash
   cd tests
   python test_enhanced_system.py
   ```

#### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run all tests
   cd tests
   python test_enhanced_system.py
   python test_security.py
   python test_gemini_implementation.py
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use clear title and description
   - Reference related issues
   - Include testing information

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings for functions and classes
- Keep functions focused and small

### API Design
- Use descriptive endpoint names
- Include proper error handling
- Add input validation
- Document with clear examples

### Testing
- Write tests for new features
- Maintain test coverage
- Use descriptive test names
- Test both success and error cases

## Project Structure

```
hr-query-chatbot/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── ai_client.py        # AI client management
│   ├── gemini_rag.py       # Gemini-based RAG system
│   └── requirements.txt    # Backend dependencies
├── frontend/               # Streamlit frontend
│   └── app.py             # Frontend application
├── tests/                  # Test files
├── dataset/               # Employee data
└── docs/                  # Documentation (if added)
```

## Development Areas

### 🎯 High Priority
- Enhanced search algorithms
- Additional AI model support
- Performance optimizations
- Security improvements

### 🔄 Medium Priority
- UI/UX improvements
- Additional data sources
- Caching mechanisms
- Monitoring and logging

### 🌟 Nice to Have
- Database integration
- Authentication system
- API rate limiting improvements
- Mobile-responsive design

## Getting Help

- **Questions**: Open a [Discussion](../../discussions)
- **Issues**: Create an [Issue](../../issues)
- **Real-time**: Check project documentation

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.
