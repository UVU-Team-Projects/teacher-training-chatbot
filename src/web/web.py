import streamlit as st
import views.home as home
import views.chat as chat
import views.create_chat as create_chat
import views.teaching_assistant as teaching_assistant
import views.teacher_profile as teacher_profile
import views.scenarios as scenarios

# Routing - only initialize if not already set
if "page" not in st.session_state:
    st.session_state.page = "home"
if "create_chat_page" not in st.session_state:
    st.session_state.create_chat_page = "student"

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
