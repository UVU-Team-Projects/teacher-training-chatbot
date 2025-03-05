import os
import sys
import time
from typing import List, Dict, Any, Optional
import streamlit as st
from langchain_core.messages import HumanMessage
from ai.embedding import EmbeddingGenerator
from ai.student_profiles import StudentProfile, STUDENT_TEMPLATES, create_student_profile, Interest, Mood
from ai.profile_builder import StudentProfileBuilder
from ai.scenario_generator import GradeLevel, SubjectMatter, ChallengeType, StudentBackground, ClassroomContext, Scenario, ScenarioGenerator, generate_random_scenario
from ai.MultiAgent_pipeline import (
    create_multi_agent_pipeline,
    create_multi_agent_state,
    student_profile_to_dict,
    scenario_to_dict,
    create_profile_for_streamlit,
    create_scenario_for_streamlit
)

# Add the project root directory to the path so we can import modules correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Set page configuration
st.set_page_config(
    page_title="Teacher Training ChatBot",
    page_icon="🧠",
    layout="wide"
)


def load_css():
    """Load custom CSS for better UI appearance."""
    css = """
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage p {
        font-size: 1.1rem;
        line-height: 1.5;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Load custom CSS
try:
    load_css()
except Exception as e:
    st.warning(f"Could not load CSS: {e}")

# App title and description
st.title("Teacher Training Chatbot")
st.markdown("""
This application simulates student interactions for teacher training. Select or create a student profile, 
choose a classroom scenario, and practice your teaching and classroom management skills with the AI student.
""")


# Student Profile Configuration
st.sidebar.header("Student Profile")

profile_creation_method = st.sidebar.radio(
    "Student Profile Method",
    ["Select Predefined", "Create Simple Profile", "Build from Description"],
    index=0
)

student_profile = None

if profile_creation_method == "Select Predefined":
    # Allow user to select from predefined profiles
    template_options = list(STUDENT_TEMPLATES.keys())
    selected_template = st.sidebar.selectbox(
        "Select Student Template",
        template_options,
        index=0
    )

    # Basic customization of the selected template
    student_name = st.sidebar.text_input("Student Name", value="Alex")
    grade_level = st.sidebar.slider(
        "Grade Level", min_value=1, max_value=12, value=2)

    # Create a profile from the template with minimal custom fields
    if st.sidebar.button("Use This Profile"):
        # Use the new helper function from MultiAgent_pipeline.py
        student_profile = create_profile_for_streamlit(
            profile_type="template",
            template_name=selected_template,
            name=student_name,
            grade_level=grade_level,
            interests=[Interest.SCIENCE, Interest.SPORTS],
            academic_strengths=["math", "science"],
            academic_challenges=["reading", "writing"],
            support_strategies=["visual aids", "frequent breaks"]
        )
        st.sidebar.success(
            f"Using {student_name}, a {selected_template} profile")

elif profile_creation_method == "Create Simple Profile":
    # Allow user to create a simple profile with direct inputs
    student_name = st.sidebar.text_input("Student Name", value="Jamie")
    grade_level = st.sidebar.slider(
        "Grade Level", min_value=1, max_value=12, value=2)

    # Use multiselect for multiple choices
    personality_traits = st.sidebar.multiselect(
        "Personality Traits",
        ["energetic", "shy", "curious", "reserved",
            "creative", "analytical", "emotional", "logical"],
        default=["curious", "energetic"]
    )

    learning_style = st.sidebar.selectbox(
        "Learning Style",
        ["visual", "auditory", "kinesthetic", "reading/writing", "multimodal"],
        index=0
    )

    # Interest selection
    interest_options = [interest.value for interest in Interest]
    selected_interests = st.sidebar.multiselect(
        "Interests",
        interest_options,
        default=["science", "sports"]
    )
    interests = [Interest(interest) for interest in selected_interests]

    # Academic information
    academic_strengths = st.sidebar.text_input(
        "Academic Strengths (comma-separated)",
        value="math, science experiments"
    ).split(',')
    academic_strengths = [s.strip() for s in academic_strengths]

    academic_challenges = st.sidebar.text_input(
        "Academic Challenges (comma-separated)",
        value="reading, sitting still"
    ).split(',')
    academic_challenges = [c.strip() for c in academic_challenges]

    support_strategies = st.sidebar.text_input(
        "Support Strategies (comma-separated)",
        value="visual aids, movement breaks"
    ).split(',')
    support_strategies = [s.strip() for s in support_strategies]

    # Create custom profile
    if st.sidebar.button("Create Profile"):
        # Use the new helper function from MultiAgent_pipeline.py
        student_profile = create_profile_for_streamlit(
            profile_type="custom",
            template_base="active_learner",
            name=student_name,
            grade_level=grade_level,
            personality_traits=personality_traits,
            learning_style=learning_style,
            interests=interests,
            typical_moods=[Mood.HAPPY, Mood.EXCITED],  # Default moods
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            support_strategies=support_strategies
        )
        st.sidebar.success(f"Custom profile for {student_name} created!")

elif profile_creation_method == "Build from Description":
    # Use the existing profile builder from description
    prompt = st.sidebar.text_area(
        "Describe the student in detail",
        value="""Sarah is a bright but sometimes anxious 2nd grader who loves science experiments and reading about nature.
