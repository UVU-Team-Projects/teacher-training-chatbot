import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Rest of your imports
import streamlit as st
import json
from datetime import datetime
from utils.storage import save_chats, load_chats
from pages import create_chat, chat

# Must be the first Streamlit command
st.set_page_config(
    page_title="Teacher Training Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation and chat storage
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'chats' not in st.session_state:
    st.session_state.chats = load_chats()

# Custom CSS for dark mode and styling
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --primary-color: #1e88e5;
        --primary-dark: #1565c0;
        --background-color: #121212;
        --container-bg: #1e1e1e;
        --text-color: #e0e0e0;
    }

    /* Main container styling */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        text-align: center;
    }

    /* Center all text elements */
    .stMarkdown, .stText, div[data-testid="stVerticalBlock"] {
        text-align: center !important;
    }

    /* Center title and headers */
    h1, h2, h3, .centered-title {
        text-align: center !important;
        width: 100%;
        margin-bottom: 2rem;
        padding-top: 2rem;
    }

    /* Chat list container */
    .chat-list {
        max-width: 800px;
        margin: 20px auto;
        padding: 15px;
        border-radius: 8px;
        background-color: var(--container-bg);
    }

    /* Chat item styling */
    .chat-item {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        margin: 5px auto;
        border-radius: 4px;
        background-color: var(--chat-item-bg);
        max-width: 700px;
    }

    /* Button styling */
    .stButton {
        display: flex;
        justify-content: center;
    }

    .stButton > button {
        max-width: 300px;
        margin: 0 auto;
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 4px;
        transition: background-color 0.2s;
    }

    /* Column alignment */
    [data-testid="column"] {
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Write element alignment */
    .element-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

def display_home_page():
    st.title("Teacher Training Chatbot")
    
# Create new chat button at the top with center alignment
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create New Chat", use_container_width=True):
            st.session_state.page = 'create_chat'
            st.rerun()
    
    # Display saved chats if any exist
    if st.session_state.chats:
        st.subheader("Saved Chats")
        for chat_session in st.session_state.chats:
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                st.write(f"Student: {chat_session['student']}")
            with col2:
                st.write(f"Scenario: {chat_session['scenario']}")
            with col3:
                st.write(f"Created: {datetime.fromisoformat(chat_session['created_at']).strftime('%Y-%m-%d')}")
            with col4:
                if st.button("Continue", key=f"continue_{chat_session['id']}", use_container_width=True):
                    st.session_state.current_chat = chat_session
                    st.session_state.page = 'chat'
                    st.rerun()

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'chats' not in st.session_state:
        st.session_state.chats = []

    # Add CSS
    st.markdown("""
    <style>
        .chat-list {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background-color: var(--container-bg);
        }
        .chat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            background-color: var(--chat-item-bg);
        }
        .chat-item:hover {
            background-color: var(--chat-item-hover-bg);
        }
        .main-button {
            width: 100%;
            margin: 10px 0;
            padding: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Page routing
    if st.session_state.page == 'home':
        display_home_page()
    elif st.session_state.page == 'create_chat':
        create_chat.create_chat_page()
    elif st.session_state.page == 'chat':
        chat.chat_page()

if __name__ == "__main__":
    main()