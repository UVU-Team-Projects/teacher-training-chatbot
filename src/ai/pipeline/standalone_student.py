from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from src.ai.pipeline.agentTools import get_student_profile, get_scenario
from src.logging import AgentLogger
from colorama import Fore, Style
from src.ai.student_profiles import StudentProfile


class StandaloneStudentBot:
    """
    A standalone student bot implementation that can be used
    independently of the LangGraph pipeline.
    """

    def __init__(self, model_name: str = 'gpt-4o-mini', tools: List[BaseTool] = [get_student_profile, get_scenario]):
        self.llm = ChatOpenAI(model=model_name).bind_tools(tools)
        self.logger = AgentLogger.get_logger("StandaloneStudentBot")
        self.logger.info(f"Initializing StandaloneStudentBot with model: {model_name}")
        self.logger.debug(f"Tools available: {[tool.name for tool in tools]}")
        self.profile = None
        self.scenario = None
        self.messages = []
        self.student_name = "student"
        self.system_prompt = ""

    def initialize(self, profile: StudentProfile, scenario: Dict[str, Any]) -> None:
        """
        Initialize the student bot with a profile and scenario.

        Args:
            profile: Student profile object
            scenario: Scenario dictionary
        """
        self.profile = profile
        self.scenario = scenario
        self.messages = []

        # Extract student name from profile if possible
        if hasattr(profile, "name"):
            self.student_name = profile.name
        
        # Create the system prompt for the LLM
        student_profile_str = str(profile)
        scenario_str = str(scenario)
        
        self.system_prompt = f"""
        You are roleplaying as a student in a class based on the following profile and scenario.
        Speak in the first person, as a student of your grade level would speak.
        Make your responses authentic to how a real student with your profile would respond in this situation.
        
        {student_profile_str}
        
        {scenario_str}
        
        Instructions:
        1. Stay in character as this student at all times
        2. Use vocabulary and sentence structure appropriate for your grade level
        3. Keep your responses short and concise
        4. Express emotions and reactions consistent with your profile
        5. Reference your interests, strengths, or challenges when appropriate
        6. Respond to the teacher's messages naturally as this student would
        """
        
        self.logger.info("Student bot initialized with profile and scenario")
        self.logger.debug(f"Student name: {self.student_name}")

    def get_response(self, teacher_message: str) -> str:
        """
        Get a response from the student bot based on the teacher's message.

        Args:
            teacher_message: The message from the teacher

        Returns:
            The student's response
        """
        self.logger.info(f"Processing teacher message: {teacher_message[:50]}...")
        
        # Add the teacher's message to the conversation history
        teacher_msg = HumanMessage(content=teacher_message, name="teacher")
        self.messages.append(teacher_msg)
        
        # Create full message list with system prompt and all conversation history
        full_messages = [SystemMessage(content=self.system_prompt)] + self.messages
        
        # Generate response from the LLM
        self.logger.info("Generating student response with LLM")
        result = self.llm.invoke(full_messages)
        
        response_content = result.content if hasattr(result, 'content') else str(result)
        self.logger.info(f"Generated response: {response_content[:50]}...")
        
        # Add the student's response to the conversation history
        student_msg = HumanMessage(content=response_content, name=self.student_name)
        self.messages.append(student_msg)
        
        # Print out the response
        print(f"\n{Fore.BLUE}Student ({self.student_name}): {response_content}{Style.RESET_ALL}")
        
        return response_content

    def get_conversation_history(self) -> List[HumanMessage]:
        """
        Get the full conversation history.

        Returns:
            List of messages from the conversation
        """
        return self.messages
    
    def end_conversation(self) -> Dict[str, Any]:
        """
        End the conversation and return metadata.

        Returns:
            Dictionary with metadata about the conversation
        """
        self.logger.info("Ending conversation")
        
        message_count = len(self.messages)
        student_messages = [msg for msg in self.messages if hasattr(msg, 'name') and msg.name == self.student_name]
        teacher_messages = [msg for msg in self.messages if hasattr(msg, 'name') and msg.name == "teacher"]
        
        return {
            "message_count": message_count,
            "student_message_count": len(student_messages),
            "teacher_message_count": len(teacher_messages),
            "student_name": self.student_name
        } 