import streamlit as st

def give_your_name():
    st.header("What is your name?", divider="rainbow")
    
    # Using a form to enable Enter key submission
    with st.form(key="name_form"):
        name = st.text_input("Your name")
        col1, col2 = st.columns([1, 5])
        with col1:
            # No back button on first screen
            st.write("")  
        with col2:
            submit_button = st.form_submit_button("Next")
        
        if submit_button:
            st.session_state.teacher_name = name
            st.session_state.teach_profile_step = 2

def select_teaching_approaches():
    st.header("Select your teaching approaches", divider="rainbow")
    
    # Using streamlit pills select the options that best fit
    options = [
        "Direct Instruction", 
        "Inquiry-Based Learning", 
        "Differentiated Instruction", 
        "Project-Based Learning", 
        "Flipped Classroom", 
        "Blended Learning",
        "Problem-Based Learning",
        "Mastery Learning",
        "Personalized Learning",
        "Experiential Learning",
        "Socratic Method",
        "Gamification",
        "Design Thinking",
        "Cooperative Learning",
        "Universal Design for Learning (UDL)"
    ]
    
    # Using a form to enable Enter key submission
    with st.form(key="approaches_form"):
        selected = st.pills("Select your teaching approaches", options, selection_mode="multi")
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            submit_button = st.form_submit_button("Next")
        
        if back_button:
            st.session_state.teach_profile_step = 1
        elif submit_button:
            st.session_state.teacher_teaching_approaches = selected
            st.session_state.teach_profile_step = 3

def select_classroom_management_philosophies():
    st.header("Select your classroom management philosophies", divider="rainbow")
    
    # Using streamlit pills select the options that best fit
    options = [
        "MTSS (Multi-Tiered System of Supports)",
        "Assertive Discipline", 
        "Positive Reinforcement", 
        "Democratic Classroom", 
        "Restorative Practices", 
        "PBIS (Positive Behavioral Interventions and Supports)", 
        "Love and Logic",
        "Culturally Responsive Management",
        "Trauma-Informed Teaching",
        "Responsive Classroom",
        "Conscious Discipline",
        "Choice Theory",
        "Non-Violent Communication"
    ]
    
    # Using a form to enable Enter key submission
    with st.form(key="philosophies_form"):
        selected = st.pills("Select your classroom management philosophies", options, selection_mode="multi")
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            submit_button = st.form_submit_button("Next")
        
        if back_button:
            st.session_state.teach_profile_step = 2
        elif submit_button:
            st.session_state.teacher_classroom_management_philosophies = selected
            st.session_state.teach_profile_step = 4

#TODO: Add more areas to ask
'''
How do you handle discipline?
How do you handle conflict?
How do you handle bullying?
How do you handle student engagement?
How do you handle parent engagement?
How do you handle student achievement?
'''

def select_grade_levels():
    st.header("Select your grade levels", divider="rainbow")
    
    # Using streamlit pills select the options that best fit
    options = [
        "Early Childhood (PreK)",
        "Primary (K-2)",
        "Elementary (3-5)",
        "Middle School (6-8)",
        "High School (9-12)",
        "Higher Education",
        "Adult Education",
        "Special Education"
    ]
    
    # Using a form to enable Enter key submission
    with st.form(key="grade_levels_form"):
        selected = st.pills("Select your grade levels", options, selection_mode="multi")
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            submit_button = st.form_submit_button("Next")
        
        if back_button:
            st.session_state.teach_profile_step = 3
        elif submit_button:
            st.session_state.teacher_grade_levels = selected
            st.session_state.teach_profile_step = 5

def add_additional_info():
    st.header("Any additional information about your teaching?", divider="rainbow")
    
    # Initialize additional info if not exists
    if "teacher_additional_info" not in st.session_state:
        st.session_state.teacher_additional_info = ""
    
    # Using a form to enable Enter key submission
    with st.form(key="additional_info_form"):
        additional_info = st.text_area(
            "Share anything else about your teaching approach, classroom management, or educational philosophy",
            value=st.session_state.teacher_additional_info,
            height=150
        )
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            submit_button = st.form_submit_button("Next")
        
        if back_button:
            st.session_state.teach_profile_step = 4
        elif submit_button:
            st.session_state.teacher_additional_info = additional_info
            st.session_state.teach_profile_step = 6

def display_teaching_profile():
    st.title("Teacher Profile")
    
    # Display the name, teaching approaches and classroom management philosophies
    st.write(f"Name: {st.session_state.teacher_name}")
    st.write(f"Teaching Approaches: {', '.join(st.session_state.teacher_teaching_approaches)}")
    st.write(f"Classroom Management Philosophies: {', '.join(st.session_state.teacher_classroom_management_philosophies)}")
    st.write(f"Grade Levels: {', '.join(st.session_state.teacher_grade_levels)}")
    
    # Display additional info if provided
    if st.session_state.teacher_additional_info:
        st.write(f"Additional Information: {st.session_state.teacher_additional_info}")
    
    # Using a form to enable Enter key submission
    with st.form(key="home_form"):
        submit_button = st.form_submit_button("Home")
        if submit_button:
            do_home_button()

def do_home_button():
    st.session_state.page = "home"

def main():
    if "teach_profile_step" not in st.session_state:
        st.session_state.teach_profile_step = 1

    if st.session_state.teach_profile_step == 1:
        give_your_name()
    elif st.session_state.teach_profile_step == 2:
        select_teaching_approaches()
    elif st.session_state.teach_profile_step == 3:
        select_classroom_management_philosophies()
    elif st.session_state.teach_profile_step == 4:
        select_grade_levels()
    elif st.session_state.teach_profile_step == 5:
        add_additional_info()
    elif st.session_state.teach_profile_step == 6:
        display_teaching_profile()
