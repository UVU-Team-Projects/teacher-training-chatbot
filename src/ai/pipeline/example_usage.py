import os
import sys
import argparse
from colorama import Fore, Style  # For terminal color output
from langchain_core.messages import HumanMessage
import uuid

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(ai_dir)
root_dir = os.path.dirname(src_dir)
sys.path.append(root_dir)

# Now we can import our modules
from src.logging import AgentLogger, LogLevel
from src.ai.student_profiles import Interest, create_student_profile
from src.ai.pipeline.supervisor import Supervisor
from src.ai.pipeline.standalone_student import StandaloneStudentBot

def example_use_case(log_level: LogLevel = LogLevel.INFO, show_openai_logs: bool = False,
                     use_cli: bool = True):
    """
    Example showing the two-phase approach: first chat with student, then evaluate.

    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        show_openai_logs: Whether to show OpenAI and HTTP related logs
        use_cli: Whether to use CLI mode or prepare for UI integration
    """
    # Set the logging level
    AgentLogger.set_level(log_level)

    # Configure whether to show filtered logs
    AgentLogger.show_filtered(show_openai_logs)

    logger = AgentLogger.get_logger("Example")
    logger.info(f"Starting example with log level: {log_level.name}")

    if show_openai_logs:
        logger.info("OpenAI and HTTP logs will be shown")
    else:
        logger.info("OpenAI and HTTP logs are filtered out")

    logger.info("Creating a student profile...")
    # Create a student profile using the predefined template
    profile = create_student_profile(
        template_name="active_learner",
        name="Alex",
        grade_level=2,
        interests=[Interest.SCIENCE, Interest.SPORTS],
        academic_strengths=["math", "science experiments"],
        academic_challenges=["sitting still", "writing long passages"],
        support_strategies=["movement breaks", "visual aids"]
    )
    logger.debug(
        f"Created profile for {profile.name}, grade {profile.grade_level}")

    logger.info("Creating a scenario...")
    # Create a sample scenario (you can use your ScenarioGenerator class here)
    scenario = {
        "title": "Math Class Disruption",
        "description": "During a math lesson on fractions, a student is having trouble focusing and starts distracting others around them. The teacher needs to address this while keeping the lesson moving forward.",
        "grade_level": "elementary",
        "subject": "mathematics",
        "challenge_type": "behavioral"
    }
    logger.debug(f"Created scenario: {scenario['title']}")

    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated session ID: {session_id}")

    # PHASE 1: Interactive conversation with the student bot
    logger.info("Starting interactive conversation with student bot...")
    student_bot = StandaloneStudentBot()
    student_bot.initialize(profile, scenario)

    # Print the start of the conversation
    print(f"\n{Fore.GREEN}Teacher-Student Conversation{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Student Profile: {profile.name}, Grade {profile.grade_level}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Scenario: {scenario['title']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit', 'done', or 'evaluate' to end the conversation{Style.RESET_ALL}\n")

    # Interactive conversation loop
    if use_cli:
        while True:
            # Get teacher input
            teacher_message = input(f"{Fore.GREEN}Teacher: {Style.RESET_ALL}")
            
            # Check for exit commands
            if teacher_message.lower() in ["exit", "quit", "bye", "goodbye", "done", "end", "evaluate"]:
                print(f"{Fore.YELLOW}Ending conversation and starting evaluation...{Style.RESET_ALL}")
                break
            
            # Get student response
            student_bot.get_response(teacher_message)
        
        # End conversation and get metadata
        conversation_metadata = student_bot.end_conversation()
        conversation_messages = student_bot.get_conversation_history()
        
        # PHASE 2: Evaluation
        logger.info("Creating evaluation supervisor...")
        supervisor = Supervisor(log_level=log_level)
        
        logger.debug("Creating supervisor graph")
        graph = supervisor.create_supervisor_graph()
        
        logger.info("Initializing agent state with conversation history...")
        # Initialize the agent state with profile, scenario, and conversation history
        state = supervisor.initialize_agent_state(
            profile=profile,
            scenario=scenario,
            session_id=session_id,
            conversation_messages=conversation_messages
        )
        
        # Execute the evaluation graph
        logger.info("Running evaluation...")
        
        # Use get_thread to get consistent thread management
        result = graph.invoke(state, config={"configurable": {"thread_id": session_id}})
        
        # The result will contain the evaluation
        if result.get("conversation_done", False):
            logger.info("Evaluation completed successfully")
            
            # If the user opted to continue the conversation, handle that
            if result.get("continue_conversation", False):
                logger.info("User chose to continue conversation after evaluation")
                
                # Enter a new conversation loop
                while True:
                    # Get teacher input
                    teacher_message = input(f"{Fore.GREEN}Teacher: {Style.RESET_ALL}")
                    
                    # Check for exit commands
                    if teacher_message.lower() in ["exit", "quit", "bye", "goodbye", "done", "end", "evaluate"]:
                        print(f"{Fore.YELLOW}Ending continued conversation...{Style.RESET_ALL}")
                        break
                    
                    # Create a teacher message
                    teacher_msg = HumanMessage(content=teacher_message, name="teacher")
                    
                    # Update state with the message and resume the thread
                    thread.update_state({"messages": [teacher_msg]})
                    result = thread.resume()
                    
                    # Check if we should end the conversation
                    if result.get("conversation_done", True) and not result.get("continue_conversation", False):
                        break
        else:
            logger.warning("Evaluation was interrupted or ended without completion")
        
        # Return the final state for potential further use
        return result
    
    # Non-CLI mode for UI integration
    else:
        logger.info("Prepared resources for UI integration")
        # Return what we need for UI integration
        return {
            "student_bot": student_bot,
            "supervisor": Supervisor(log_level=log_level),
            "session_id": session_id,
            "profile": profile,
            "scenario": scenario
        }


