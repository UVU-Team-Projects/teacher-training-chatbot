from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional, Literal
from langchain_core.tools import BaseTool
from src.ai.pipeline.agent_state import AgentState
from src.ai.pipeline.agentTools import get_student_profile, get_scenario
from src.logging import AgentLogger
from colorama import Fore, Style


class StudentBot:
    def __init__(self, model_name: str = 'gpt-4o-mini', tools: List[BaseTool] = [get_student_profile, get_scenario]):
        self.llm = ChatOpenAI(model=model_name).bind_tools(tools)
        self.prompt_sent = False
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
        self.prompt_sent = True

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
        if isinstance(student_profile, str) and "Name:" in student_profile:
            try:
                name_line = [line for line in student_profile.split(
                    '\n') if "Name:" in line][0]
                student_name = name_line.split("Name:")[1].strip()
                self.logger.debug(f"Extracted student name: {student_name}")
            except:
                self.logger.warning(
                    "Failed to extract student name from profile")
        elif hasattr(student_profile, "name"):
            student_name = student_profile.name

        # Print out the response
        print(f"\n{Fore.BLUE}Student: {response_content}{Style.RESET_ALL}")

        # Update UI metadata with response information
        ui_metadata = state.get("ui_metadata", {})
        ui_metadata.update({
            "current_speaker": "student",
            "is_thinking": False,
            "student_name": student_name,
            "last_response": response_content[:50] + "..." if len(response_content) > 50 else response_content
        })

        # Return result with student name
        self.logger.debug("Returning Command with updated messages")
        return Command(
            update={'messages': messages +
                    [HumanMessage(content=response_content,
                                  name=student_name)],
                    'current_node': 'student',
                    'ui_metadata': ui_metadata},
            goto='supervisor'
        )


class Evaluation:
    """
    This class is used to evaluate the conversation between the student and the teacher.
    Only called when the user ends the conversation.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name)
        self.logger = AgentLogger.get_logger("Evaluation")

    def evaluate(self, state: AgentState) -> Command[Literal['supervisor']]:
        """
        Evaluate the conversation between teacher and student.

        Args:
            state: Current agent state

        Returns:
            Command with evaluation results
        """
        self.logger.info("Running conversation evaluation")

        messages = state.get("messages", [])
        student_profile = state.get("studentProfile", "No profile available")
        scenario = state.get("scenario", "No scenario available")

        # Skip if there aren't enough messages
        if len(messages) < 3:
            self.logger.warning("Not enough messages to evaluate")
            evaluation_results = {
                "summary": "Conversation was too short to evaluate.",
                "effectiveness": "N/A",
                "authenticity": "N/A",
                "suggestions": ["Have a longer conversation to receive meaningful feedback."]
            }
        else:
            # Create evaluation prompt
            evaluation_prompt = f"""
            You are an educational expert evaluating a teacher-student interaction.
            
            STUDENT PROFILE:
            {student_profile}
            
            SCENARIO:
            {scenario}
            
            Analyze the following conversation between a teacher and student.
            Evaluate how well the teacher addressed the student's needs based on their profile.
            
            CONVERSATION:
            {[f"{msg.name if hasattr(msg, 'name') else 'Unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
             for msg in messages]}
            
            Provide the following in your evaluation:
            1. Summary of the interaction
            2. Effectiveness score (1-10) with explanation
            3. Authenticity score (1-10) for how well the student was portrayed
            4. Specific suggestions for improvement
            
            Format your response as JSON with the following keys:
            summary, effectiveness, authenticity, suggestions
            """

            # Get evaluation from LLM
            try:
                self.logger.debug("Sending evaluation prompt to LLM")
                result = self.llm.invoke(evaluation_prompt)

                response_content = result.content if hasattr(
                    result, 'content') else str(result)

                # Try to parse as JSON, fallback to text if not valid JSON
                try:
                    import json
                    import re

                    # Extract JSON if it's wrapped in backticks
                    json_match = re.search(
                        r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = response_content

                    evaluation_results = json.loads(json_str)
                    self.logger.debug(
                        "Successfully parsed evaluation results as JSON")
                except:
                    self.logger.warning(
                        "Could not parse evaluation as JSON, using raw text")
                    evaluation_results = {
                        "summary": response_content[:500],
                        "effectiveness": "See summary",
                        "authenticity": "See summary",
                        "suggestions": ["See summary for details"]
                    }
            except Exception as e:
                self.logger.error(f"Error during evaluation: {str(e)}")
                evaluation_results = {
                    "summary": f"Error during evaluation: {str(e)}",
                    "effectiveness": "Error",
                    "authenticity": "Error",
                    "suggestions": ["Try again later."]
                }

        # Print evaluation results
        print("\n" + "="*50)
        print(f"{Fore.GREEN}CONVERSATION EVALUATION:{Style.RESET_ALL}")
        print(
            f"Summary: {evaluation_results.get('summary', 'No summary available')}")
        print(
            f"Effectiveness: {evaluation_results.get('effectiveness', 'N/A')}")
        print(f"Authenticity: {evaluation_results.get('authenticity', 'N/A')}")
        print("Suggestions:")
        for suggestion in evaluation_results.get('suggestions', ['No suggestions available']):
            print(f"- {suggestion}")
        print("="*50)

        # Update UI metadata
        ui_metadata = state.get("ui_metadata", {})
        ui_metadata.update({
            "is_evaluating": False,
            "is_complete": True,
            "evaluation_complete": True
        })

        return Command(
            update={
                'current_node': 'evaluation',
                'evaluation_results': evaluation_results,
                'conversation_done': True,
                'ui_metadata': ui_metadata
            },
            goto='supervisor'
        )
