from pages import create_chat, chat
import streamlit as st
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add the project root directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


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
# if 'chats' not in st.session_state:
#     st.session_state.chats = load_chats() TODO: Fix this

# Load CSS from file
with open(os.path.join(current_dir, "assets", "styles.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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
                st.write(
                    f"Created: {datetime.fromisoformat(chat_session['created_at']).strftime('%Y-%m-%d')}")
            with col4:
                if st.button("Continue", key=f"continue_{chat_session['id']}", use_container_width=True):
                    st.session_state.current_chat = chat_session
                    st.session_state.page = 'chat'
                    st.rerun()


def main():
    # Page routing
    if st.session_state.page == 'home':
        display_home_page()
    elif st.session_state.page == 'create_chat':
        create_chat.create_chat_page()
    elif st.session_state.page == 'chat':
        chat.chat_page()


if __name__ == "__main__":
    main()
