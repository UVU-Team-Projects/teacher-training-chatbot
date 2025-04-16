import os
import sys
import argparse
from colorama import Fore, Style  # For terminal color output
import uuid

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(src_dir)
sys.path.append(root_dir)

# Now we can import our modules
from src.logging import AgentLogger, LogLevel
from src.ai.student_profiles import Interest, create_student_profile
from src.ai.standalone_agents import ConversationManager

def example_standalone_agents(log_level: LogLevel = LogLevel.INFO, show_openai_logs: bool = False):
    """
    Example showing the new standalone agent approach.

    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        show_openai_logs: Whether to show OpenAI and HTTP related logs
    """
    # Set the logging level
    AgentLogger.set_level(log_level)

    # Configure whether to show filtered logs
    AgentLogger.show_filtered(show_openai_logs)

    logger = AgentLogger.get_logger("Example")
    logger.info(f"Starting standalone agents example with log level: {log_level.name}")

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
    logger.debug(f"Created profile for {profile.name}, grade {profile.grade_level}")

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
    
    # Initialize the conversation manager
    logger.info("Initializing conversation manager...")
    manager = ConversationManager(log_level=log_level)
    manager.initialize(profile, scenario)
    
    # Print the start of the conversation
    print(f"\n{Fore.GREEN}Teacher-Student Conversation{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Student Profile: {profile.name}, Grade {profile.grade_level}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Scenario: {scenario['title']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit', 'done', or 'evaluate' to end the conversation{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'kb: <query>' to search the knowledge base{Style.RESET_ALL}\n")
    
    # Interactive conversation loop
    conversation_active = True
    while conversation_active:
        # Get teacher input
        teacher_message = input(f"{Fore.GREEN}Teacher: {Style.RESET_ALL}")
        
        # Process the message
        response, metadata = manager.process_message(teacher_message)
        
        # Check if conversation is done
        if metadata.get("is_done", False):
            print(f"\n{Fore.YELLOW}{response}{Style.RESET_ALL}")
            
            # Ask user if they want to continue
            continue_choice = input(f"{Fore.YELLOW}> {Style.RESET_ALL}").strip().lower()
            
            # Process the continue choice
            result = manager.continue_conversation(continue_choice in ["yes", "y", "continue"])
            
            # Check if we should end the conversation
            if result.get("is_done", True):
                conversation_active = False
                logger.info("Conversation ended")
                print(f"\n{Fore.YELLOW}Conversation ended. Saving conversation...{Style.RESET_ALL}")
                
                # Save the conversation
                output_file = manager.save_conversation()
                print(f"\n{Fore.YELLOW}Conversation saved to: {output_file}{Style.RESET_ALL}")
    
    # Return the final conversation state for potential further use
    return {
        "profile": profile,
        "scenario": scenario,
        "evaluation_results": manager.evaluation_results,
        "session_id": manager.session_id
    }

def streamlit_integration_example():
    """
    Example showing how to integrate with Streamlit.
    This is a placeholder showing the basic API for integration.
    
    In a real implementation, this would be in a separate file.
    """
    # Example of how to initialize for Streamlit
    from src.ai.student_profiles import create_student_profile, Interest
    from src.ai.standalone_agents import initialize_conversation_manager, process_streamlit_message, continue_streamlit_conversation
    
    # Create a student profile
    profile = create_student_profile(
        template_name="active_learner",
        name="Alex",
        grade_level=2,
        interests=[Interest.SCIENCE, Interest.SPORTS],
        academic_strengths=["math", "science experiments"],
        academic_challenges=["sitting still", "writing long passages"],
        support_strategies=["movement breaks", "visual aids"]
    )
    
    # Create a scenario
    scenario = {
        "title": "Math Class Disruption",
        "description": "During a math lesson on fractions, a student is having trouble focusing and starts distracting others around them. The teacher needs to address this while keeping the lesson moving forward.",
        "grade_level": "elementary",
        "subject": "mathematics",
        "challenge_type": "behavioral"
    }
    
    # Initialize the conversation manager
    manager = initialize_conversation_manager(
        profile=profile,
        scenario=scenario,
        model_name="gpt-4o-mini",
        log_level=LogLevel.INFO
    )
    
    # Example of how to process a message in Streamlit
    teacher_message = "Hello, how are you doing today?"
    response_data = process_streamlit_message(manager, teacher_message)
    
    # Example of how you would handle the response in Streamlit
    """
    import streamlit as st
    
    # Display the response
    if response_data["type"] == "student":
        st.chat_message("assistant").write(response_data["text"])
    elif response_data["type"] == "knowledge_base":
        st.info(response_data["text"])
    elif response_data["type"] == "evaluation":
        # Display evaluation results
        st.success("Evaluation complete!")
        eval_results = response_data["evaluation_results"]
        
        st.write(f"Summary: {eval_results.get('summary', 'No summary available')}")
        st.write(f"Effectiveness: {eval_results.get('effectiveness', 'N/A')}")
        st.write(f"Authenticity: {eval_results.get('authenticity', 'N/A')}")
        
        st.write("Suggestions:")
        for suggestion in eval_results.get('suggestions', ['No suggestions available']):
            st.write(f"- {suggestion}")
            
        # Ask if user wants to continue
        if st.button("Continue Conversation"):
            continue_result = continue_streamlit_conversation(manager, True)
        else:
            continue_result = continue_streamlit_conversation(manager, False)
    """
    
    # Return the manager for further use
    return manager

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run the standalone agent example")
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

    args = parser.parse_args()

    # Convert string to LogLevel enum
    log_level = LogLevel[args.log_level]

    # Run the example with the specified parameters
    example_standalone_agents(log_level, args.show_openai_logs) 