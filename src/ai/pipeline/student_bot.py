from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional, Literal
from langchain_core.tools import BaseTool
from src.ai.pipeline.agent_state import AgentState
from src.ai.pipeline.agentTools import get_student_profile, get_scenario
from src.logging import AgentLogger


class StudentBot:
    def __init__(self, model_name: str = 'gpt-4o-mini', tools: List[BaseTool] = [get_student_profile, get_scenario]):
        self.llm = ChatOpenAI(model=model_name).bind_tools(tools)
        self.logger = AgentLogger.get_logger("StudentBot")
        self.logger.info(f"Initializing StudentBot with model: {model_name}")
        self.logger.debug(f"Tools available: {[tool.name for tool in tools]}")

    def converse(self, state: AgentState) -> Command[Literal['supervisor']]:
        self.logger.debug("StudentBot.converse called")
        AgentLogger.log_state(state, "STUDENT INPUT")

        # Get student profile and scenario from state
        student_profile = state.get("studentProfile", "No profile available")
        scenario = state.get("scenario", "No scenario available")

        self.logger.debug("Retrieved profile and scenario from state")

        # Create a comprehensive system prompt for the LLM
        system_prompt = f"""
        You are roleplaying as a student in a class based on the following profile and scenario.
        Speak in the first person, as a student of your grade level would speak.
        Make your responses authentic to how a real student with your profile would respond in this situation.
        
        {student_profile}
        
        {scenario}
        
        Instructions:
        1. Stay in character as this student at all times
        2. Use vocabulary and sentence structure appropriate for your grade level
        3. Keep your responses short and concise
        4. Express emotions and reactions consistent with your profile
        5. Reference your interests, strengths, or challenges when appropriate
        6. Respond to the teacher's messages naturally as this student would
        """

        self.logger.debug("Created system prompt for LLM")

        # Create system message and get last message from state
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None

        if last_message:
            content = last_message.content if hasattr(
                last_message, 'content') else str(last_message)
            sender = last_message.name if hasattr(
                last_message, 'name') else "unknown"
            self.logger.info(
                f"Responding to message from {sender}: {content[:50]}...")
        else:
            self.logger.warning("No messages found in state")

        # Create full message list with system prompt
        full_messages = [SystemMessage(content=system_prompt)]
        if last_message:
            full_messages.append(last_message)

        # Generate response from the LLM
        self.logger.info("Generating student response with LLM")
        result = self.llm.invoke(full_messages)

        response_content = result.content if hasattr(
            result, 'content') else str(result)
        self.logger.info(f"Generated response: {response_content[:50]}...")

        # Extract student name from profile if possible
        student_name = "student"
        if "Name:" in student_profile:
            try:
                name_line = [line for line in student_profile.split(
                    '\n') if "Name:" in line][0]
                student_name = name_line.split("Name:")[1].strip()
                self.logger.debug(f"Extracted student name: {student_name}")
            except:
                self.logger.warning(
                    "Failed to extract student name from profile")

        # Return result with student name
        self.logger.debug("Returning Command with updated messages")
        return Command(
            update={'messages': messages +
                    [HumanMessage(content=response_content, name='student')]},
            goto='supervisor'
        )
