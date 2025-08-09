# Render.com deployment configuration
# Place this in the root of your repository

# For Backend Service:
# - Build Command: pip install -r backend/requirements.txt
# - Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
# - Environment: Python 3.11

# For Frontend Service:
# - Build Command: pip install -r frontend/requirements.txt  
# - Start Command: cd frontend && streamlit run app.py --server.port $PORT --server.address 0.0.0.0
# - Environment: Python 3.11

# Environment Variables needed:
# Backend:
# - GEMINI_API_KEY=your_gemini_api_key
# - OPENAI_API_KEY=your_openai_api_key (optional)

# Frontend:
# - API_BASE=https://your-backend-service-name.onrender.com
