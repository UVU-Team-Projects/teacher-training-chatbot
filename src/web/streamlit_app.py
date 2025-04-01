import streamlit as st
import os
import sys
from typing import Dict, Any

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(src_dir)
sys.path.append(root_dir)

# Import the necessary modules
from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES
from src.ai.scenario_generator import generate_random_scenario
from src.logging import AgentLogger, LogLevel
from src.ai.standalone_agents import (
    initialize_conversation_manager,
    process_streamlit_message,
    continue_streamlit_conversation,
    ConversationManager
)

# Set up logging
AgentLogger.set_level(LogLevel.INFO)
logger = AgentLogger.get_logger("StreamlitApp")

# App title and description
st.set_page_config(
    page_title="Teacher Training Chatbot",
    page_icon="👨‍🏫",
    layout="wide"
)

st.title("Teacher Training Chatbot")
st.markdown(
    """
    Practice your teaching skills by interacting with a simulated student and receiving feedback.
    
    1. Configure the student profile and scenario on the sidebar
    2. Chat with the student
    3. End the conversation to receive evaluation
    4. Choose to continue or start a new conversation
    
    You can also use `kb:` followed by a query to search the knowledge base at any time.
    """
)

# Initialize session state variables
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = None
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'evaluation_complete' not in st.session_state:
    st.session_state.evaluation_complete = False
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'scenario' not in st.session_state:
    st.session_state.scenario = None

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Model selection
    model_name = st.selectbox(
        "Select AI Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo-16k"],
        index=0
    )
    
    st.subheader("Student Profile")
    
    # Profile template selection
    profile_template = st.selectbox(
        "Select Profile Template",
        list(STUDENT_TEMPLATES.keys()),
        index=0
    )
    
    # Student name
    student_name = st.text_input("Student Name", "Alex")
    
    # Grade level
    grade_level = st.slider("Grade Level", 1, 12, 4)
    
    # Interests (multi-select)
    interest_options = [interest.name for interest in Interest]
    selected_interests = st.multiselect(
        "Interests",
        interest_options,
        default=[Interest.SCIENCE.name, Interest.SPORTS.name]
    )
    
    # Academic strengths and challenges
    academic_strengths = st.text_input(
        "Academic Strengths (comma separated)",
        "math, science experiments"
    ).split(",")
    academic_strengths = [s.strip() for s in academic_strengths if s.strip()]
    
    academic_challenges = st.text_input(
        "Academic Challenges (comma separated)",
        "sitting still, writing long passages"
    ).split(",")
    academic_challenges = [s.strip() for s in academic_challenges if s.strip()]
    
    # Support strategies
    support_strategies = st.text_input(
        "Support Strategies (comma separated)",
        "movement breaks, visual aids"
    ).split(",")
    support_strategies = [s.strip() for s in support_strategies if s.strip()]
    
    st.subheader("Scenario")
    
    # Option to use a random scenario or custom
    scenario_type = st.radio(
        "Scenario Type",
        ["Random", "Custom"],
        index=0
    )
    
    if scenario_type == "Custom":
        scenario_title = st.text_input(
            "Scenario Title",
            "Math Class Disruption"
        )
        
        scenario_description = st.text_area(
            "Scenario Description",
            "During a math lesson on fractions, a student is having trouble focusing and starts distracting others around them. The teacher needs to address this while keeping the lesson moving forward."
        )
        
        scenario_grade_level = st.selectbox(
            "Grade Level",
            ["elementary", "middle", "high"],
            index=0
        )
        
        scenario_subject = st.selectbox(
            "Subject",
            ["mathematics", "science", "language_arts", "social_studies", "other"],
            index=0
        )
        
        scenario_challenge = st.selectbox(
            "Challenge Type",
            ["behavioral", "academic", "emotional", "social", "other"],
            index=0
        )
    
    # Start/Reset conversation button
    start_button = st.button("Start New Conversation")

# Initialize or reset conversation if button clicked
if start_button:
    # Clear previous conversation state
    st.session_state.messages = []
    st.session_state.evaluation_complete = False
    
    # Convert interests to enum
    try:
        interests = []
        for interest in selected_interests:
            try:
                interests.append(Interest[interest])
            except (KeyError, ValueError) as e:
                st.warning(f"Couldn't convert interest '{interest}' to enum: {str(e)}")
                # Use string value instead
                interests.append(interest)
    except Exception as e:
        st.error(f"Error converting interests to enum: {str(e)}")
        interests = [str(interest) for interest in selected_interests]
    
    # Create the student profile
    try:
        profile = create_student_profile(
            template_name=profile_template,
            name=student_name,
            grade_level=grade_level,
            interests=interests,
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            support_strategies=support_strategies
        )
    except Exception as e:
        st.error(f"Error creating student profile: {str(e)}")
        st.stop()
    
    # Create the scenario
    if scenario_type == "Random":
        try:
            scenario = generate_random_scenario().__dict__
        except Exception as e:
            st.error(f"Error generating random scenario: {str(e)}")
            scenario = {
                "title": "Fallback Scenario",
                "description": "A simple classroom scenario where you need to engage with the student.",
                "grade_level": "elementary",
                "subject": "general",
                "challenge_type": "engagement"
            }
    else:
        scenario = {
            "title": scenario_title,
            "description": scenario_description,
            "grade_level": scenario_grade_level,
            "subject": scenario_subject,
            "challenge_type": scenario_challenge
        }
    
    # Store profile and scenario in session
    st.session_state.profile = profile
    st.session_state.scenario = scenario
    
    # Initialize conversation manager
    try:
        st.session_state.conversation_manager = initialize_conversation_manager(
            profile=profile,
            scenario=scenario,
            model_name=model_name,
            log_level=LogLevel.INFO
        )
    except Exception as e:
        st.error(f"Error initializing conversation manager: {str(e)}")
        st.stop()
    
    # Set conversation as active
    st.session_state.conversation_active = True
    
    # Add system message to conversation
    st.session_state.messages.append({
        "role": "system",
        "content": f"Conversation started with {profile.name}, a grade {profile.grade_level} student."
    })

