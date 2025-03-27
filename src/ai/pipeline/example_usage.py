
import os
import sys
import argparse
from colorama import Fore, Style  # For terminal color output
from langchain_core.messages import HumanMessage

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(ai_dir)
root_dir = os.path.dirname(src_dir)
sys.path.append(root_dir)

# Now we can import our modules
from src.ai.pipeline.supervisor import Supervisor
from src.ai.student_profiles import Interest, create_student_profile
from src.logging import AgentLogger, LogLevel

def example_use_case(log_level: LogLevel = LogLevel.INFO, show_openai_logs: bool = False):
    """
    Example showing how to create and use a student profile and scenario with the LangGraph agent.

    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        recursion_limit: Maximum number of steps in the conversation before forcing termination
        show_openai_logs: Whether to show OpenAI and HTTP related logs
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

    logger.debug("Creating supervisor graph")
    graph = supervisor.create_supervisor_graph()

    logger.info("Initializing agent state...")
    # Initialize the agent state with both the profile and scenario
    state = supervisor.initialize_agent_state(
        profile=profile, scenario=scenario)

    # Execute the graph with our state
    logger.info(f"Invoking the agent ...")
    try:
        # Add an initial teacher message
        # Ask for user input for the initial teacher message
        while True:
            print("Enter your message to the student (exit, quit, q to exit):")
            user_input = input(Fore.GREEN + "Teacher: " + Style.RESET_ALL)
            if not user_input.strip():
                # Use default message if user doesn't provide one
                user_input = "Alex, I notice you're having trouble focusing on our fractions worksheet. What's going on?"
                logger.debug("Using default teacher message")

            if user_input.lower() in ["exit", "quit", "q"]:
                logger.info("User chose to exit the conversation")
                break

            logger.debug(f"Adding teacher message: {user_input}")
            state["messages"] = state.get("messages", []) + [HumanMessage(
                content=user_input, name="teacher")]

            # Use the invoke_graph method that includes recursion limit
            result = graph.invoke(
                state, config={"configurable": {"thread_id": 43}})

            print("\nTeacher-Student Conversation:")
            last_message = result["messages"][-1]
            if isinstance(last_message, HumanMessage):
                print(
                    Fore.BLUE + f"{profile.name}: {last_message.content}" + Style.RESET_ALL)
            else:
                print(Fore.GREEN +
                      f"Teacher: {last_message.content}" + Style.RESET_ALL)

            # for message in result["messages"]:
            #     sender = message.name if hasattr(
            #         message, 'name') else "Teacher"
            #     content = message.content if hasattr(
            #         message, 'content') else str(message)
            #     print(f"{sender}: {content}")

        logger.info("Example completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error in graph execution: {str(e)}")
        print(f"\nError occurred: {str(e)}")
        # Return the last state we had
        return state


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

    args = parser.parse_args()

    # Convert string to LogLevel enum
    log_level = LogLevel[args.log_level]

    # Run the example with the specified parameters
    example_use_case(log_level, args.show_openai_logs)
