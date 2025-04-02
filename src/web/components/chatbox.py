import streamlit as st
import time
import sys
import os
from pathlib import Path

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.append(str(src_path))
# from ai.chatbot import TeacherTrainingChatbot
from src.ai.standalone_agents import (
    initialize_conversation_manager,
    process_streamlit_message,
    continue_streamlit_conversation,
    ConversationManager
)

def main():
    profile = st.session_state.selected_student
    st.session_state.profile = profile
    scenario = st.session_state.selected_scenario

     # Initialize conversation manager
    try:
        st.session_state.conversation_manager = initialize_conversation_manager(
            profile=profile,
            scenario=scenario,
            model_name="gpt-4o-mini",
            # log_level=LogLevel.INFO
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

    st.subheader(f"{scenario.get('title')} - {profile.name}")

    # Display current configuration if conversation is active
    if st.session_state.conversation_active and st.session_state.selected_student:
        
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