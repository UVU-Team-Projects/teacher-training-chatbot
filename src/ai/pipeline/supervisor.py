from typing import List, Dict, Any, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_openai import ChatOpenAI

from src.ai.pipeline.agent_state import AgentState
from src.ai.pipeline.student_bot import StudentBot
from src.ai.student_profiles import StudentProfile
from src.ai.pipeline.agentTools import set_student_profile_in_state, set_scenario_in_state
from src.logging import AgentLogger, LogLevel

# List of available agent members
members = ["student"]
# Options including completion state
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal[*options]


class Supervisor:
    def __init__(self, model_name: str = "gpt-4o-mini", log_level: LogLevel = LogLevel.INFO):
        self.llm = ChatOpenAI(model=model_name)
        self.logger = AgentLogger.get_logger("Supervisor")
        AgentLogger.set_level(log_level)
        self.logger.info(f"Initializing Supervisor with model: {model_name}")

        self.supervisor_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            f" following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )
        self.logger.debug(f"Supervisor prompt: {self.supervisor_prompt}")

    def initialize_agent_state(self, state: AgentState = None, profile: StudentProfile = None, scenario=None) -> AgentState:
        """
        Initialize a complete agent state with a student profile and scenario.

        Args:
            state: Initial state dictionary, will be created if None
            profile: Optional StudentProfile object
            scenario: Optional scenario object

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

        # Log the complete state at debug level
        AgentLogger.log_state(state, "INITIALIZED STATE")

        return state

    def supervisor(self, state: AgentState) -> Command[Literal[*members, END]]:
        """Supervise the conversation and provide feedback"""
        self.logger.debug("Supervisor node called")
        AgentLogger.log_state(state, "SUPERVISOR INPUT")

        messages = [
            {"role": "system", "content": self.supervisor_prompt}] + state["messages"]

        # Log the last message content
        if state["messages"]:
            last_msg = state["messages"][-1]
            content = last_msg.content if hasattr(
                last_msg, 'content') else str(last_msg)
            sender = last_msg.name if hasattr(last_msg, 'name') else "unknown"
            self.logger.info(
                f"Processing message from {sender}: {content[:50]}...")

        # Generate a response from the supervisor LLM
        self.logger.debug("Invoking LLM for routing decision")
        response = self.llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]

        if goto == "FINISH":
            self.logger.info("Routing decision: FINISH (end of conversation)")
            goto = END
        else:
            self.logger.info(f"Routing decision: {goto}")

        return Command(goto=goto, update={'next': goto})

    def create_supervisor_graph(self) -> CompiledStateGraph:
        """Create the supervisor graph with connected components."""
        self.logger.info("Creating supervisor graph")

        # Create the graph
        workflow = StateGraph(AgentState)
        workflow.set_entry_point("supervisor")

        # Nodes
        self.logger.debug("Adding supervisor node")
        workflow.add_node("supervisor", self.supervisor)

        self.logger.debug("Adding student node")
        workflow.add_node('student', StudentBot().converse)

        self.logger.info("Graph compilation complete")
        return workflow.compile()
