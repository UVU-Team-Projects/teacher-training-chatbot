from langgraph.graph import MessagesState
from typing import List, Dict, Any, Optional


class AgentState(MessagesState):
    """Agent state used across all components in the pipeline."""
    current_node: str = None
    studentProfile: str = None
    scenario: str = None

    # Fields for UI integration
    session_id: str = None
    ui_metadata: Dict[str, Any] = None
    conversation_done: bool = False
    evaluation_results: Dict[str, Any] = None
