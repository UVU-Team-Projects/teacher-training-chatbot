import streamlit as st
import time
import sys
import os
from pathlib import Path

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.append(str(src_path))
from ai.chatbot import TeacherTrainingChatbot

def main():
    student = st.session_state.selected_student
    scenario = st.session_state.selected_scenario

    st.subheader(f"{scenario.title} - {student.name}")

    # Initialize chatbot if not in session state
    if "chatbot" not in st.session_state:
        try:
            with st.spinner("Initializing AI model..."):
                st.session_state.chatbot = TeacherTrainingChatbot()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {str(e)}")
            st.info("Make sure Ollama is running with: 'ollama serve'")
            st.info("And that you've pulled the model with: 'ollama pull llama3.2:3b'")
            return

    # Streamed response emulator for AI responses
    def response_generator(response):
        for word in response.split():
            yield word + " "
            time.sleep(0.02)  # Slightly faster than before

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter your response...", key="chat_input"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with the AI chatbot
        with st.chat_message(f"{student.name[0]}"):
            student_profile = student.__dict__
            scenario_info = scenario.__dict__
            
            with st.spinner("Thinking..."):
                try:
                    ai_response = st.session_state.chatbot.invoke_agent(
                        query=prompt,
                        student_profile=student_profile,
                        scenario=scenario_info
                    )
                    
                    # Display streamed response
                    response_text = st.write_stream(response_generator(ai_response))
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    response_text = error_msg
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": f"{student.name[0]}", "content": response_text})