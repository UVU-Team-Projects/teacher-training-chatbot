from typing import List, Dict, Any, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


# Get the absolute path of the project root
import os, sys
root_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the src directory
src_dir = os.path.join(root_dir, 'src')
# Add the src to sys.path
sys.path.append(src_dir)

# Project imports
from agent_state import AgentState
from student_bot import StudentBot, Evaluation
from student_profiles import StudentProfile
from agentTools import set_student_profile_in_state, set_scenario_in_state
from logging import AgentLogger, LogLevel
from langgraph.checkpoint.memory import MemorySaver
from standalone_student import StandaloneStudentBot

# List of available agent members
members = ["evaluation", "student_bot", "continue_prompt"]
# Options including completion state
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["evaluation", "student_bot", "continue_prompt", "FINISH"]


class Supervisor:
    def __init__(self, model_name: str = "gpt-4o-mini", log_level: LogLevel = LogLevel.INFO):
        self.llm = ChatOpenAI(model=model_name)
        self.evaluation = Evaluation()
        self.student_bot = None  # Will be initialized when needed
        self.checkpointer = MemorySaver()  # For persisting state

        # Initialize logger
        self.logger = AgentLogger.get_logger("Supervisor")
        AgentLogger.set_level(log_level)
        self.logger.info(f"Initializing Supervisor with model: {model_name}")

        self.supervisor_prompt = (
            "You are a supervisor tasked with evaluating a conversation between a teacher and student."
            " Your job is to provide detailed feedback on the teacher's approach."
        )
        self.logger.debug(f"Supervisor prompt: {self.supervisor_prompt}")

    def initialize_agent_state(self, state: AgentState = None, profile: StudentProfile = None,
                               scenario=None, session_id: str = None, conversation_messages=None) -> AgentState:
        """
        Initialize a complete agent state with a student profile, scenario, and conversation history.

        Args:
            state: Initial state dictionary, will be created if None
            profile: Optional StudentProfile object
            scenario: Optional scenario object
            session_id: Optional session identifier for tracking UI sessions
            conversation_messages: List of messages from the teacher-student conversation

        Returns:
            A properly initialized agent state dictionary
        """
        self.logger.info("Initializing agent state")

        if not state:
            self.logger.debug("Creating new AgentState")
            state = AgentState()

        if profile:
            self.logger.info(f"Setting student profile: {profile.name}")
            state = set_student_profile_in_state(state, profile)
            
            # If we have a profile, initialize the student bot
            if not self.student_bot:
                self.student_bot = StandaloneStudentBot()
                self.student_bot.initialize(profile, scenario)

        if scenario:
            title = getattr(scenario, 'title', scenario.get(
                'title', 'Unknown scenario')) if hasattr(scenario, 'get') else 'Unknown scenario'
            self.logger.info(f"Setting scenario: {title}")
            state = set_scenario_in_state(state, scenario)

        if session_id:
            state["session_id"] = session_id

        # Add conversation messages if provided
        if conversation_messages:
            state["messages"] = conversation_messages
            self.logger.info(f"Added {len(conversation_messages)} messages to state")

        # Initialize UI metadata
        state["ui_metadata"] = {
            "current_speaker": "system",
            "is_thinking": False,
            "can_interrupt": True
        }

        # Set initial node to evaluation
        state["current_node"] = "evaluation"
        state["conversation_done"] = False
        state["continue_conversation"] = False

        # Log the complete state at debug level
        AgentLogger.log_state(state, "INITIALIZED STATE")

        return state

    def supervisor(self, state: AgentState) -> Command[Literal["evaluation", "student_bot", "continue_prompt", END]]:
        """
        Core routing logic that decides which node to go to next.

        Args:
            state: Current agent state

        Returns:
            Command directing to the next node
        """
        self.logger.debug("Supervisor node called")

        # Get the last node that was processed
        previous_node = state.get("current_node", None)
        
        # Print current state for debugging
        self.logger.debug(f"Current node: {previous_node}")
        self.logger.debug(f"Conversation done: {state.get('conversation_done', False)}")
        self.logger.debug(f"Continue conversation: {state.get('continue_conversation', False)}")

        # Check if we should continue the conversation
        if state.get("continue_conversation", False):
            self.logger.info("User wants to continue conversation after evaluation")
            return Command(goto="student_bot",
                         update={'current_node': 'student_bot',
                                 'conversation_done': False,
                                 'ui_metadata': {**state.get("ui_metadata", {}),
                                               "is_complete": False,
                                               "current_speaker": "teacher",
                                               "is_evaluating": False}})

        # After evaluation is done, always go to continue prompt
        if previous_node == "evaluation":
            self.logger.info("Evaluation completed, showing continue prompt")
            return Command(goto="continue_prompt",
                         update={'current_node': 'continue_prompt'})
                         
        # Check if conversation is marked as done but we're not coming from evaluation
        if state.get("conversation_done", False) and previous_node != "evaluation":
            self.logger.info("Conversation marked as done, showing continue prompt")
            return Command(goto="continue_prompt",
                         update={'current_node': 'continue_prompt'})
        
        # After student_bot interaction, go to evaluation
        if previous_node == "student_bot":
            return Command(goto="evaluation",
                         update={'current_node': 'evaluation',
                                 'ui_metadata': {**state.get("ui_metadata", {}),
                                               "current_speaker": "system",
                                               "is_evaluating": True}})
        
        # By default, start with evaluation (if coming from START)
        return Command(goto="evaluation",
                     update={'current_node': 'evaluation',
                             'ui_metadata': {**state.get("ui_metadata", {}),
                                           "current_speaker": "system",
                                           "is_evaluating": True}})

    def student_bot_node(self, state: AgentState) -> Command[Literal["supervisor"]]:
        """
        Handle interaction with the student bot.
        
        Args:
            state: Current agent state
            
        Returns:
            Command with student response
        """
        self.logger.info("Student bot node called")
        
        # Get the last message from the teacher
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if last_message and hasattr(last_message, 'name') and last_message.name == "teacher":
            # Get response from student bot
            teacher_message = last_message.content
            response = self.student_bot.get_response(teacher_message)
            
            # Get student name
            student_name = self.student_bot.student_name
            
            # Update UI metadata
            ui_metadata = state.get("ui_metadata", {})
            ui_metadata.update({
                "current_speaker": "student",
                "is_thinking": False,
                "student_name": student_name
            })
            
            # Return command with student response
            return Command(
                update={
                    'current_node': 'student_bot',
                    'ui_metadata': ui_metadata
                },
                goto='supervisor'
            )
        
        # If there's no teacher message, just return to supervisor
        return Command(
            update={'current_node': 'student_bot'},
            goto='supervisor'
        )
    
    def continue_prompt_node(self, state: AgentState) -> Command[Literal["supervisor", END]]:
        """
        Ask the user if they want to continue the conversation after evaluation.
        
        Args:
            state: Current agent state
            
        Returns:
            Command with updated state
        """
        self.logger.info("Continue prompt node called")
        
        # Print the continue prompt
        print("\n" + "="*50)
        print(f"Would you like to continue the conversation? (yes/no)")
        
        # Get user input
        user_input = input("> ").strip().lower()
        
        # Check if user wants to continue
        if user_input in ["yes", "y", "continue"]:
            self.logger.info("User chose to continue the conversation")
            return Command(
                update={
                    'continue_conversation': True,
                    'conversation_done': False,
                    'ui_metadata': {**state.get("ui_metadata", {}),
                                  "is_complete": False,
                                  "current_speaker": "teacher"}
                },
                goto='supervisor'
            )
        else:
            self.logger.info("User chose to end the conversation")
            return Command(
                update={
                    'continue_conversation': False,
                    'conversation_done': True,
                    'ui_metadata': {**state.get("ui_metadata", {}),
                                  "is_complete": True}
                },
                goto=END
            )

    def create_supervisor_graph(self) -> CompiledStateGraph:
        """
        Create a supervisor graph with evaluation and optional student interaction.
        
        Returns:
            Compiled workflow graph
        """
        self.logger.info("Creating supervisor graph")

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        self.logger.debug("Adding supervisor node")
        workflow.add_node("supervisor", self.supervisor)
        
        self.logger.debug("Adding evaluation node")
        workflow.add_node('evaluation', self.evaluation.evaluate)
        
        self.logger.debug("Adding student_bot node")
        workflow.add_node('student_bot', self.student_bot_node)
        workflow.add_node('student_bot2', self.student_bot_node)
        
        self.logger.debug("Adding continue_prompt node")
        workflow.add_node('continue_prompt', self.continue_prompt_node)

        # Add connections between nodes
        workflow.set_entry_point("supervisor")
        # workflow.add_edge("supervisor", "evaluation")
        # workflow.add_edge("supervisor", "student_bot")
        # workflow.add_edge("supervisor", "continue_prompt")
        # workflow.add_edge("supervisor", END)
        # workflow.add_edge("evaluation", "continue_prompt")  # Evaluation now goes to continue_prompt
        # workflow.add_edge("student_bot", "supervisor")
        # workflow.add_edge("continue_prompt", "supervisor")
        # workflow.add_edge("continue_prompt", END)

        self.logger.info("Graph compilation complete")

        # Compile graph with checkpointing and interrupt_after to prevent recursion issues
        return workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_after=["student_bot", "continue_prompt"] 
        )

    def update_from_streamlit(self, state_id: str, user_input: str) -> Dict[str, Any]:
        """
        Update the graph state with user input from a Streamlit interface.

        Args:
            state_id: The thread/state ID to update
            user_input: The message from the teacher/user

        Returns:
            Updated state information for the UI
        """
        # Get the thread
        checkpoint = self.checkpointer.get(state_id)
        if not checkpoint:
            self.logger.error(f"No checkpoint found for state ID: {state_id}")
            return {"error": "Session not found"}

        # Create the message
        message = HumanMessage(content=user_input, name="teacher")

        # Get the last graph state
        thread = checkpoint["thread"]

        # Update the state with the new message
        updated_state = thread.update_state(
            {"messages": [message]}
        )

        # Resume the graph execution
        result = thread.resume()

        # Return information useful for the UI
        return {
            "state": result,
            "is_done": result.get("conversation_done", False),
            "ui_metadata": result.get("ui_metadata", {}),
            "continue_conversation": result.get("continue_conversation", False)
        }
