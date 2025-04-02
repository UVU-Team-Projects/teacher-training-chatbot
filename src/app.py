import os
import sys
import time
from typing import List, Dict, Any, Optional
import streamlit as st

# Add the project root directory to the path so we can import modules correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import project modules
try:
    from ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from ai.profile_builder import StudentProfileBuilder
    from ai.rag_pipeline import RAG, create_pipeline, chat_with_student
    from ai.simple_rag import SimpleRAG
    from ai.embedding import EmbeddingGenerator
except ImportError:
    from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from src.ai.profile_builder import StudentProfileBuilder
    from src.ai.rag_pipeline import RAG, create_pipeline, chat_with_student
    from src.ai.simple_rag import SimpleRAG
    from src.ai.embedding import EmbeddingGenerator

# Load custom CSS


def load_css():
    css_file = os.path.join(current_dir, "static/css/style.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Set page configuration
st.set_page_config(
    page_title="Teacher Training Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
try:
    load_css()
except Exception as e:
    st.warning(f"Could not load CSS: {e}")

# App title and description
st.title("Teacher Training Chatbot")
st.markdown("""
This application allows you to interact with a Retrieval Augmented Generation (RAG) system
that has been trained on teacher training materials. Ask questions and get responses based on
the knowledge base.
""")

# Sidebar for model configuration
st.sidebar.header("Configuration")

# Model selection
model_type = st.sidebar.selectbox(
    "Select RAG Implementation",
    ["Simple RAG", "Student Profile RAG"]
)

# Model parameters
model_name = st.sidebar.selectbox(
    "Select Model",
    ["gpt-4o-mini"],
    index=0
)

k_documents = st.sidebar.slider(
    "Number of retrieved documents",
    min_value=1,
    max_value=10,
    value=5
)

# Student profile configuration (only shown when Student Profile RAG is selected)
if model_type == "Student Profile RAG":
    st.sidebar.header("Student Profile")

    student_profile: StudentProfile = None

    build_from_prompt = st.sidebar.checkbox(
        label="Build from a prompt", value=False)
    if build_from_prompt:
        prompt = st.sidebar.text_input(
            "Enter a prompt to build the student profile from")
        if st.sidebar.button("Build Profile"):
            builder = StudentProfileBuilder()
            student_profile: StudentProfile = builder.build_profile_from_text(
                prompt)
            st.sidebar.success("Student profile built successfully")
    else:
        template_options = list(STUDENT_TEMPLATES.keys())
        template_options = list(STUDENT_TEMPLATES.keys())
        selected_template = st.sidebar.selectbox(
            "Select Student Template",
            template_options,
            index=0
        )

        student_name = st.sidebar.text_input("Student Name", "Alex")

        grade_level = st.sidebar.number_input(
            "Grade Level",
            min_value=1,
            max_value=12,
            value=2
        )

        interest_options = [interest.value for interest in Interest]
        selected_interests = st.sidebar.multiselect(
            "Interests",
            interest_options,
            default=["science", "sports"]
        )

        # Convert selected interest strings back to Interest enum values
        interests = [Interest(interest) for interest in selected_interests]

        # Create the student profile
        student_profile: StudentProfile = create_student_profile(
            template_name=selected_template,
            name=student_name,
            grade_level=grade_level,
            interests=interests
        )

    if student_profile:
        # Show template details
        with st.sidebar.expander("View Student Profile Details"):
            st.write(f"**Name:** {student_profile.name}")
            st.write(f"**Grade Level:** {student_profile.grade_level}")
            st.write(
                f"**Personality Traits:** {', '.join(student_profile.personality_traits)}")
            st.write(f"**Learning Style:** {student_profile.learning_style}")
            st.write(
                f"**Academic Strengths:** {', '.join(student_profile.academic_strengths)}")
            st.write(
                f"**Academic Challenges:** {', '.join(student_profile.academic_challenges)}")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the RAG system


@st.cache_resource
def initialize_rag_system(model_type: str, model_name: str):
    """Initialize the appropriate RAG system based on user selection"""
    with st.spinner("Initializing RAG system... This may take a moment."):
        if model_type == "Simple RAG":
            return SimpleRAG(model_name=model_name)
        else:  # Student Profile RAG
            agent = create_pipeline()
            return agent


# Get RAG system
rag_system = initialize_rag_system(model_type, model_name)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_query = st.chat_input("Ask a question about teaching...")

# Process user input
if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)

    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            if model_type == "Simple RAG":
                # Use the Simple RAG implementation
                response = rag_system.generate_response(
                    user_query, k=k_documents)
                response_content = response.content
            else:
                # Use the Student Profile RAG implementation
                response_content = chat_with_student(
                    rag_system, student_profile, user_query)

            # Simulate typing effect
            full_response = response_content
            displayed_response = ""

            # Optional: Add typing effect (comment out if you don't want this)
            for chunk in full_response.split():
                displayed_response += chunk + " "
                message_placeholder.markdown(displayed_response + "▌")
                time.sleep(0.05)

            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response_content})

# Add expander with retrieved documents (if checkbox is selected)
show_context = st.sidebar.checkbox("Show retrieved context", value=False)

if show_context and st.session_state.messages and len(st.session_state.messages) > 0:
    with st.expander("Retrieved Documents"):
        if user_query:
            # Get the context documents
            db = EmbeddingGenerator().return_chroma()
            results = db.similarity_search_with_score(
                user_query, k=k_documents)

            for i, (doc, score) in enumerate(results):
                st.markdown(f"### Document {i+1} (Score: {score:.4f})")
                st.markdown(doc.page_content)
                st.markdown("---")

# Add a reset button to clear the chat
if st.sidebar.button("Reset Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
