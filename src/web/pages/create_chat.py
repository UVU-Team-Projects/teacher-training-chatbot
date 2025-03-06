import streamlit as st
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.data.database import crud

@dataclass
class Student:
    id: int
    name: str
    traits: List[str]
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    motivations: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    communication_style: Optional[str] = None

@dataclass
class Scenario:
    id: int
    title: str
    description: str

def safe_convert_to_list(value):
    """Convert a value to a list safely"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    return []

def convert_student_profile(db_student):
    """Convert database student to our Student dataclass"""
    return Student(
        id=db_student.id,
        name=db_student.name,
        traits=safe_convert_to_list(db_student.traits),
        strengths=safe_convert_to_list(db_student.strengths),
        weaknesses=safe_convert_to_list(db_student.weaknesses),
        motivations=safe_convert_to_list(db_student.motivations),
        fears=safe_convert_to_list(db_student.fears),
        communication_style=db_student.communication_style if db_student.communication_style else None
    )

def convert_scenario(db_scenario):
    """Convert SQLAlchemy Scenario to our Scenario dataclass"""
    return Scenario(
        id=db_scenario.id,
        title=db_scenario.title,
        description=db_scenario.description
    )

@st.cache_data(ttl=1)
def get_students() -> List[Student]:
    """Get all active students from the database"""
    try:
        students = crud.get_all_students()
        return [convert_student_profile(student) for student in students]
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return []

def get_scenarios() -> List[Scenario]:
    """Get all scenarios from the database"""
    try:
        db_scenarios = crud.get_all_scenarios()
        return [convert_scenario(scenario) for scenario in db_scenarios]
    except Exception as e:
        st.error(f"Error loading scenarios: {e}")
        return []

def create_new_student(data: dict) -> bool:
    print("Create new student called") #Debug
    """Create a new student profile and add it to the database"""
    try:
        # Convert comma-separated strings into lists using safe_convert_to_list
        name = data['name']
        traits = safe_convert_to_list(data['traits'])
        strengths = safe_convert_to_list(data['strengths'])
        weaknesses = safe_convert_to_list(data['weaknesses'])
        motivations = safe_convert_to_list(data.get('motivations', ''))
        fears = safe_convert_to_list(data.get('fears', ''))
        communication_style = data.get('communication_style', '')
        
        # Call the CRUD function with the proper parameters
        created_student = crud.create_student(
            name,
            traits,
            strengths,
            weaknesses,
            motivations,
            fears,
            communication_style
        )
        if created_student is not None:
            # Print all students after successful creation
            print("\nCurrent students in database:")
            for student in crud.get_all_students():
                print(f"\nStudent ID: {student.id}")
                print(f"Name: {student.name}")
                print(f"Traits: {', '.join(student.traits)}")
                print(f"Strengths: {', '.join(student.strengths) if student.strengths else 'None'}")
                print(f"Weaknesses: {', '.join(student.weaknesses) if student.weaknesses else 'None'}")
                print(f"Motivations: {', '.join(student.motivations) if student.motivations else 'None'}")
                print(f"Fears: {', '.join(student.fears) if student.fears else 'None'}")
                print(f"Communication Style: {student.communication_style}")
                print("-" * 50)
            return True
        else:
            st.error("Error: Student was not created.")
            return False
    except Exception as e:
        st.error(f"Error creating student: {e}")
        return False

def create_new_scenario(title: str, description: str) -> bool:
    """Create a new scenario and add it to the database"""
    print("Create new scenario called") #Debug
    try:
        # Call the CRUD function with the correct parameters
        created_scenario = crud.create_scenario(title, description)
        if created_scenario is not None:
            # Print all scenarios after successful creation
            print("\nCurrent scenarios in database:")
            for scenario in crud.get_all_scenarios():
                print(f"\nScenario ID: {scenario.id}")
                print(f"Title: {scenario.title}")
                print(f"Description: {scenario.description}")
                print("-" * 50)
            return True
        else:
            st.error("Error: Scenario was not created.")
            return False
    except Exception as e:
        st.error(f"Error creating scenario: {e}")
        return False

def create_chat_page():
    """Main page for creating a new chat session"""
    if 'create_chat_step' not in st.session_state:
        st.session_state.create_chat_step = 'student'

    # Add CSS for the cards
    st.markdown("""
    <style>
        .selection-card {
            background-color: var(--container-bg);
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem;
            border: 1px solid var(--primary-color);
            transition: transform 0.2s;
        }
        
        .selection-card:hover {
            transform: translateY(-4px);
        }
        
        .create-new-card {
            border: 2px dashed var(--primary-color);
            background-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.create_chat_step == 'student':
        display_student_selection()
    else:
        display_scenario_selection()

def display_student_selection():
    """Display the student selection grid"""
    st.title("Select a Student")
    
    cols = st.columns(4)
    
    # Create New Student card
    with cols[0]:
        create_new_student_card()
    
    # Display existing students
    students = get_students()
    for idx, student in enumerate(students):
        with cols[(idx + 1) % 4]:
            display_student_card(student)

def display_scenario_selection():
    """Display the scenario selection grid"""
    st.title("Select a Scenario")
    
    if st.button("← Back to Students"):
        st.session_state.create_chat_step = 'student'
        st.rerun()
    
    cols = st.columns(4)
    
    # Create New Scenario card
    with cols[0]:
        create_new_scenario_card()
    
    # Display existing scenarios
    scenarios = get_scenarios()
    for idx, scenario in enumerate(scenarios):
        with cols[(idx + 1) % 4]:
            display_scenario_card(scenario)

def create_new_student_card():
    """Display and handle the Create New Student card"""
    st.markdown("""
        <div class='selection-card create-new-card'>
            <h3>Create New Student</h3>
            <p>Add a new student profile</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Create Student", key="new_student"):
        st.session_state["show_form"] = True
    
    # Move form outside the button condition
    if st.session_state.get("show_form", False):
        with st.form("new_student_form", clear_on_submit=True):
            print("Showing form") # Debug print
            name = st.text_input("Student Name")
            traits = st.text_input("Traits (comma-separated)")
            strengths = st.text_input("Strengths (comma-separated)")
            weaknesses = st.text_input("Weaknesses (comma-separated)")
            motivations = st.text_input("Motivations (comma-separated)")
            fears = st.text_input("Fears (comma-separated)")
            communication_style = st.text_area("Communication Style")
            
            submitted = st.form_submit_button("Create")
            print(f"Form submitted: {submitted}") # Debug print
            
            if submitted and name:
                print(f"Processing submission for {name}") # Debug print
                success = create_new_student({
                    'name': name,
                    'traits': traits,
                    'strengths': strengths,
                    'weaknesses': weaknesses,
                    'motivations': motivations,
                    'fears': fears,
                    'communication_style': communication_style
                })
                
                if success:            
                    print(submitted, name)

                    st.success("Student created successfully!")
                    st.session_state["show_form"] = False  # Hide form after success
                    st.cache_data.clear()
                    st.rerun()

def display_student_card(student: Student):
    """Display a student card"""
    st.markdown(f"""
        <div class='selection-card'>
            <h3>{student.name}</h3>
            <p>Traits: {', '.join(student.traits)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Select", key=f"student_{student.id}"):
        st.session_state.selected_student = student
        st.session_state.create_chat_step = 'scenario'
        st.rerun()

def create_new_scenario_card():
    """Display and handle the Create New Scenario card"""
    st.markdown("""
        <div class='selection-card create-new-card'>
            <h3>Create New Scenario</h3>
            <p>Add a new training scenario</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Create Scenario", key="new_scenario"):
        st.session_state["show_scenario_form"] = True
    
    # Move form outside the button condition
    if st.session_state.get("show_scenario_form", False):
        with st.form("new_scenario_form", clear_on_submit=True):
            print("Showing scenario form") # Debug print
            title = st.text_input("Scenario Title")
            description = st.text_area("Scenario Description")
            
            submitted = st.form_submit_button("Create")
            print(f"Form submitted: {submitted}") # Debug print
            
            if submitted and title and description:
                print(f"Processing submission for scenario: {title}") # Debug print
                if create_new_scenario(title, description):
                    st.success("Scenario created successfully!")
                    st.session_state["show_scenario_form"] = False  # Hide form after success
                    st.cache_data.clear()
                    st.rerun()

def display_scenario_card(scenario: Scenario):
    """Display a scenario card"""
    st.markdown(f"""
        <div class='selection-card'>
            <h3>{scenario.title}</h3>
            <p>{scenario.description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Select", key=f"scenario_{scenario.id}"):
        # Initialize new chat session
        st.session_state.current_chat = {
            'id': str(datetime.now().timestamp()),  # Unique ID
            'student': st.session_state.selected_student.name,
            'scenario': scenario.title,
            'student_data': st.session_state.selected_student.__dict__,
            'scenario_data': scenario.__dict__,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to saved chats
        if 'chats' not in st.session_state:
            st.session_state.chats = []
        st.session_state.chats.append(st.session_state.current_chat)
        
        # Transition to chat page
        st.session_state.page = 'chat'
        st.rerun()

def create_new_chat_session(student: Student, scenario: Scenario):
    """Create a new chat session and store it"""
    new_session = {
        "id": str(len(st.session_state.chats) + 1),
        "student": student.name,
        "scenario": scenario.title,
        "timestamp": datetime.now().isoformat(),
        "messages": []
    }
    st.session_state.chats.append(new_session)
    st.session_state.current_chat = new_session