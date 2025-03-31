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

def example_use_case(log_level: LogLevel = LogLevel.INFO, show_openai_logs: bool = False,
                     use_cli: bool = True):
    """
    Example showing how to create and use a student profile and scenario with the LangGraph agent.

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

    logger.info("Creating and running the LangGraph agent...")
    # Create the supervisor agent with the specified log level
    supervisor = Supervisor(log_level=log_level)

    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated session ID: {session_id}")

    logger.debug("Creating supervisor graph")
    graph = supervisor.create_supervisor_graph()

    logger.info("Initializing agent state...")
    # Initialize the agent state with both the profile and scenario
    state = supervisor.initialize_agent_state(
        profile=profile,
        scenario=scenario,
        session_id=session_id
    )

    # Set up CLI mode if requested
    if use_cli:
        state["ui_metadata"]["cli_mode"] = True
    else:
        state["ui_metadata"]["cli_mode"] = False

    # Print the start of the conversation
    print(f"\n{Fore.GREEN}Teacher-Student Conversation{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Student Profile: {profile.name}, Grade {profile.grade_level}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Scenario: {scenario['title']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit', 'done', or 'evaluate' to end the conversation{Style.RESET_ALL}\n")

    # Execute the graph with our state
    logger.info(f"Invoking the agent...")
    try:
        # In CLI mode, we run the graph and let it handle the human-in-the-loop pattern
        if use_cli:
            # Execute the graph with initial state
            result = graph.invoke(state, config={"configurable": {"thread_id": session_id}})

            # The result will contain all the conversation history and evaluation
            if result.get("conversation_done", False):
                logger.info(
                    "Conversation completed successfully with evaluation")
            else:
                logger.info(
                    "Conversation was interrupted or ended without evaluation")

            # Return the final state for potential further use
            return result

        # In non-CLI mode (e.g., for Streamlit), we return the graph and session ID
        else:
            logger.info("Prepared graph and state for UI integration")
            # Just return what we need to connect from the UI
            return {
                "graph": graph,
                "supervisor": supervisor,
                "session_id": session_id,
                "initial_state": state,
                "profile": profile,
                "scenario": scenario
            }

    except Exception as e:
        logger.error(f"Error in graph execution: {str(e)}")
        print(f"\nError occurred: {str(e)}")
        # Return the last state we had
        return state


def streamlit_integration_example():
    """
    Example showing how to integrate with Streamlit.
    This is a placeholder for the actual integration code.

    In a real implementation, this would be in a separate file.
    """
    # Get the graph, supervisor and session ID
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
    
    # Show conversation history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        role = message.get('role', 'assistant')
        content = message.get('content', '')
        with st.chat_message(role):
            st.write(content)
    
    # Get user input
    if prompt := st.chat_input("What do you want to say to the student?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with our supervisor
        result = st.session_state.resources['supervisor'].update_from_streamlit(
            st.session_state.resources['session_id'], 
            prompt
        )
        
        # Get student response
        if 'state' in result and 'messages' in result['state']:
            latest_message = result['state']['messages'][-1]
            response = latest_message.content
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display response
            with st.chat_message("assistant"):
                st.write(response)
        
        # Check if conversation is done
        if result.get('is_done', False):
            st.success("Conversation complete!")
            
            # Show evaluation results
            if 'evaluation_results' in result.get('state', {}):
                eval_results = result['state']['evaluation_results']
                st.header("Conversation Evaluation")
                st.write(f"Summary: {eval_results.get('summary', 'No summary available')}")
                st.write(f"Effectiveness: {eval_results.get('effectiveness', 'N/A')}")
                st.write(f"Authenticity: {eval_results.get('authenticity', 'N/A')}")
                
                st.subheader("Suggestions")
                for suggestion in eval_results.get('suggestions', ['No suggestions available']):
                    st.write(f"- {suggestion}")
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
