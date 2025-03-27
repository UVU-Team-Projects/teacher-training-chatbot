import streamlit as st
import time
import sys
import os
from pathlib import Path
import requests
import subprocess

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.append(str(src_path))
from ai.chatbot import TeacherTrainingChatbot

def is_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def is_model_available(model_name="llama3.2:3b"):
    """Check if the model is available in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(m.get("name") == model_name for m in models)
        return False
    except:
        return False

def clear_chat():
    """Clear the chat history"""
    if "ai_messages" in st.session_state:
        st.session_state.ai_messages = []

def main():
    # Create two columns for the header
    col1, col2 = st.columns([5, 1])
    
    # Use the first column for the title
    with col1:
        st.subheader("AI Teaching Assistant")
    
    # Use the second column for the clear button
    with col2:
        st.button("🗑️ Clear Chat", on_click=clear_chat, key="clear_ai_chat")

    # Check Ollama service
    if not is_ollama_running():
        st.error("⚠️ Ollama service is not running")
        st.info("Please start Ollama with: 'ollama serve'")
        st.button("Retry Connection", on_click=lambda: None)
        return

    # Check model availability
    model_name = "llama3.2:3b"
    if not is_model_available(model_name):
        st.warning(f"⚠️ Model '{model_name}' is not downloaded")
        
        if st.button("Download Model"):
            with st.spinner(f"Downloading {model_name}... This may take several minutes"):
                result = subprocess.run(["ollama", "pull", model_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success(f"Successfully downloaded {model_name}")
                else:
                    st.error(f"Failed to download model: {result.stderr}")
                    return
        else:
            st.info(f"Please download the model with: 'ollama pull {model_name}'")
            return

    # Initialize chatbot if not in session state
    chatbot_initialized = False
    if "ai_chatbot" not in st.session_state or st.session_state.ai_chatbot is None:
        try:
            with st.spinner("Initializing AI model..."):
                st.session_state.ai_chatbot = TeacherTrainingChatbot()
                chatbot_initialized = True
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {str(e)}")
            st.info("Make sure Ollama is running and the model is downloaded.")
            
            # Add a retry button
            if st.button("Retry Connection", key="retry_chatbot_init"):
                st.rerun()
            return
    else:
        chatbot_initialized = True

    # Only proceed if chatbot is initialized
    if not chatbot_initialized:
        return

    # Streamed response emulator for AI responses
    def response_generator(response):
        for word in response.split():
            yield word + " "
            time.sleep(0.02)  # Adjust speed as needed

    # Initialize chat history with a unique name to avoid conflicts
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter your question...", key="ai_chat_input"):
        # Add user message to chat history
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with the AI chatbot - check again that chatbot exists
        if st.session_state.ai_chatbot is None:
            st.error("Chatbot not properly initialized. Please refresh the page.")
            return

        with st.chat_message("AI"):
            # Create empty dictionaries for student and scenario
            student_profile = {}
            scenario_info = {}
            
            # If student and scenario are selected, use them
            if hasattr(st.session_state, 'selected_student') and st.session_state.selected_student:
                student_profile = st.session_state.selected_student.__dict__
            if hasattr(st.session_state, 'selected_scenario') and st.session_state.selected_scenario:  
                scenario_info = st.session_state.selected_scenario.__dict__
            
            with st.spinner("Thinking..."):
                try:
                    ai_response = st.session_state.ai_chatbot.invoke_agent(
                        query=prompt,
                        student_profile=student_profile,
                        scenario=scenario_info
                    )
                    
                    # Display streamed response
                    response_text = st.write_stream(response_generator(ai_response))
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.info("Try refreshing the page or restarting Ollama.")
                    response_text = error_msg
        
        # Add assistant response to chat history
        st.session_state.ai_messages.append({"role": "AI", "content": response_text})