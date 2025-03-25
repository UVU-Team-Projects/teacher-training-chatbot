import streamlit as st
import components.main_menu as main_menu

def main():
    if "teacher_title" not in st.session_state:
        st.session_state.teacher_title = "Teacher"
        st.session_state.teacher_philosophy = ""

    st.title("Teacher Dashboard")
    st.header(f"Welcome {st.session_state.teacher_title}", divider="rainbow")    
    
    # Display the main menu
    main_menu.display()