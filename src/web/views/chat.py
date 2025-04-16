import streamlit as st
import components.chatbox as chatbox
import components.ai_chatbox as ai_assistant
import components.chat_settings as chat_settings
import components.documents as documents

def do_home_button():
    st.session_state.page = "home"

def chat():
    chatbox.main()

    with st.sidebar:
        st.button("Home", on_click=do_home_button)
        # Initialize selected tab if not already in session state
        if "chat_selected_tab" not in st.session_state:
            st.session_state.chat_selected_tab = "AI Assistant"
        
        # Create the selectbox for navigation
        chat_selected_tab = st.selectbox(
            "Chat Toolbox",
            ("AI Assistant", "Knowledge Base", "Chat Settings")
        )
        
        # Save the selected tab in session state
        st.session_state.chat_selected_tab = chat_selected_tab
        
        # Display the appropriate component based on the selected tab
        if chat_selected_tab == "AI Assistant":
            pass
            # ai_assistant.main()
        elif chat_selected_tab == "Knowledge Base":
            # Placeholder for Knowledge Base component
            pass
            #documents.main()
        elif chat_selected_tab == "Chat Settings":
            chat_settings.main()