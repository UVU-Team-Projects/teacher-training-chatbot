import streamlit as st

def go_to_create_chat():
    st.session_state.page = "create_chat"

def go_to_scenarios():
    st.session_state.page = "scenarios"

def go_to_teaching_assistant():
    st.session_state.page = "teaching_assistant"

def go_to_teacher_profile():
    st.session_state.page = "teacher_profile"

def display():
    # Custom CSS for buttons
    st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            height: 60px;
            margin: 10px 0px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the menu with columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.button("📚 Scenarios", on_click=go_to_scenarios, key="menu_scenarios")
        st.button("💬 Create a Chat", on_click=go_to_create_chat, key="menu_chat")
        st.button("🧠 Teaching Assistant", on_click=go_to_teaching_assistant, key="menu_assistant")
        st.button("👤 Teacher Profile", on_click=go_to_teacher_profile, key="menu_profile")