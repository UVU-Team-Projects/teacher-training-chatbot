import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import warnings
import os

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

# Initialize all session state variables
def init_session_state():
    """Initialize all session state variables used throughout the application"""
    
    # --- Routing variables ---
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "create_chat_page" not in st.session_state:
        st.session_state.create_chat_page = "student"
    
    # --- Student and scenario selection ---
    if "selected_student" not in st.session_state:
        st.session_state.selected_student = None
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = None
    if "students" not in st.session_state:
        st.session_state.students = []
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = []
    
    # --- Chatbot variables ---
    # Student chatbot
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = None
    if 'conversation_active' not in st.session_state:
        st.session_state.conversation_active = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'evaluation_complete' not in st.session_state:
        st.session_state.evaluation_complete = False
    
    # AI chatbot
    if "ai_chatbot" not in st.session_state:
        st.session_state.ai_chatbot = None
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    
    # --- Teacher profile ---
    if "teacher_profile" not in st.session_state:
        st.session_state.teacher_profile = {}
    
    # --- Form submission flags ---
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

# Call the initialization function
init_session_state()

# Import views after session state initialization to avoid issues
import views.home as home
import views.chat as chat
import views.create_chat as create_chat
import views.teaching_assistant as teaching_assistant
import views.teacher_profile as teacher_profile
import views.scenarios as scenarios

# Use the current page value from session state
match st.session_state.page:
    case "home":
        home.main()
    case "chat":
        chat.chat()
    case "create_chat":
        create_chat.main()
    case "teaching_assistant":
        teaching_assistant.main()
    case "teacher_profile":
        teacher_profile.main()
    case "scenarios":
        scenarios.main()
    case _:
        "Error: Page not found"
