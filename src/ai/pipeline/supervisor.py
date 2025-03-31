from typing import List, Dict, Any, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.ai.pipeline.agent_state import AgentState
from src.ai.pipeline.student_bot import StudentBot, Evaluation
from src.ai.student_profiles import StudentProfile
from src.ai.pipeline.agentTools import set_student_profile_in_state, set_scenario_in_state
from src.logging import AgentLogger, LogLevel
from langgraph.checkpoint.memory import MemorySaver

# List of available agent members
members = ["student", "evaluation"]
# Options including completion state
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["student", "evaluation", "FINISH"]


class Supervisor:
    def __init__(self, model_name: str = "gpt-4o-mini", log_level: LogLevel = LogLevel.INFO):
        self.llm = ChatOpenAI(model=model_name)
        self.student_bot = StudentBot()
        self.evaluation = Evaluation()
        self.checkpointer = MemorySaver()  # For persisting state

        # Initialize logger
        self.logger = AgentLogger.get_logger("Supervisor")
        AgentLogger.set_level(log_level)
        self.logger.info(f"Initializing Supervisor with model: {model_name}")

        self.supervisor_prompt = (
            "You are a supervisor tasked with managing a conversation between a teacher and student."
            " Your job is to decide who should act next based on the conversation context."
            " When the teacher indicates they want to end the conversation, route to evaluation."
        )
        self.logger.debug(f"Supervisor prompt: {self.supervisor_prompt}")

    def initialize_agent_state(self, state: AgentState = None, profile: StudentProfile = None,
                               scenario=None, session_id: str = None) -> AgentState:
        """
        Initialize a complete agent state with a student profile and scenario.

        Args:
            state: Initial state dictionary, will be created if None
            profile: Optional StudentProfile object
            scenario: Optional scenario object
            session_id: Optional session identifier for tracking UI sessions

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

        if scenario:
            title = getattr(scenario, 'title', scenario.get(
                'title', 'Unknown scenario')) if hasattr(scenario, 'get') else 'Unknown scenario'
            self.logger.info(f"Setting scenario: {title}")
            state = set_scenario_in_state(state, scenario)

        if session_id:
            state["session_id"] = session_id

        # Initialize UI metadata
        state["ui_metadata"] = {
            "current_speaker": "system",
            "is_thinking": False,
            "can_interrupt": True
        }

        # Set initial node to human input to wait for the teacher's first message
        state["current_node"] = "humanInput"
        state["conversation_done"] = False

        # Log the complete state at debug level
        AgentLogger.log_state(state, "INITIALIZED STATE")

        return state

    def supervisor(self, state: AgentState) -> Command[Literal["student", "evaluation", "humanInput", END]]:
        """
        Core routing logic that decides which node to go to next.

        Args:
            state: Current agent state

        Returns:
            Command directing to the next node
        """
        self.logger.debug("Supervisor node called")

        # Check if this is the first interaction
        is_first_turn = len(state.get("messages", [])) <= 1

        # Get the last node that was processed
        previous_node = state.get("current_node", None)

        # Check if conversation is marked as done
        if state.get("conversation_done", False):
            return Command(goto=END, update={'current_node': 'FINISH'})

        # Route based on context
        if is_first_turn:
            # If we're just starting, go to human input first
            return Command(goto="humanInput", update={'current_node': 'humanInput'})

        elif previous_node == "humanInput":
            # Check for exit phrases in the last message
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, HumanMessage) and any(phrase in last_message.content.lower() for phrase in
                                                                  ["exit", "quit", "bye", "goodbye", "done", "end", "evaluate"]):
                    # User wants to end conversation, go to evaluation
                    return Command(goto="evaluation",
                                   update={'current_node': 'evaluation',
                                           'ui_metadata': {**state.get("ui_metadata", {}),
                                                           "current_speaker": "system",
                                                           "is_evaluating": True}})
                else:
                    # Normal message, send to student
                    return Command(goto="student",
                                   update={'current_node': 'student',
                                           'ui_metadata': {**state.get("ui_metadata", {}),
                                                           "current_speaker": "student",
                                                           "is_thinking": True}})

        elif previous_node == "student":
            # After student responds, go back to human input for teacher's turn
            return Command(goto="humanInput",
                           update={'current_node': 'humanInput',
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "current_speaker": "teacher",
                                                   "is_thinking": False}})

        elif previous_node == "evaluation":
            # After evaluation is done, end the graph
            return Command(goto=END,
                           update={'current_node': 'FINISH',
                                   'conversation_done': True,
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "is_complete": True}})

        else:
            # Default fallback - go to human input
            return Command(goto="humanInput",
                           update={'current_node': 'humanInput',
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "current_speaker": "teacher"}})

    def get_human_input(self, state: AgentState) -> Command[Literal['supervisor']]:
        """
        Node for handling human input. In a real application, this would be replaced
        with code that receives input from a UI (e.g., Streamlit).

        Args:
            state: Current agent state

        Returns:
            Command with the human input added to messages
        """
        self.logger.debug("Human input node called")

        # This function doesn't actually collect input in the graph
        # It's just a placeholder node that the langgraph interrupt mechanism will pause at
        # The actual input will be injected via update_state from the UI

        # In CLI mode, we'll collect input here for testing
        if state.get("ui_metadata", {}).get("cli_mode", True):
            self.logger.info("CLI mode: Waiting for human input...")
            user_input = input("Teacher: ")
            self.logger.info(f"Human input: {user_input}")

            # Add message to state
            messages = state.get("messages", [])
            updated_messages = messages + \
                [HumanMessage(content=user_input, name="teacher")]

            return Command(
                update={'messages': updated_messages,
                        'current_node': 'humanInput',
                        'ui_metadata': {**state.get("ui_metadata", {}), "last_input": user_input}},
                goto='supervisor'
            )

        # In UI mode, we'll just pass control back to supervisor
        # The actual input will come from the UI via update_state
        return Command(
            update={'current_node': 'humanInput'},
            goto='supervisor'
        )

    def create_supervisor_graph(self) -> CompiledStateGraph:
        """Create the supervisor graph with connected components and checkpointing."""
        self.logger.info("Creating supervisor graph")

        # Create the graph
        workflow = StateGraph(AgentState)

        # Nodes
        self.logger.debug("Adding supervisor node")
        workflow.add_node("supervisor", self.supervisor)

        self.logger.debug("Adding student node")
        workflow.add_node('student', self.student_bot.converse)

        self.logger.debug("Adding evaluation node")
        workflow.add_node('evaluation', self.evaluation.evaluate)

        self.logger.debug("Adding human input node")
        workflow.add_node('humanInput', self.get_human_input)

        # Add connections between nodes
        workflow.set_entry_point("supervisor")
        # workflow.add_edge('supervisor', 'student')
        # workflow.add_edge('supervisor', 'humanInput')
        # workflow.add_edge('supervisor', 'evaluation')
        # workflow.add_edge('supervisor', END)
        # workflow.add_edge('student', 'supervisor')
        # workflow.add_edge('humanInput', 'supervisor')
        # workflow.add_edge('evaluation', 'supervisor')

        self.logger.info("Graph compilation complete")

        # Compile graph with checkpointing and interruption for human-in-the-loop
        return workflow.compile(
            checkpointer=self.checkpointer,
            # Interrupt before humanInput node to allow UI integration
            # interrupt_before=["humanInput"]
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
            {"messages": [message]},
            # Apply this update as if it came from the humanInput node
            as_node="humanInput"
        )

        # Resume the graph execution
        result = thread.resume()

        # Return information useful for the UI
        return {
            "state": result,
            "is_done": result.get("conversation_done", False),
            "ui_metadata": result.get("ui_metadata", {})
        }
