# frontend/app.py
import streamlit as st
import requests
import os
import time
import re
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="HR Resource Query Chatbot", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI with FontAwesome icons
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stForm {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .candidate-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .match-score {
        background-color: #e8f5e8;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        font-weight: bold;
        color: #2d5a2d;
    }
    .availability-available {
        color: #28a745;
        font-weight: bold;
    }
    .availability-available i {
        margin-right: 5px;
    }
    .availability-notice {
        color: #ffc107;
        font-weight: bold;
    }
    .availability-notice i {
        margin-right: 5px;
    }
    .availability-busy {
        color: #dc3545;
        font-weight: bold;
    }
    .availability-busy i {
        margin-right: 5px;
    }
    .error-container {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-container {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .search-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }
    .search-section h3 {
        color: white;
        margin-bottom: 1rem;
    }
    .results-section {
        scroll-margin-top: 20px;
    }
    
    /* Professional Icon Styles */
    .icon-professional {
        margin-right: 8px;
        font-size: 1.1em;
    }
    .icon-search {
        color: #2563eb;
        margin-right: 8px;
    }
    .icon-settings {
        color: #6b7280;
        margin-right: 8px;
    }
    .icon-examples {
        color: #059669;
        margin-right: 8px;
    }
    .icon-history {
        color: #7c3aed;
        margin-right: 8px;
    }
    .icon-clear {
        color: #dc2626;
        margin-right: 8px;
    }
    .icon-refresh {
        color: #0891b2;
        margin-right: 8px;
    }
    .icon-status {
        color: #065f46;
        margin-right: 8px;
    }
    .btn-icon {
        display: inline-flex;
        align-items: center;
    }
    
    /* Custom button styling for icons */
    .stButton > button {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Fix for form submit buttons */
    .stForm .stButton > button {
        width: 100%;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Get API base URL
API_BASE = os.getenv("API_BASE", "https://hr-query-chatbot-bdg8.onrender.com/")

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_search_time' not in st.session_state:
    st.session_state.last_search_time = 0
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'scroll_to_results' not in st.session_state:
    st.session_state.scroll_to_results = False

def validate_query(query: str) -> tuple[bool, str]:
    """Validate the search query"""
    if not query.strip():
        return False, "Please enter a search query"
    
    if len(query.strip()) < 3:
        return False, "Query must be at least 3 characters long"
    
    if len(query) > 500:
        return False, "Query is too long (max 500 characters)"
    
    # Check for potentially problematic patterns
    if re.match(r'^[^a-zA-Z]*$', query):
        return False, "Query must contain at least some letters"
    
    return True, ""

def format_availability(availability: str) -> str:
    """Format availability with appropriate styling"""
    if availability == 'available':
        return f'<span class="availability-available"><i class="fas fa-check-circle"></i> Available</span>'
    elif availability == 'on_notice':
        return f'<span class="availability-notice"><i class="fas fa-clock"></i> On Notice</span>'
    else:
        return f'<span class="availability-busy"><i class="fas fa-times-circle"></i> Busy</span>'

def display_candidate_card(candidate: Dict[str, Any], index: int, is_last: bool = False):
    """Display a candidate card with enhanced formatting"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {index}. {candidate['name']}")
            
        with col2:
            if 'final_score' in candidate:
                score = candidate['final_score']
                st.markdown(f'<div class="match-score">Score: {score:.2f}</div>', 
                          unsafe_allow_html=True)
        
        # Main candidate information
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown(f"**Skills:** {', '.join(candidate['skills'])}")
            st.markdown(f"**Experience:** {candidate['experience_years']} years")
            
        with info_col2:
            st.markdown(f"**Projects:** {', '.join(candidate['projects'])}")
            st.markdown(f"**Availability:** {format_availability(candidate['availability'])}", 
                       unsafe_allow_html=True)
        
        # Additional information if available
        if 'similarity_score' in candidate:
            st.caption(f"Semantic similarity: {candidate['similarity_score']:.3f}")
        
        if 'skill_match_count' in candidate:
            st.caption(f"Skill matches: {candidate['skill_match_count']}")
        
        # Only add separator if not the last candidate
        if not is_last:
            st.markdown("---")

def add_to_search_history(query: str, result_count: int):
    """Add search to history"""
    history_entry = {
        'query': query,
        'timestamp': time.time(),
        'result_count': result_count
    }
    st.session_state.search_history.insert(0, history_entry)
    # Keep only last 10 searches
    st.session_state.search_history = st.session_state.search_history[:10]

# Sidebar for additional features
with st.sidebar:
    st.markdown('<h4><i class="fas fa-cog icon-settings"></i>Search Settings</h4>', unsafe_allow_html=True)
    
    # Advanced search options
    top_k = st.slider("Max candidates to show", 1, 15, 5, 
                     help="Maximum number of candidates to display")
    
    include_busy = st.checkbox("Include busy candidates", value=True,
                              help="Whether to include candidates marked as busy")
    
    min_experience = st.number_input("Minimum experience (years)", 
                                   min_value=0, max_value=20, value=0,
                                   help="Filter candidates by minimum years of experience")
    
    st.markdown('<h4><i class="fas fa-code icon-examples"></i>Search Examples</h4>', unsafe_allow_html=True)
    example_queries = [
        "Senior Python developer with healthcare experience",
        "Machine learning engineer for fintech project",
        "React developer with 3+ years experience",
        "Data scientist with NLP and medical background",
        "Full-stack developer for e-commerce platform"
    ]
    
    for example in example_queries:
        if st.button(example, key=f"example_{example[:20]}"):
            st.session_state.example_query = example
    
    # Search history
    if st.session_state.search_history:
        st.markdown('<h4><i class="fas fa-history icon-history"></i>Recent Searches</h4>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.search_history[:5]):
            if st.button(f"{entry['query'][:30]}... ({entry['result_count']} results)", 
                        key=f"history_{i}"):
                st.session_state.example_query = entry['query']

# Main content
st.markdown('<h1 class="main-header">🤖 HR Resource Query Chatbot</h1>', 
           unsafe_allow_html=True)

# Main search input (prominent)
st.markdown('<h3><i class="fas fa-search icon-search"></i>Search for Candidates</h3>', unsafe_allow_html=True)
st.markdown("Use natural language to describe the ideal candidate for your role")

# Get query from session state if set by example/history
default_query = st.session_state.get('example_query', "")

# Add a flag to track if we should clear the input
if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False

# If we need to clear input, override default_query
if st.session_state.clear_input:
    default_query = ""
    st.session_state.clear_input = False

# Create search form
with st.form("search_form", clear_on_submit=False):
    query = st.text_area(
        "Search Query Input",
        value=default_query,
        height=120,
        placeholder="e.g., Senior React developer with fintech experience and 5+ years background",
        help="Be specific about skills, experience level, domain expertise, and any other requirements",
        label_visibility="collapsed",
        key="search_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_button = st.form_submit_button("🔍 Search Candidates", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.form_submit_button("🗑️ Clear", use_container_width=True)
    
    with col3:
        # Rate limiting check
        time_since_last = time.time() - st.session_state.last_search_time
        if time_since_last < 2 and not clear_button:
            st.warning(f"Wait {2-time_since_last:.1f}s")
            search_button = False

# Quick example buttons
st.markdown("**💡 Quick Examples:**")
example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    if st.button("🐍 Python Developer", use_container_width=True, key="python_btn"):
        st.session_state.example_query = "Find Python developers with 3+ years experience in healthcare"
        st.rerun()

with example_col2:
    if st.button("⚛️ React Developer", use_container_width=True, key="react_btn"):
        st.session_state.example_query = "Senior React developer with fintech experience and 5+ years background"
        st.rerun()

with example_col3:
    if st.button("🤖 ML Engineer", use_container_width=True):
        st.session_state.example_query = "Machine learning engineer with NLP experience for healthcare projects"
        st.rerun()

st.markdown("---")

# Handle clear button
if clear_button:
    # Clear example query from session state
    if 'example_query' in st.session_state:
        del st.session_state.example_query
    # Reset show_results flag
    st.session_state.show_results = False
    st.session_state.scroll_to_results = False
    # Set flag to clear input field
    st.session_state.clear_input = True
    st.rerun()

# Search logic
if search_button:
    # Clear example query from session state after successful search
    if 'example_query' in st.session_state:
        del st.session_state.example_query
    
    # Set flag to show results section and trigger scroll
    st.session_state.show_results = True
    st.session_state.scroll_to_results = True
        
    # Validate query
    is_valid, error_message = validate_query(query)
    if not is_valid:
        st.error(f"❌ **Invalid Query:** {error_message}")
        # Don't clear example_query on error so user can fix it
        st.stop()
    
    # Rate limiting
    st.session_state.last_search_time = time.time()
    
    with st.spinner("Searching for candidates..."):
        try:
            # Test backend connection first with timeout
            health_resp = requests.get(f"{API_BASE}/health", timeout=5)
            if health_resp.status_code != 200:
                st.error("❌ **Backend server is not responding.** Please make sure it's running.")
                st.code("cd backend && python main.py", language="bash")
                st.stop()
            
            # Apply filters to query if needed
            enhanced_query = query
            if min_experience > 0:
                enhanced_query += f" with minimum {min_experience} years experience"
            
            # Make the search request with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    resp = requests.post(
                        f"{API_BASE}/chat", 
                        json={"query": enhanced_query, "top_k": top_k}, 
                        timeout=30
                    )
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        st.warning(f"⏱️ Request timeout, retrying... (attempt {attempt + 2})")
                        time.sleep(1)
                    else:
                        raise
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Filter candidates based on settings
                candidates = data.get("candidates", [])
                if not include_busy:
                    candidates = [c for c in candidates if c['availability'] != 'busy']
                
                if min_experience > 0:
                    candidates = [c for c in candidates if c['experience_years'] >= min_experience]
                
                # Add to search history
                add_to_search_history(query, len(candidates))
                
                # Display results
                if candidates:
                    st.success(f"✅ **Found {len(candidates)} matching candidate(s)!**")
                    
                    # Clear the input field for next search
                    st.session_state.clear_input = True
                    
                    # Add results marker for auto-scroll
                    st.markdown('<div id="results-marker"></div>', unsafe_allow_html=True)
                    
                    # Display assistant response if available
                    if data.get("message"):
                        st.markdown("### 🤖 AI Recommendation")
                        st.info(data["message"])
                    
                    # Display candidates
                    st.markdown("### 👥 Candidate Results")
                    
                    for i, candidate in enumerate(candidates, 1):
                        is_last = (i == len(candidates))
                        display_candidate_card(candidate, i, is_last)
                        
                else:
                    st.warning("⚠️ **No candidates found matching your criteria.**")
                    st.markdown("""
                    **Suggestions:**
                    - Try broader search terms
                    - Reduce experience requirements
                    - Include busy candidates
                    - Check spelling and terminology
                    """)
                    
            else:
                st.error(f"❌ **Backend Error:** {resp.status_code}")
                with st.expander("Error Details"):
                    st.code(resp.text)
                    
        except requests.exceptions.ConnectionError:
            st.markdown('<div class="error-container">', unsafe_allow_html=True)
            st.error("❌ **Backend Connection Failed**")
            st.markdown("""
            **Troubleshooting Steps:**
            1. Make sure the backend server is running
            2. Check if the API URL is correct
            3. Verify there are no firewall issues
            
            **To start the backend:**
            """)
            st.code("cd backend && python main.py", language="bash")
            st.markdown('</div>', unsafe_allow_html=True)
            
        except requests.exceptions.Timeout:
            st.error("⏱️ **Request Timeout**")
            st.markdown("The search is taking too long. This might indicate:")
            st.markdown("- Backend server is overloaded")
            st.markdown("- Complex query requiring more processing time")
            st.markdown("- Network connectivity issues")
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ **Request Error:** {str(e)}")
            
        except Exception as e:
            st.error(f"❌ **Unexpected Error:** {str(e)}")
            with st.expander("Debug Information"):
                st.code(f"Error type: {type(e).__name__}")
                st.code(f"Error details: {str(e)}")

# Results section - with auto-scroll functionality
if st.session_state.show_results:
    # Add scroll trigger when results are shown
    if st.session_state.scroll_to_results:
        # Use HTML/JS for immediate scroll after content loads
        st.markdown("""
        <script>
            // Multiple attempts to scroll with different timing
            function scrollToResults() {
                const marker = document.getElementById('results-marker');
                if (marker) {
                    marker.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    return true;
                }
                return false;
            }
            
            // Try multiple times with increasing delays
            setTimeout(scrollToResults, 100);
            setTimeout(scrollToResults, 500);
            setTimeout(scrollToResults, 1000);
            
            // Also try after document is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', scrollToResults);
            } else {
                scrollToResults();
            }
        </script>
        """, unsafe_allow_html=True)
        # Reset scroll flag
        st.session_state.scroll_to_results = False

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🚀 Powered by OpenAI | Gemini + RAG**")
with col2:
    if st.button("🔄 Refresh Page"):
        st.rerun()
with col3:
    st.markdown(f"**API Status:** {API_BASE}")
