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


# ============================================================
# SIDEBAR: STUDENT PROFILE CONFIGURATION
# ============================================================
st.sidebar.header("Student Profile")

# Choose how to create the student profile
profile_creation_method = st.sidebar.radio(
    "Student Profile Method",
    ["Select Predefined", "Create Simple Profile", "Build from Description"],
    index=0
)

student_profile = None

# OPTION 1: Select from predefined student profile templates
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
        # Use the create_student_profile function directly from student_profiles.py
        student_profile = create_student_profile(
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

# OPTION 2: Create a custom student profile with direct inputs
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
        # Create a custom StudentProfile directly
        template = STUDENT_TEMPLATES.get("active_learner")
        student_profile = StudentProfile(
            name=student_name,
            grade_level=grade_level,
            personality_traits=personality_traits,
            learning_style=learning_style,
            interests=interests,
            typical_moods=[Mood.HAPPY, Mood.EXCITED],  # Default moods
            behavioral_patterns=template["behavioral_patterns"] if template else {},
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            social_dynamics=template["social_dynamics"] if template else {},
            support_strategies=support_strategies
        )
        st.sidebar.success(f"Custom profile for {student_name} created!")

# OPTION 3: Build a student profile from a text description
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
        # Use AI to generate a student profile from the text description
        builder = StudentProfileBuilder()
        student_profile = builder.build_profile_from_text(prompt)
        st.sidebar.success(
            f"Built profile for {student_profile.name} from description")

# ============================================================
# SIDEBAR: SCENARIO CONFIGURATION
# ============================================================
st.sidebar.header("Scenario")

scenario_method = st.sidebar.radio(
    "Scenario Method",
    ["Generate Random", "Create Custom"],
    index=0
)

scenario = None

# OPTION 1: Generate a random classroom scenario
if scenario_method == "Generate Random":
    if st.sidebar.button("Generate Random Scenario"):
        # Use the scenario generator to create a random scenario
        scenario = generate_random_scenario()
        st.sidebar.success(f"Generated scenario: {scenario.title}")
        st.sidebar.markdown(
            f"**Description:** {scenario.description[:100]}...")

# OPTION 2: Create a custom classroom scenario
else:  # Create Custom
    grade_level_options = {level.name: level for level in GradeLevel}
    selected_grade = st.sidebar.selectbox(
        "Grade Level",
        list(grade_level_options.keys()),
        index=0
    )
    grade_level = grade_level_options[selected_grade]

    subject_options = {subj.name: subj for subj in SubjectMatter}
    selected_subject = st.sidebar.selectbox(
        "Subject",
        list(subject_options.keys()),
        index=0
    )
    subject = subject_options[selected_subject]

    challenge_options = {chall.name: chall for chall in ChallengeType}
    selected_challenge = st.sidebar.selectbox(
        "Challenge Type",
        list(challenge_options.keys()),
        index=0
    )
    challenge_type = challenge_options[selected_challenge]

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
        scenario = scenario_gen.generate_scenario(
            grade_level=grade_level,
            subject=subject,
            challenge_type=challenge_type,
            student_background=student_background,
            classroom_context=classroom_context
        )
        st.session_state.scenario = scenario
        st.sidebar.success("Scenario created successfully!")
        st.sidebar.markdown(
            f"**Title:** {scenario.title}\n\n**Description:** {scenario.description[:100]}...")

# ============================================================
# CHAT HISTORY MANAGEMENT
# ============================================================
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# View and clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()

# ============================================================
# SIDEBAR: ADDITIONAL CONFIGURATION
# ============================================================
st.sidebar.header("Configuration")
# Checkbox to show retrieved documents context
show_context = st.sidebar.checkbox("Show Retrieved Documents", value=False)

# ============================================================
# SESSION STATE MANAGEMENT
# ============================================================
# Custom session state for tracking conversations
if "student_profile" not in st.session_state:
    st.session_state.student_profile = None

if "scenario" not in st.session_state:
    st.session_state.scenario = None

# Update session state with current selections
if student_profile:
    st.session_state.student_profile = student_profile

if scenario:
    st.session_state.scenario = scenario

# ============================================================
# DISPLAY CURRENT PROFILE AND SCENARIO
# ============================================================
# Create two columns for displaying current profile and scenario
col1, col2 = st.columns(2)

# Display current student profile information
with col1:
    st.subheader("Current Student Profile")
    if st.session_state.student_profile:
        profile = st.session_state.student_profile
        
        # Handle both dictionary and object types
        if hasattr(profile, 'get'):  # It's a dictionary
            profile_name = profile.get('name', 'Unknown')
            grade_level = profile.get('grade_level', 'Unknown')
            learning_style = profile.get('learning_style', 'Unknown')
            personality_traits = profile.get('personality_traits', [])
            interests = profile.get('interests', [])
            academic_strengths = profile.get('academic_strengths', 'Unknown')
            academic_challenges = profile.get('academic_challenges', 'Unknown')
        else:  # It's an object
            profile_name = getattr(profile, 'name', 'Unknown')
            grade_level = getattr(profile, 'grade_level', 'Unknown')
            learning_style = getattr(profile, 'learning_style', 'Unknown')
            personality_traits = getattr(profile, 'personality_traits', [])
            interests = getattr(profile, 'interests', [])
            academic_strengths = getattr(profile, 'academic_strengths', 'Unknown')
            academic_challenges = getattr(profile, 'academic_challenges', 'Unknown')
        
        st.success(f"Active Profile: {profile_name}")
        
        with st.expander("Profile Details", expanded=True):
            st.markdown(f"**Name:** {profile_name}")
            st.markdown(f"**Grade Level:** {grade_level}")
            st.markdown(f"**Learning Style:** {learning_style}")
            
            # Display personality traits if available
            if personality_traits:
                traits = ", ".join(personality_traits) if isinstance(personality_traits, list) else personality_traits
                st.markdown(f"**Personality:** {traits}")
            
            # Display interests if available
            if interests:
                # Handle both string and Interest enum types
                interest_values = []
                for interest in interests:
                    if hasattr(interest, 'value'):  # It's an enum
                        interest_values.append(interest.value)
                    else:
                        interest_values.append(str(interest))
                
                interests_str = ", ".join(interest_values)
                st.markdown(f"**Interests:** {interests_str}")
            
            # Display academic information
            st.markdown(f"**Academic Strengths:** {academic_strengths}")
            st.markdown(f"**Academic Challenges:** {academic_challenges}")
    else:
        st.warning("No student profile selected. Please create or select a profile.")

# Display current scenario information
with col2:
    st.subheader("Current Scenario")
    if st.session_state.scenario:
        scenario = st.session_state.scenario
        
        # Handle both dictionary and object types
        if hasattr(scenario, 'get'):  # It's a dictionary
            title = scenario.get('title', 'Unknown')
            description = scenario.get('description', 'No description available')
            grade_level = scenario.get('grade_level', 'Unknown')
            subject = scenario.get('subject', 'Unknown')
            challenge_type = scenario.get('challenge_type', 'Unknown')
        else:  # It's an object
            title = getattr(scenario, 'title', 'Unknown')
            description = getattr(scenario, 'description', 'No description available')
            
            # Handle enum values
            grade_level_obj = getattr(scenario, 'grade_level', None)
            grade_level = getattr(grade_level_obj, 'value', str(grade_level_obj)) if grade_level_obj else 'Unknown'
            
            subject_obj = getattr(scenario, 'subject', None)
            subject = getattr(subject_obj, 'value', str(subject_obj)) if subject_obj else 'Unknown'
            
            challenge_obj = getattr(scenario, 'challenge_type', None)
            challenge_type = getattr(challenge_obj, 'value', str(challenge_obj)) if challenge_obj else 'Unknown'
        
        st.success(f"Active Scenario: {title}")
        
        with st.expander("Scenario Details", expanded=True):
            st.markdown(f"**Title:** {title}")
            
            # Display description with a character limit
            if len(description) > 150:
                st.markdown(f"**Description:** {description[:150]}...")

            else:
                st.markdown(f"**Description:** {description}")
            
            # Display other scenario details
            st.markdown(f"**Grade Level:** {grade_level}")
            st.markdown(f"**Subject:** {subject}")
            st.markdown(f"**Challenge Type:** {challenge_type}")
    else:
        st.warning("No scenario selected. Please create or select a scenario.")

# ============================================================
# CHAT INTERFACE
# ============================================================
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
            # Prompt user to create a profile if none exists
            message_placeholder.markdown(
                "Please create or select a student profile before starting the conversation.")
        else:
            # Display warning if no scenario is selected
            if st.session_state.scenario is None:
                st.warning(
                    "No scenario selected. A random scenario will be generated automatically.")

            # Create initial state with profile and scenario
            state = create_multi_agent_state(
                messages=[HumanMessage(content=prompt)],
                student_profile=st.session_state.student_profile,
                scenario=st.session_state.scenario
            )
            
            # Process through multi-agent system
            agent = create_multi_agent_pipeline()
            result = agent.invoke(
                state,
                config={"configurable": {"thread_id": 43}}
            )

            # Check for notifications from the agent
            if result.get("notification"):
                st.info(result["notification"])
                
                # If a scenario was generated, update the session state
                if result.get("scenario") and st.session_state.scenario is None:
                    st.session_state.scenario = result["scenario"]
                    # Force a rerun to update the UI with the new scenario
                    st.experimental_rerun()
                    
                # If a profile was generated, update the session state
                if result.get("student_profile") and st.session_state.student_profile is None:
                    st.session_state.student_profile = result["student_profile"]
                    # Force a rerun to update the UI with the new profile
                    st.experimental_rerun()

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

# ============================================================
# DISPLAY RETRIEVED DOCUMENTS (OPTIONAL)
# ============================================================
# Add expander with retrieved documents (if checkbox is selected)
if show_context and st.session_state.messages and len(st.session_state.messages) > 0:
    with st.expander("Retrieved Documents"):
        if prompt:
            # Get the context documents using the embedding generator
            db = EmbeddingGenerator().return_chroma()
            results = db.similarity_search_with_score(prompt, k=5)

            for i, (doc, score) in enumerate(results):
                st.markdown(
                    f"**Document {i+1}** (Relevance: {score:.2f})")
                st.markdown(doc.page_content)
                st.markdown("---")
