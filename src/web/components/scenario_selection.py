import streamlit as st
import src.data.database.crud as db
from src.ai.scenario_generator import Scenario, ScenarioGenerator, GradeLevel, SubjectMatter, ChallengeType, StudentBackground, ClassroomContext

def do_back_button():
    st.session_state.create_chat_page = "student"

def select_scenario(scenario):
    # Store the selected scenario in session state
    st.session_state.selected_scenario = {
        "title": scenario.title,
        "description": scenario.description,
        "grade_level": scenario.grade_level.value if hasattr(scenario.grade_level, 'value') else scenario.grade_level,
        "subject": scenario.subject.value if hasattr(scenario.subject, 'value') else scenario.subject,
        "challenge_type": scenario.challenge_type.value if hasattr(scenario.challenge_type, 'value') else scenario.challenge_type,
        "id": scenario.id if hasattr(scenario, 'id') else None,
        "instruction": scenario.instruction if hasattr(scenario, 'instruction') else None
    }
    
    # Change page to chat
    st.session_state.page = "chat"
    
    # Display success message
    st.success(f"Selected scenario: {scenario.title}")

def load_scenarios():
    st.session_state.scenarios = []
    # Get scenarios from database
    scenarios = db.get_all_scenarios()
    
    for scenario_data in scenarios:
        try:
            # Create a simplified Scenario object with only the fields that exist in the database
            scenario = Scenario(
                title=scenario_data.title,
                description=scenario_data.description,
                # Use default/empty values for fields that don't exist in the database
                grade_level=None,
                subject=None,
                challenge_type=None,
                student_background=StudentBackground(
                    age=10,
                    grade=5,
                    learning_style="visual",
                    special_needs=[],
                    cultural_background="",
                    language_background=""
                ),
                classroom_context=ClassroomContext(
                    class_size=25,
                    time_of_day="morning",
                    class_duration=45,
                    previous_activities=[],
                    classroom_setup="Traditional rows",
                    available_resources=[]
                ),
                key_considerations=[],
                evidence_based_strategies=[],
                research_sources=[]
            )
            
            # Store the database ID and instruction in the object
            if hasattr(scenario_data, 'id'):
                scenario.id = scenario_data.id
            if hasattr(scenario_data, 'instruction'):
                scenario.instruction = scenario_data.instruction
                
            st.session_state.scenarios.append(scenario)
            
        except Exception as e:
            print(f"Error processing scenario: {e}")
            import traceback
            traceback.print_exc()
            continue

def create_scenario_form():
    # Create the form to add a new scenario
    with st.expander("**Create New Scenario**"):
        with st.form(key="new_scenario_form", clear_on_submit=True):
            # Required fields
            title = st.text_input("Title*", help="Required")
            description = st.text_area("Description*", height=150, help="Required")
            
            # Grade level and subject
            col1, col2 = st.columns(2)
            with col1:
                grade_level = st.selectbox(
                    "Grade Level*",
                    options=[g.value for g in GradeLevel],
                    format_func=lambda x: x.replace("_", " ").title(),
                    help="Required"
                )
            with col2:
                subject = st.selectbox(
                    "Subject*",
                    options=[s.value for s in SubjectMatter],
                    format_func=lambda x: x.replace("_", " ").title(),
                    help="Required"
                )
                
            challenge_type = st.selectbox(
                "Challenge Type*",
                options=[c.value for c in ChallengeType],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Required"
            )
            
            # Student Background
            st.subheader("Student Background")
            sb_col1, sb_col2 = st.columns(2)
            with sb_col1:
                student_age = st.number_input("Age", min_value=5, max_value=22, value=10)
                student_grade = st.number_input("Grade", min_value=1, max_value=12, value=5)
                learning_style = st.selectbox(
                    "Learning Style",
                    options=["visual", "auditory", "kinesthetic", "reading/writing"],
                    format_func=lambda x: x.title()
                )
            with sb_col2:
                special_needs = st.text_input("Special Needs (comma-separated)")
                cultural_background = st.text_input("Cultural Background")
                language_background = st.text_input("Language Background")
            
            # Classroom Context
            st.subheader("Classroom Context")
            cc_col1, cc_col2 = st.columns(2)
            with cc_col1:
                class_size = st.number_input("Class Size", min_value=1, max_value=50, value=25)
                time_of_day = st.selectbox(
                    "Time of Day",
                    options=["morning", "afternoon", "evening"],
                    format_func=lambda x: x.title()
                )
                class_duration = st.number_input("Class Duration (minutes)", min_value=30, max_value=120, value=45)
            with cc_col2:
                previous_activities = st.text_input("Previous Activities (comma-separated)")
                classroom_setup = st.selectbox(
                    "Classroom Setup",
                    options=["Traditional rows", "Group tables", "U-shaped", "Circle"]
                )
                available_resources = st.text_input("Available Resources (comma-separated)")
            
            # Additional info
            st.subheader("Additional Information")
            key_considerations = st.text_area("Key Considerations (one per line)", height=80)
            evidence_based_strategies = st.text_area("Evidence-Based Strategies (one per line)", height=80)
            research_sources = st.text_area("Research Sources (one per line)", height=80)
            
            submitted = st.form_submit_button("Create Scenario")
            
            if submitted:
                if not title or not description or not grade_level or not subject or not challenge_type:
                    st.error("All required fields must be filled.")
                    return
                
                # Process inputs
                spec_needs_list = [sn.strip() for sn in special_needs.split(",")] if special_needs else []
                prev_act_list = [pa.strip() for pa in previous_activities.split(",")] if previous_activities else []
                avail_res_list = [ar.strip() for ar in available_resources.split(",")] if available_resources else []
                key_cons_list = [kc.strip() for kc in key_considerations.split("\n")] if key_considerations else []
                strategies_list = [s.strip() for s in evidence_based_strategies.split("\n")] if evidence_based_strategies else []
                sources_list = [s.strip() for s in research_sources.split("\n")] if research_sources else []
                
                # Create the necessary objects for the full Scenario structure
                student_bg = StudentBackground(
                    age=student_age,
                    grade=student_grade,
                    learning_style=learning_style,
                    special_needs=spec_needs_list,
                    cultural_background=cultural_background,
                    language_background=language_background
                )
                
                classroom_ctx = ClassroomContext(
                    class_size=class_size,
                    time_of_day=time_of_day,
                    class_duration=class_duration,
                    previous_activities=prev_act_list,
                    classroom_setup=classroom_setup,
                    available_resources=avail_res_list
                )
                
                # Generate an instruction based on scenario details
                instruction = f"""This scenario involves a {grade_level.replace('_', ' ')} {subject.replace('_', ' ')} class 
                with a {challenge_type.replace('_', ' ')} challenge. The student is {student_age} years old in grade {student_grade} 
                with a {learning_style} learning style. The class has {class_size} students and lasts {class_duration} minutes."""
                
                # Create in database (supports only title, description, instruction)
                success = db.create_scenario(
                    title=title,
                    description=description,
                    instruction=instruction
                )
                
                if success:
                    st.success(f"Scenario '{title}' created!")
                    st.rerun()
                else:
                    st.error(f"Failed to create scenario '{title}'.")

