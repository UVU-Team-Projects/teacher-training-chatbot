from typing import List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_openai import ChatOpenAI


class Supervisor:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name)

    def supervisor(self, state: MessagesState) -> Command[Literal["agent1", END]]:
        """Supervise the conversation and provide feedback"""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.type == "human":
            # Generate a response from the LLM
            response = self.llm.invoke(messages)
            messages.append(response)
        return {"messages": messages}

    def create_supervisor_graph(self) -> StateGraph:
        # Implement the graph creation logic here
        workflow = StateGraph(MessagesState)
        workflow.add_node("supervisor", self.supervisor)
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", END)
        return workflow.compile()
