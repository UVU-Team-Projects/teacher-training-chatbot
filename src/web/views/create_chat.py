import streamlit as st
import src.web.views.teacher_profile as teacher_profile
import components.student_selection as student_selection
import components.scenario_selection as scenario_selection

def main():
    match st.session_state.create_chat_page:
        case "student":
            student_selection.main()
        case "scenario":
            scenario_selection.main()