# Display current configuration if conversation is active
if st.session_state.conversation_active and st.session_state.profile:
    profile = st.session_state.profile
    scenario = st.session_state.scenario
    
    with st.expander("Current Session Information", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Student Profile")
            st.write(f"**Name:** {profile.name}")
            st.write(f"**Grade:** {profile.grade_level}")
            st.write(f"**Interests:** {', '.join([str(i) for i in profile.interests])}")
            st.write(f"**Strengths:** {', '.join(profile.academic_strengths)}")
            st.write(f"**Challenges:** {', '.join(profile.academic_challenges)}")
        
        with col2:
            st.subheader("Scenario")
            st.write(f"**Title:** {scenario['title']}")
            st.write(f"**Description:** {scenario['description']}")

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    if role == "system":
        st.info(content)
    elif role == "teacher":
        st.chat_message("user").write(content)
    elif role == "kb":
        st.chat_message("assistant", avatar="📚").write(content)
    elif role == "student" or role == st.session_state.profile.name if st.session_state.profile else False:
        with st.chat_message("assistant"):
            st.write(content)
    elif role == "evaluation":
        with st.container(border=True):
            st.subheader("Conversation Evaluation")
            st.markdown(content)

# Evaluation results display
if st.session_state.evaluation_complete and 'evaluation_results' in st.session_state:
    eval_results = st.session_state.evaluation_results
    
    with st.expander("View Detailed Evaluation", expanded=True):
        st.subheader("Conversation Evaluation")
        
        st.markdown(f"**Summary:** {eval_results.get('summary', 'No summary available')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Effectiveness Score", eval_results.get('effectiveness', 'N/A'))
        with col2:
            st.metric("Authenticity Score", eval_results.get('authenticity', 'N/A'))
        
        if 'best_practices_alignment' in eval_results:
            st.markdown(f"**Best Practices Alignment:** {eval_results.get('best_practices_alignment', 'N/A')}")
        
        st.subheader("Suggestions")
        for suggestion in eval_results.get('suggestions', ['No suggestions available']):
            st.markdown(f"- {suggestion}")
        
        # Buttons to continue or end
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue Conversation"):
                result = continue_streamlit_conversation(
                    st.session_state.conversation_manager, 
                    True
                )
                st.session_state.evaluation_complete = False
                st.rerun()
        with col2:
            if st.button("End Conversation"):
                result = continue_streamlit_conversation(
                    st.session_state.conversation_manager, 
                    False
                )
                # Save the conversation
                output_file = st.session_state.conversation_manager.save_conversation()
                st.success(f"Conversation saved to: {output_file}")
                st.session_state.conversation_active = False
                st.rerun()

# Chat input
if st.session_state.conversation_active and not st.session_state.evaluation_complete:
    # Create chat input for teacher
    if prompt := st.chat_input("Type your message to the student..."):
        # Add teacher message to chat history
        st.session_state.messages.append({"role": "teacher", "content": prompt})
        
        # Display teacher message
        st.chat_message("user").write(prompt)
        
        # Process message using conversation manager
        if st.session_state.conversation_manager:
            response_data = process_streamlit_message(
                st.session_state.conversation_manager,
                prompt
            )
            
            # Handle different response types
            if response_data["type"] == "student":
                # Add student message to chat history
                st.session_state.messages.append({
                    "role": st.session_state.profile.name,
                    "content": response_data["text"]
                })
                
                # Display student message
                with st.chat_message("assistant"):
                    st.write(response_data["text"])
                    
            elif response_data["type"] == "knowledge_base":
                # Add KB message to chat history
                st.session_state.messages.append({
                    "role": "kb",
                    "content": response_data["text"]
                })
                
                # Display KB message
                st.chat_message("assistant", avatar="📚").write(response_data["text"])
                
            elif response_data["type"] == "evaluation":
                # Store evaluation results
                st.session_state.evaluation_results = response_data["evaluation_results"]
                st.session_state.evaluation_complete = True
                
                # Add evaluation message to chat history
                eval_text = f"""
                ## Evaluation Complete
                
                **Summary:** {response_data['evaluation_results'].get('summary', 'No summary available')}
                
                **Effectiveness:** {response_data['evaluation_results'].get('effectiveness', 'N/A')}
                
                **Authenticity:** {response_data['evaluation_results'].get('authenticity', 'N/A')}
                
                Would you like to continue the conversation?
                """
                
                st.session_state.messages.append({
                    "role": "evaluation",
                    "content": eval_text
                })
                
                st.rerun()
else:
    # Show welcome message if no conversation is active
    if not st.session_state.conversation_active and len(st.session_state.messages) == 0:
        st.info("Configure the student profile and scenario in the sidebar, then click 'Start New Conversation' to begin.") 