She's usually focused in the morning but gets tired and distracted in the afternoon.
She works well in small groups but can be hesitant to speak up in larger class discussions.
Sarah excels at math but struggles with writing long passages.
She benefits from visual aids and frequent positive reinforcement."""
    )
    if st.sidebar.button("Build Profile"):
        builder = StudentProfileBuilder()
        student_profile = builder.build_profile_from_text(prompt)
        st.sidebar.success(
            f"Built profile for {student_profile.name} from description")

# Scenario configuration
st.sidebar.header("Scenario")

scenario_method = st.sidebar.radio(
    "Scenario Method",
    ["Generate Random", "Create Custom"],
    index=0
)

scenario = None

if scenario_method == "Generate Random":
    if st.sidebar.button("Generate Random Scenario"):
        scenario = generate_random_scenario()
        st.sidebar.success(f"Generated scenario: {scenario.title}")
        st.sidebar.markdown(
            f"**Description:** {scenario.description[:100]}...")

else:  # Create Custom
    grade_level = st.sidebar.selectbox(
        "Grade Level",
        [level.value for level in GradeLevel],
        index=0
    )

    subject = st.sidebar.selectbox(
        "Subject",
        [subj.value for subj in SubjectMatter],
        index=0
    )

    challenge_type = st.sidebar.selectbox(
        "Challenge Type",
        [chall.value for chall in ChallengeType],
        index=0
    )

    # Simplified student background and classroom context
    age = st.sidebar.slider("Student Age", min_value=5, max_value=18, value=8)
    class_size = st.sidebar.slider(
        "Class Size", min_value=5, max_value=35, value=20)
    time_of_day = st.sidebar.selectbox(
        "Time of Day",
        ["Morning", "Afternoon", "After Lunch"],
        index=0
    )

    if st.sidebar.button("Create Scenario"):
        # Create minimal versions of required objects
        student_background = StudentBackground(
            age=age,
            grade=int(age-5),  # Approximate grade from age
            learning_style="visual",
        )

        classroom_context = ClassroomContext(
            class_size=class_size,
            time_of_day=time_of_day,
            class_duration=45,
            previous_activities=["reading", "math"],
            classroom_setup="traditional desks",
            available_resources=["whiteboard", "computers"]
        )

        # Initialize scenario generator
        scenario_gen = ScenarioGenerator()

        # Generate scenario with chosen parameters
        if st.sidebar.button("Generate Scenario"):
            with st.sidebar:
                # Use the new helper function from MultiAgent_pipeline.py
                scenario = create_scenario_for_streamlit(
                    scenario_type="custom",
                    grade=grade_level,
                    subject=subject,
                    challenge_type=challenge_type,
                    student_background=student_background,
                    classroom_context=classroom_context
                )
                st.session_state.scenario = scenario
                st.success("Scenario created successfully!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# View and clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()

# Sidebar configuration
st.sidebar.header("Configuration")
# Checkbox to show retrieved documents context
show_context = st.sidebar.checkbox("Show Retrieved Documents", value=False)

# Custom session state for tracking conversations
if "student_profile" not in st.session_state:
    st.session_state.student_profile = None

if "scenario" not in st.session_state:
    st.session_state.scenario = None

# Update session state with current selections
if student_profile:
    st.session_state.student_profile = student_profile

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display chat input
if prompt := st.chat_input("Your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display all messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Generate bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Use the multi-agent system with student profile and scenario
        if st.session_state.student_profile is None:
            message_placeholder.markdown(
                "Please create or select a student profile before starting the conversation.")
        else:
            # Create initial state with profile and scenario
            # Only set generate_missing=True if you want to auto-generate missing components
            state = create_multi_agent_state(
                messages=[HumanMessage(content=prompt)],
                student_profile=st.session_state.student_profile,
                scenario=st.session_state.scenario,
                generate_missing=False  # Don't auto-generate - respect Streamlit state
            )

            # Display warning if no scenario is selected
            if st.session_state.scenario is None:
                st.warning(
                    "No scenario selected. The student responses won't be scenario-specific. Please select or generate a scenario for a better experience.")

                # Add a button to generate a scenario now
                if st.button("Generate a scenario now"):
                    # Use our helper function to generate a random scenario
                    profile = st.session_state.student_profile
                    grade = profile.get("grade_level", "MIDDLE_SCHOOL")

                    scenario = create_scenario_for_streamlit(
                        scenario_type="random",
                        grade=grade
                    )

                    # Update the session state with the generated scenario
                    st.session_state.scenario = scenario
                    st.success(
                        f"Generated scenario: {scenario.get('title', 'New scenario')}")
                    st.experimental_rerun()  # Rerun to update the UI

            # Ensure the state is properly structured
            # Log for debugging
            print("State:", state)
            print("Scenario type:", type(state.get("scenario")))
            print("Student profile type:", type(state.get("student_profile")))

            # Process through multi-agent system
            agent = create_multi_agent_pipeline()
            result = agent.invoke(
                state,
                config={"configurable": {"thread_id": 43}}
            )

            # Extract the response
            if result["messages"] and len(result["messages"]) > 0:
                response_content = result["messages"][-1].content

                # Display feedback separately if available
                if result.get("feedback"):
                    response_content += "\n\n---\n\n**Teacher Feedback:**\n" + \
                        result["feedback"]
            else:
                response_content = "No response generated. Please try again."

            # Update the UI
            message_placeholder.markdown(response_content)

            # Add assistant message to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": response_content})

# Add expander with retrieved documents (if checkbox is selected)
if show_context and st.session_state.messages and len(st.session_state.messages) > 0:
    with st.expander("Retrieved Documents"):
        if prompt:
            # Get the context documents
            db = EmbeddingGenerator().return_chroma()
            results = db.similarity_search_with_score(prompt, k=5)

            for i, (doc, score) in enumerate(results):
                st.markdown(
                    f"**Document {i+1}** (Relevance: {score:.2f})")
                st.markdown(doc.page_content)
                st.markdown("---")
