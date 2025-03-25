import streamlit as st
import components.ai_chatbox as ai_chatbox

def do_home_button():
    st.session_state.page = "home"

def main():
    ai_chatbox.main()

    with st.sidebar:
        st.button("Home", on_click=do_home_button)