def streamlit_integration_example():
    """
    Example showing how to integrate with Streamlit.
    This is a placeholder for the actual integration code.

    In a real implementation, this would be in a separate file.
    """
    # Get the resources needed for UI integration
    resources = example_use_case(use_cli=False)

    # This is placeholder code showing how it would work in Streamlit
    # In a real implementation, this would be called from the Streamlit app

    # Example pseudocode:
    """
    import streamlit as st
    
    st.title("Teacher-Student Conversation")
    
    # Initialize resources on first run
    if 'resources' not in st.session_state:
        st.session_state.resources = example_use_case(use_cli=False)
        
    # Display student profile and scenario
    st.sidebar.header("Student Profile")
    st.sidebar.write(f"Name: {st.session_state.resources['profile'].name}")
    st.sidebar.write(f"Grade: {st.session_state.resources['profile'].grade_level}")
    
    st.sidebar.header("Scenario")
    st.sidebar.write(st.session_state.resources['scenario']['title'])
    st.sidebar.write(st.session_state.resources['scenario']['description'])
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_phase = "student_interaction"
    
    # Display conversation history
    for message in st.session_state.messages:
        role = message.get('role', 'assistant')
        content = message.get('content', '')
        with st.chat_message(role):
            st.write(content)
    
    # Phase 1: Student interaction
    if st.session_state.conversation_phase == "student_interaction":
        # Get user input
        if prompt := st.chat_input("What do you want to say to the student?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Check for exit command
            if prompt.lower() in ["exit", "quit", "bye", "goodbye", "done", "end", "evaluate"]:
                st.session_state.conversation_phase = "evaluation"
                st.rerun()
            
            # Get student response
            student_bot = st.session_state.resources['student_bot']
            response = student_bot.get_response(prompt)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display response
            with st.chat_message("assistant"):
                st.write(response)
    
    # Phase 2: Evaluation
    elif st.session_state.conversation_phase == "evaluation":
        student_bot = st.session_state.resources['student_bot']
        conversation_messages = student_bot.get_conversation_history()
        
        supervisor = st.session_state.resources['supervisor']
        session_id = st.session_state.resources['session_id']
        profile = st.session_state.resources['profile']
        scenario = st.session_state.resources['scenario']
        
        # Create the graph
        graph = supervisor.create_supervisor_graph()
        
        # Initialize state
        state = supervisor.initialize_agent_state(
            profile=profile,
            scenario=scenario,
            session_id=session_id,
            conversation_messages=conversation_messages
        )
        
        # Run evaluation
        result = graph.invoke(state)
        
        # Display evaluation
        st.header("Conversation Evaluation")
        if 'evaluation_results' in result:
            eval_results = result['evaluation_results']
            st.write(f"Summary: {eval_results.get('summary', 'No summary available')}")
            st.write(f"Effectiveness: {eval_results.get('effectiveness', 'N/A')}")
            st.write(f"Authenticity: {eval_results.get('authenticity', 'N/A')}")
            
            st.subheader("Suggestions")
            for suggestion in eval_results.get('suggestions', ['No suggestions available']):
                st.write(f"- {suggestion}")
        else:
            st.write("No evaluation results available")
    """

    return resources


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run the teacher-student simulation example")
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    parser.add_argument(
        "--show-openai-logs",
        action="store_true",
        help="Show OpenAI and HTTP related logs"
    )
    parser.add_argument(
        "--ui-mode",
        action="store_true",
        help="Prepare for UI integration instead of running in CLI mode"
    )

    args = parser.parse_args()

    # Convert string to LogLevel enum
    log_level = LogLevel[args.log_level]

    # Run the example with the specified parameters
    if args.ui_mode:
        resources = streamlit_integration_example()
        print("Resources prepared for UI integration:")
        print(f"Session ID: {resources['session_id']}")
        print("Run your Streamlit app to continue")
    else:
        example_use_case(log_level, args.show_openai_logs)
