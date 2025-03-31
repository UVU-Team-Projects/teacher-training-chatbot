from typing import List, Dict, Any, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.ai.pipeline.agent_state import AgentState
from src.ai.pipeline.student_bot import StudentBot
from src.ai.pipeline.evaluation import Evaluation
from src.ai.student_profiles import StudentProfile
from src.ai.pipeline.agentTools import set_student_profile_in_state, set_scenario_in_state, get_classroom_management_insights
from src.logging import AgentLogger, LogLevel
from langgraph.checkpoint.memory import MemorySaver
from colorama import Fore, Style

# List of available agent members
members = ["student", "evaluation", "kb_retrieval"]
# Options including completion state
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["student", "evaluation", "kb_retrieval", "FINISH"]


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
            " When the teacher requests classroom management help, route to kb_retrieval."
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

    def supervisor(self, state: AgentState) -> Command[Literal["student", "evaluation", "kb_retrieval", "humanInput", END]]:
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
        
        # Track conversation turns
        current_turns = state.get("conversation_turns", 0)
        max_turns = state.get("max_turns_without_reset", 15)
        
        # Increment the turn counter
        current_turns += 1
        self.logger.debug(f"Conversation turn #{current_turns}")
        
        # Check if we need to reset the turn counter to prevent hitting recursion limits
        # We only reset during normal teacher-student exchange patterns
        if previous_node == "student" and current_turns > max_turns / 2:
            self.logger.info(f"Resetting conversation turn counter (was at {current_turns})")
            current_turns = 1
        
        # Check if conversation is marked as done
        if state.get("conversation_done", False):
            return Command(goto=END, update={'current_node': 'FINISH'})

        # Route based on context
        if is_first_turn:
            # If we're just starting, go to human input first
            return Command(goto="humanInput", update={
                'current_node': 'humanInput',
                'conversation_turns': 1  # Reset at the beginning
            })

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
                                           'conversation_turns': current_turns,
                                           'ui_metadata': {**state.get("ui_metadata", {}),
                                                           "current_speaker": "system",
                                                           "is_evaluating": True}})
                elif isinstance(last_message, HumanMessage) and any(phrase in last_message.content.lower() for phrase in
                                                                  ["help me with this", "classroom management", "management advice", "what should I do", "strategies for"]):
                    # User wants classroom management help
                    return Command(goto="kb_retrieval",
                                   update={'current_node': 'kb_retrieval',
                                           'conversation_turns': current_turns,
                                           'ui_metadata': {**state.get("ui_metadata", {}),
                                                           "current_speaker": "system",
                                                           "is_retrieving": True}})
                else:
                    # Normal message, send to student
                    return Command(goto="student",
                                   update={'current_node': 'student',
                                           'conversation_turns': current_turns,
                                           'ui_metadata': {**state.get("ui_metadata", {}),
                                                           "current_speaker": "student",
                                                           "is_thinking": True}})

        elif previous_node == "student":
            # After student responds, go back to human input for teacher's turn
            return Command(goto="humanInput",
                           update={'current_node': 'humanInput',
                                   'conversation_turns': current_turns,
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "current_speaker": "teacher",
                                                   "is_thinking": False}})
        
        elif previous_node == "kb_retrieval":
            # After knowledge base retrieval, go back to human input
            return Command(goto="humanInput",
                           update={'current_node': 'humanInput',
                                   'conversation_turns': current_turns,
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "current_speaker": "teacher",
                                                   "is_thinking": False,
                                                   "is_retrieving": False}})

        elif previous_node == "evaluation":
            # After evaluation is done, end the graph
            return Command(goto=END,
                           update={'current_node': 'FINISH',
                                   'conversation_done': True,
                                   'conversation_turns': 1, # Reset for any future use
                                   'ui_metadata': {**state.get("ui_metadata", {}),
                                                   "is_complete": True}})

        else:
            # Default fallback - go to human input
            return Command(goto="humanInput",
                           update={'current_node': 'humanInput',
                                   'conversation_turns': current_turns,
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

        # Suggest classroom management support for new teachers
        student_response = None
        messages = state.get("messages", [])
        
        # Check if the last message was from the student
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if hasattr(last_message, 'name') and last_message.name != "teacher" and last_message.name != "classroom_insights":
                student_response = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # If we have a student response, check if it might need classroom management help
        if student_response:
            try:
                # Use a lightweight check to see if classroom management help might be useful
                challenging_indicators = [
                    "don't want to", "won't", "can't make me", "not fair", "whatever", 
                    "stupid", "hate", "boring", "don't care", "why should I",
                    "no way", "not doing", "shut up", "leave me alone"
                ]
                
                if any(indicator in student_response.lower() for indicator in challenging_indicators):
                    # This seems like a situation where classroom management help might be useful
                    print(f"\n{Fore.YELLOW}Tip: This may be a challenging classroom situation. Ask for classroom management help by including 'classroom management' or 'what should I do' in your response.{Style.RESET_ALL}")
            except Exception as e:
                self.logger.error(f"Error suggesting classroom management help: {str(e)}")

        # In CLI mode, we'll collect input here for testing
        if state.get("ui_metadata", {}).get("cli_mode", True):
            self.logger.info("CLI mode: Waiting for human input...")
            # Get user input
            user_input = input(f"{Fore.GREEN}Teacher: {Style.RESET_ALL}")
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

    def kb_retrieval(self, state: AgentState) -> Command[Literal['supervisor']]:
        """
        Node for retrieving classroom management knowledge.
        
        Args:
            state: Current agent state
            
        Returns:
            Command with classroom management insights
        """
        self.logger.info("Knowledge base retrieval node called")
        
        # Extract any specific query from the last message
        messages = state.get("messages", [])
        query = None
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, HumanMessage):
                content = last_message.content.lower()
                # Check if there's a specific query after trigger phrases
                triggers = ["classroom management", "help me with", "what should i do about", "strategies for"]
                for trigger in triggers:
                    if trigger in content:
                        # Extract the query that follows the trigger
                        query = content.split(trigger, 1)[1].strip()
                        if query:
                            self.logger.info(f"Extracted specific query: {query}")
                            break
        
        # Retrieve classroom management insights
        updated_state = get_classroom_management_insights.func(state, query)
        kb_insights = updated_state.get("kb_insights", {})
        
        # Format insights as a message
        if isinstance(kb_insights, str):
            insights_message = kb_insights
        else:
            insights_message = kb_insights.get("summary", "No relevant insights found.")
        
        # Add message to state
        messages = state.get("messages", [])
        updated_messages = messages + [AIMessage(content=insights_message, name="classroom_insights")]
        
        # Update UI metadata
        ui_metadata = state.get("ui_metadata", {})
        ui_metadata.update({
            "current_speaker": "system",
            "is_retrieving": False,
            "last_kb_query": query or "Generated from conversation",
            "has_kb_insights": True
        })
        
        return Command(
            update={
                'messages': updated_messages,
                'kb_insights': kb_insights,
                'current_node': 'kb_retrieval',
                'ui_metadata': ui_metadata
            },
            goto='supervisor'
        )

    def create_supervisor_graph(self) -> CompiledStateGraph:
        """
        Create the workflow graph for the supervisor.

        Returns:
            Compiled workflow graph
        """
        self.logger.info("Creating supervisor graph")

        # Initialize the graph
        workflow = StateGraph(AgentState)

        # Add nodes for each agent
        workflow.add_node("supervisor", self.supervisor)
        workflow.add_node("student", self.student_bot.converse)
        workflow.add_node("evaluation", self.evaluation.evaluate)
        workflow.add_node("humanInput", self.get_human_input)
        workflow.add_node("kb_retrieval", self.kb_retrieval)

        # Set the entry point
        workflow.set_entry_point("supervisor")

        # Compile the graph with an increased recursion limit
        # This allows for longer conversations while preventing infinite loops
        checkpointer = MemorySaver()
        self.logger.info("Compiling supervisor graph")
        return workflow.compile(checkpointer=checkpointer)

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
