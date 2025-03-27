from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Agent state used across all components in the pipeline."""
    next: str = None
    studentProfile: str = None
    scenario: str = None