def delete_scenario(scenario):
    # Delete the scenario from the database
    db.delete_scenario(scenario.id if hasattr(scenario, 'id') else None)
    st.rerun()

def generate_ai_scenario():
    with st.spinner("Generating scenario with AI..."):
        try:
            scenario_generator = ScenarioGenerator()
            scenario = scenario_generator.generate_random_scenario()
            
            # Save the generated scenario to the database
            success = db.create_scenario(
                title=scenario.title,
                description=scenario.description,
                grade_level=scenario.grade_level.value,
                subject=scenario.subject.value,
                challenge_type=scenario.challenge_type.value,
                student_age=scenario.student_background.age,
                student_grade=scenario.student_background.grade,
                learning_style=scenario.student_background.learning_style,
                special_needs=scenario.student_background.special_needs,
                cultural_background=scenario.student_background.cultural_background,
                language_background=scenario.student_background.language_background,
                class_size=scenario.classroom_context.class_size,
                time_of_day=scenario.classroom_context.time_of_day,
                class_duration=scenario.classroom_context.class_duration,
                previous_activities=scenario.classroom_context.previous_activities,
                classroom_setup=scenario.classroom_context.classroom_setup,
                available_resources=scenario.classroom_context.available_resources,
                key_considerations=scenario.key_considerations,
                evidence_based_strategies=scenario.evidence_based_strategies,
                research_sources=scenario.research_sources
            )
            
            if success:
                st.success("AI scenario generated successfully!")
                st.rerun()
            else:
                st.error("Failed to save AI-generated scenario.")
        except Exception as e:
            st.error(f"Error generating scenario: {e}")
            import traceback
            traceback.print_exc()

def main():
    title, back = st.columns([9,1], vertical_alignment="bottom")
    with title:
        st.header("Scenarios", divider="rainbow")
    with back:
        st.button("Back", on_click=do_back_button, key='scenario-back', use_container_width=True)

    # Load scenarios
    load_scenarios()
    
    # Display scenarios
    with st.container(border=True, height=400):
        if not st.session_state.scenarios:
            st.info("No scenarios available. Create a new scenario below.")
        else:
            for scenario in st.session_state.scenarios:
                with st.expander(scenario.title):
                    st.write(scenario.description)
                    
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Grade Level:** " + (scenario.grade_level.value.replace("_", " ").title() if hasattr(scenario.grade_level, 'value') else str(scenario.grade_level)))
                            st.write("**Subject:** " + (scenario.subject.value.replace("_", " ").title() if hasattr(scenario.subject, 'value') else str(scenario.subject)))
                        with col2:
                            st.write("**Challenge:** " + (scenario.challenge_type.value.replace("_", " ").title() if hasattr(scenario.challenge_type, 'value') else str(scenario.challenge_type)))
                    
                    select_button, _, delete_button = st.columns([1,4,1])
                    select_button.button("Select", 
                            on_click=select_scenario, 
                            args=(scenario,), 
                            key=f"select_scenario_{id(scenario)}")
                    delete_button.button("Delete",
                            on_click=delete_scenario,
                            args=(scenario,),
                            key=f"delete_scenario_{id(scenario)}")
    
    create_scenario_form()

