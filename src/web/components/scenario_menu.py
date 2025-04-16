import streamlit as st

def open_chat():
    st.session_state.selected_student = None
    st.session_state.page = "chat"

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
        st.button("Scenario 1", on_click=open_chat, key="menu_scenarios")
        st.button("Scenario 2", on_click=open_chat, key="menu_chat")
        st.button("Scenario 3", on_click=open_chat, key="menu_assistant")
        st.button("👤Scenario 4", on_click=open_chat, key="menu_profile")