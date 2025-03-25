import streamlit as st

def save_teacher_profile():
    """Save teacher profile and continue to create chat page"""
    # Store teacher profile in session state

    # Navigate to create chat page
    st.session_state.page = "home"

def main():
    st.title("Teacher Profile")
    st.write("Please provide some information about yourself as a teacher.")
    
    # Initialize session state variables if they don't exist
    if "teacher_title" not in st.session_state:
        st.session_state.teacher_title = ""
    if "teacher_philosophy" not in st.session_state:
        st.session_state.teacher_philosophy = ""
    
    # Form for teacher details
    with st.form("teacher_profile_form"):
        # Title field
        st.text_input(
            "How would you like to be addressed?", 
            key="teacher_title",
            placeholder="Mr., Mrs., Dr., Professor, etc."
        )
        
        # Philosophy text area
        st.text_area(
            "Your teaching beliefs and philosophy", 
            key="teacher_philosophy",
            height=200,
            placeholder="Share your approach to teaching, classroom management philosophy, and educational beliefs..."
        )
        
        # Submit button
        st.form_submit_button("Continue", on_click=save_teacher_profile)
    