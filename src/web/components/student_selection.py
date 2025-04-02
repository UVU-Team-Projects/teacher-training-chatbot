import streamlit as st
import src.data.database.crud as db
from src.ai.student_profiles import StudentProfile, create_student_profile  # Import the StudentProfile class

def do_home_button():
    st.session_state.page = "home"

def select_student(student):
    st.session_state.selected_student = student
    # Change page to scenario selection.
    st.session_state.create_chat_page = "scenario"

def load_students():
    st.session_state.students = []
    # Get students from database
    student_profiles = db.get_all_students()
    
    # StudentProfile objects are now used directly
    for profile in student_profiles:
        try:
            # We're already using StudentProfile objects, so just add them to the session state
            st.session_state.students.append(profile)
        except Exception as e:
            print(f"Error processing student profile: {e}")
            import traceback
            traceback.print_exc()
            continue

def create_student_form():
    # Create the form to add a new student
    with st.expander("**Create New Student**"):
        with st.form(key="new_student_form", clear_on_submit=True, enter_to_submit=False):
            # Required fields
            new_student_name = st.text_input("Name*", help="Required")
            traits = st.text_input("Traits* (comma-separated)", help="Required. Example: outgoing, curious, persistent")
            
            # Optional fields with appropriate input types
            st.subheader("Academic Profile")
            strengths = st.text_input("Strengths (comma-separated)", help="Example: math, reading, creativity")
            weaknesses = st.text_input("Weaknesses (comma-separated)", help="Example: organization, focus, writing")
            
            st.subheader("Psychological Profile")
            motivations = st.text_input("Motivations (comma-separated)", help="Example: recognition, mastery, social connection")
            fears = st.text_input("Fears (comma-separated)", help="Example: failure, embarrassment, rejection")
            
            st.subheader("Communication")
            communication_style = st.selectbox(
                "Communication Style",
                options=["", "Direct", "Reserved", "Enthusiastic", "Analytical", "Visual", "Verbal"],
                index=0
            )
            engagement_level = st.slider("Engagement Level", 1, 10, 5)
            
            submitted = st.form_submit_button("Create Student")
            
            # Check if form was submitted and required fields are not empty
            if submitted:
                if not new_student_name:
                    st.error("Name is required.")
                    return
                    
                if not traits:
                    st.error("At least one trait is required.")
                    return
                
                # Process trait input
                trait_list = [t.strip() for t in traits.split(",") if t.strip()]
                
                # Process optional inputs
                strength_list = [s.strip() for s in strengths.split(",") if s.strip()] if strengths else None
                weakness_list = [w.strip() for w in weaknesses.split(",") if w.strip()] if weaknesses else None
                motivation_list = [m.strip() for m in motivations.split(",") if m.strip()] if motivations else None
                fear_list = [f.strip() for f in fears.split(",") if f.strip()] if fears else None
                comm_style = communication_style if communication_style else None
                
                # Create student profile object
                student_profile = create_student_profile(
                    name=new_student_name,
                    grade_level=grade_level,
                    interests=interest_list,
                    academic_strengths=strength_list,
                    academic_challenges=weakness_list,
                    support_strategies=support_list
                )
                # Create student in database
                success = db.create_student(
                    name=new_student_name,
                    traits=trait_list,
                    strengths=strength_list,
                    weaknesses=weakness_list,
                    motivations=motivation_list,
                    fears=fear_list,
                    communication_style=comm_style
                )
                if success:
                    st.success(f"Student '{new_student_name}' created!")
                    st.rerun()
                else:
                    st.error(f"Failed to create student '{new_student_name}'.")

def delete_student(student):
    # Delete the student from the database
    db.delete_student(student.id)

#TODO: Create edit student functionality.
def edit_student(student):
    print("Edit student functionality not implemented yet.")

def main():
    title, back = st.columns([9,1], vertical_alignment="bottom")
    with title:
        st.header("Please select a student.", divider="rainbow")
    with back:
        st.button("Back", on_click=do_home_button, key='student-back', use_container_width=True)

    # Load students from database
    load_students()
    
    # Display students in a list of st.expander elements.
    with st.container(border=True, height=400):
        if not st.session_state.students:
            st.info("No students available. Create a new student below.")
        else:
            for student in st.session_state.students:
                with st.expander(student.name):
                    st.write(student.about)
                    select_button, edit_button, _, delete_button = st.columns([1,1,3,1])
                    select_button.button("Select", 
                            on_click=select_student, 
                            args=(student,), 
                            key=f"{student.id}_select_button")
                    edit_button.button("Edit",
                            on_click=edit_student,
                            args=(student,),
                            key=f"{student.id}_edit_button")
                    delete_button.button("Delete",
                            on_click=delete_student,
                            args=(student,),
                            key=f"{student.id}_delete_button")
    
    create_student_form()