from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any, Optional, Tuple, Union
from langchain_core.tools import BaseTool
from src.logging import AgentLogger, LogLevel
from colorama import Fore, Style
from src.ai.student_profiles import StudentProfile
from src.ai.embedding import EmbeddingGenerator
import json
import os
from datetime import datetime

class KnowledgeBaseRetriever:
    """
    A standalone knowledge base retriever that uses RAG to search for relevant information
    using a Chroma vector store.
    """

    def __init__(self): # model_name is no longer directly used here but kept for potential future use
        """
        Initialize the knowledge base retriever.
        """
        self.logger = AgentLogger.get_logger("KnowledgeBaseRetriever")
        self.logger.info(f"Initializing KnowledgeBaseRetriever using ChromaDB.")

        # Initialize EmbeddingGenerator and ChromaDB
        self.embedder = EmbeddingGenerator()
        self.db = self.embedder.return_chroma()

        if self.db is None:
            self.logger.error("Failed to initialize ChromaDB. Knowledge base retrieval will not work.")
            self.retriever = None
        else:
            # Set up the retriever
            self.retriever = self.db.as_retriever(search_kwargs={'k': 3}) # Retrieve top 3 results
            self.logger.info("ChromaDB retriever initialized successfully.")

    def query(self, question: str) -> str:
        """
        Query the ChromaDB knowledge base to find relevant information using RAG.

        Args:
            question: The query to search for

        Returns:
            A string containing the formatted relevant documents, or an error message.
        """
        self.logger.info(f"Querying knowledge base: {question[:50]}...")

        if self.retriever is None:
            error_msg = "Error: Knowledge base retriever not initialized."
            self.logger.error(error_msg)
            return error_msg

        try:
            # Use the retriever to get relevant documents
            retrieved_docs = self.retriever.invoke(question)

            # Format the documents into a single string
            response_content = "\n---\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}" for doc in retrieved_docs])

            if not response_content:
                response_content = "No relevant information found in the knowledge base."

            self.logger.info(f"Knowledge base response generated from {len(retrieved_docs)} documents.")

            # Format the response for display
            formatted_response = (
                f"\\n{Fore.MAGENTA}Knowledge Base:{Style.RESET_ALL}\\n"
                f"{response_content}\\n"
                f"{'-' * 50}\\n"
            )

            print(formatted_response)

            return response_content

        except Exception as e:
            self.logger.error(f"Error querying knowledge base: {str(e)}")
            return f"Error querying knowledge base: {str(e)}"


class StandaloneStudentBot:
    """Standalone implementation of a student bot for teacher training."""
    
    def __init__(
        self, 
        student_profile: Union[Dict[str, Any], StudentProfile], 
        scenario: Dict[str, Any],
        model_name: str = "gpt-4o-mini",
        conversation_history: List[Dict[str, Any]] = None,
        knowledge_base: Optional[KnowledgeBaseRetriever] = None
    ):
        """Initialize the student bot with the given profile and scenario.
        
        Args:
            student_profile: The profile of the student to simulate.
            scenario: The scenario context for the conversation.
            model_name: The name of the model to use.
            conversation_history: Optional initial conversation history.
            knowledge_base: Optional knowledge base retriever.
        """
        self.logger = AgentLogger.get_logger("StandaloneStudentBot")
        self.logger.info(f"Initializing StandaloneStudentBot with model {model_name}")
        
        # Convert dict to StudentProfile if needed
        if isinstance(student_profile, dict):
            # Assume the dict has the right structure
            self.profile = student_profile
        else:
            self.profile = student_profile
            
        self.scenario = scenario
        self.model_name = model_name
        self.conversation_history = conversation_history or []
        
        # Set student name from profile
        self.student_name = self.profile.name if hasattr(self.profile, "name") else "student"
        
        # Configure the knowledge base retriever
        if knowledge_base is None:
            self.kb_retriever = KnowledgeBaseRetriever()
        else:
            self.kb_retriever = knowledge_base
        
        # Initialize the language model
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        
        # Build the system prompt
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the student bot based on the profile and scenario.
        
        Returns:
            The system prompt string.
        """
        # Extract profile information
        if hasattr(self.profile, "name"):
            name = self.profile.name
            grade = self.profile.grade_level
            interests = ", ".join([str(interest) for interest in self.profile.interests])
            strengths = ", ".join(self.profile.academic_strengths)
            challenges = ", ".join(self.profile.academic_challenges)
            supports = ", ".join(self.profile.support_strategies)
        else:
            # Handle dictionary profile
            name = self.profile.get("name", "Student")
            grade = self.profile.get("grade_level", "Unknown")
            interests = ", ".join([str(i) for i in self.profile.get("interests", [])])
            strengths = ", ".join(self.profile.get("academic_strengths", []))
            challenges = ", ".join(self.profile.get("academic_challenges", []))
            supports = ", ".join(self.profile.get("support_strategies", []))
        
        # Extract scenario information
        scenario_title = self.scenario.get("title", "Unknown Scenario")
        scenario_desc = self.scenario.get("description", "No description available")
        
        # Build the system prompt
        system_prompt = f"""
        You are simulating a student named {name} in grade {grade}. 
        
        # Your Profile
        - Name: {name}
        - Grade: {grade}
        - Interests: {interests}
        - Academic Strengths: {strengths}
        - Academic Challenges: {challenges}
        - Effective Support Strategies: {supports}
        
        # Current Scenario
        {scenario_title}: {scenario_desc}
        
        # Instructions
        1. Stay in character as this student at all times.
        2. Respond authentically based on your profile and the scenario.
        3. Your responses should reflect your grade level vocabulary and knowledge.
        4. When faced with challenges related to your profile, display realistic behaviors.
        5. Be responsive to effective support strategies when teachers use them.
        6. Do not break character or reveal that you are an AI.
        7. Keep responses concise and conversational, appropriate for a student of your age.
        8. Do not explain your reasoning or mention that you're following instructions.
        
        Respond as if you are directly speaking as {name}.
        """
        
        return system_prompt.strip()
    
    def get_response(self, teacher_message: str) -> str:
        """Generate a response to the teacher's message.
        
        Args:
            teacher_message: The message from the teacher.
            
        Returns:
            The student's response.
        """
        self.logger.info(f"Generating student response to: {teacher_message}")
        
        # Convert conversation history to LangChain format
        messages = [SystemMessage(content=self.system_prompt)]
        
        for message in self.conversation_history:
            if message["role"] == "teacher":
                messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "student":
                messages.append(AIMessage(content=message["content"]))
        
        # Add the current message
        messages.append(HumanMessage(content=teacher_message))
        
        # Generate response
        response = self.llm.invoke(messages)
        student_response = response.content
        
        # Update conversation history
        self.conversation_history.append({"role": "teacher", "content": teacher_message})
        self.conversation_history.append({"role": "student", "content": student_response})
        
        return student_response
    
    def generate_response(self, teacher_message: str) -> str:
        """Alias for get_response for backward compatibility."""
        return self.get_response(teacher_message)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history.
        
        Returns:
            The conversation history.
        """
        return self.conversation_history
    
    def end_conversation(self) -> Dict[str, Any]:
        """End the conversation and return metadata.
        
        Returns:
            A dictionary containing metadata about the conversation.
        """
        self.logger.info("Ending conversation")
        
        # Calculate basic stats
        message_count = len(self.conversation_history)
        teacher_messages = [m for m in self.conversation_history if m["role"] == "teacher"]
        student_messages = [m for m in self.conversation_history if m["role"] == "student"]
        
        return {
            "message_count": message_count,
            "teacher_message_count": len(teacher_messages),
            "student_message_count": len(student_messages),
            "student_name": self.student_name
        }


class StandaloneEvaluator:
    """Evaluator for teacher-student conversations."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the evaluator.
        
        Args:
            model_name: The name of the model to use.
            knowledge_base: Optional knowledge base retriever.
        """
        self.logger = AgentLogger.get_logger("StandaloneEvaluator")
        self.logger.info(f"Initializing StandaloneEvaluator with model {model_name}")
        self.model_name = model_name
        self.knowledge_base = KnowledgeBaseRetriever()
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
    
    def evaluate(
        self, 
        conversation_history: List[Dict[str, Any]],
        student_profile: Union[Dict[str, Any], StudentProfile],
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate the conversation between teacher and student.
        
        Args:
            conversation_history: The conversation history to evaluate.
            student_profile: The profile of the student.
            scenario: The scenario context.
            
        Returns:
            A dictionary containing the evaluation results.
        """
        self.logger.info("Evaluating conversation")
        
        # Convert profile to dict if needed
        if not isinstance(student_profile, dict):
            profile_dict = {
                "name": student_profile.name,
                "grade_level": student_profile.grade_level,
                "interests": [str(i) for i in student_profile.interests],
                "academic_strengths": student_profile.academic_strengths,
                "academic_challenges": student_profile.academic_challenges,
                "support_strategies": student_profile.support_strategies
            }
        else:
            profile_dict = student_profile
        
        # Convert scenario to dict with JSON serializable values
        if isinstance(scenario, dict):
            # Create a copy of the scenario with all values converted to JSON serializable types
            scenario_dict = {}
            for key, value in scenario.items():
                # Convert enum values to strings
                if hasattr(value, "__module__") and "enum" in value.__module__.lower():
                    scenario_dict[key] = str(value)
                else:
                    scenario_dict[key] = value
        else:
            # If it's not a dict, convert to string
            scenario_dict = {"description": str(scenario)}
        
        # Format conversation for the prompt
        conversation_text = ""
        for message in conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "teacher":
                conversation_text += f"Teacher: {content}\n\n"
            elif role == "student":
                conversation_text += f"Student: {content}\n\n"
        
        # Query the knowledge base if available
        kb_info = ""
        if self.knowledge_base:
            kb_query = f"teaching strategies for {scenario_dict.get('challenge_type', 'behavioral')} challenges in {scenario_dict.get('grade_level', 'elementary')} {scenario_dict.get('subject', 'classroom')}"
            kb_info = self.knowledge_base.query(kb_query)
            
            # Also query for student profile specific strategies
            profile_query = f"teaching strategies for students with {', '.join(profile_dict.get('academic_challenges', []))}"
            profile_kb_info = self.knowledge_base.query(profile_query)
            kb_info += "\n\n" + profile_kb_info
        
        # Create the evaluation prompt
        evaluation_prompt = f"""
        You are an expert teacher mentor tasked with evaluating a conversation between a teacher and a student.
        
        # Student Profile
        ```json
        {json.dumps(profile_dict, indent=2)}
        ```
        
        # Scenario
        ```json
        {json.dumps(scenario_dict, indent=2)}
        ```
        
        # Conversation
        {conversation_text}
        
        # Relevant Teaching Best Practices
        {kb_info}
        
        # Evaluation Task
        Evaluate the teacher's interaction with the student based on:
        1. Effectiveness in addressing the scenario challenge
        2. Appropriateness of responses to the student's needs
        3. Alignment with teaching best practices
        4. Authenticity of the interaction
        
        Provide a structured evaluation in the following JSON format:
        ```json
        {{
            "summary": "Brief summary of the interaction (1-2 sentences)",
            "effectiveness": "Score from 1-10 with brief explanation",
            "authenticity": "Score from 1-10 with brief explanation",
            "best_practices_alignment": "Analysis of how well the teacher followed best practices",
            "strengths": ["Strength 1", "Strength 2", "etc."],
            "areas_for_improvement": ["Area 1", "Area 2", "etc."],
            "suggestions": ["Specific suggestion 1", "Specific suggestion 2", "etc."]
        }}
        ```
        
        Respond ONLY with the JSON evaluation. Do not include any other text.
        """
        
        # Get evaluation
        messages = [SystemMessage(content=evaluation_prompt)]
        response = self.llm.invoke(messages)
        
        # Extract JSON from response
        evaluation_text = response.content
        
        # Clean up the response to extract just the JSON
        evaluation_text = evaluation_text.strip()
        if evaluation_text.startswith("```json"):
            evaluation_text = evaluation_text[7:]
        if evaluation_text.endswith("```"):
            evaluation_text = evaluation_text[:-3]
        
        # Parse the JSON
        try:
            evaluation_results = json.loads(evaluation_text.strip())
        except json.JSONDecodeError:
            # If JSON parsing fails, return a simple evaluation
            self.logger.error(f"Failed to parse evaluation results: {evaluation_text}")
            evaluation_results = {
                "summary": "Evaluation could not be properly formatted.",
                "effectiveness": "N/A",
                "authenticity": "N/A",
                "suggestions": ["Try again with a more complete conversation."]
            }
        
        return evaluation_results


class ConversationManager:
    """
    Manages the conversation flow between the teacher, student bot, and evaluator.
    """
    
    def __init__(
        self,
        student_profile: Union[Dict[str, Any], StudentProfile],
        scenario: Dict[str, Any],
        model_name: str = "gpt-4o-mini",
        evaluator_model: str = "gpt-4o-mini"
    ):
        """
        Initialize the conversation manager.
        
        Args:
            student_profile: The profile of the student to simulate.
            scenario: The scenario context for the conversation.
            model_name: The name of the language model to use for the student bot.
            evaluator_model: The name of the language model to use for the evaluator.
        """
        self.logger = AgentLogger.get_logger("ConversationManager")
        self.logger.info(f"Initializing ConversationManager with models: {model_name}, {evaluator_model}")
        
        # Initialize components
        self.student_bot = StandaloneStudentBot(
            student_profile=student_profile,
            scenario=scenario,
            model_name=model_name
        )
        self.evaluator = StandaloneEvaluator(model_name=evaluator_model)
        self.kb_retriever = KnowledgeBaseRetriever()
        
        # Store profile and scenario
        self.student_profile = student_profile
        self.scenario = scenario
        
        # Conversation state
        self.conversation_done = False
        self.evaluation_results = None
        
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message from the teacher.
        
        Args:
            message: The message from the teacher
            
        Returns:
            A dictionary containing the response type and content.
        """
        self.logger.info(f"Processing message: {message[:50]}...")
        
        # Check if the conversation is done and no evaluation yet
        if self.conversation_done and not self.evaluation_results:
            # Run evaluation
            self.evaluation_results = self.evaluator.evaluate(
                conversation_history=self.student_bot.get_conversation_history(),
                student_profile=self.student_profile,
                scenario=self.scenario
            )
            
            return {
                "type": "evaluation",
                "evaluation_results": self.evaluation_results
            }
        
        # Check if the message is a knowledge base query
        if message.startswith("kb:") or message.startswith("KB:"):
            query = message[3:].strip()
            kb_response = self.kb_retriever.query(query)
            
            return {
                "type": "knowledge_base",
                "text": kb_response
            }
        
        # Check if the message indicates the end of the conversation
        if message.lower() in ["end", "end conversation", "finish", "evaluate"]:
            self.conversation_done = True
            
            # Run evaluation
            self.evaluation_results = self.evaluator.evaluate(
                conversation_history=self.student_bot.get_conversation_history(),
                student_profile=self.student_profile,
                scenario=self.scenario
            )
            
            return {
                "type": "evaluation",
                "evaluation_results": self.evaluation_results
            }
        
        # Regular message - get response from student bot
        student_response = self.student_bot.get_response(message)
        
        return {
            "type": "student",
            "text": student_response
        }
        
    def continue_conversation(self, continue_flag: bool) -> bool:
        """
        Handle the continuation of the conversation after evaluation.
        
        Args:
            continue_flag: Whether to continue the conversation or not.
            
        Returns:
            True if the conversation was continued, False otherwise.
        """
        if continue_flag:
            # Reset conversation state to continue
            self.conversation_done = False
            self.evaluation_results = None
            return True
        else:
            # End the conversation
            return False
            
    def save_conversation(self, output_dir: str = "conversation_logs") -> str:
        """Save the conversation to a file.
        
        Args:
            output_dir: The directory to save the conversation to.
            
        Returns:
            The path to the saved conversation file.
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/conversation_{timestamp}.json"
        
        # Convert profile to JSON serializable format if needed
        if hasattr(self.student_profile, "__dict__"):
            profile_dict = {}
            for key, value in self.student_profile.__dict__.items():
                # Handle enum values
                if hasattr(value, "__module__") and "enum" in value.__module__.lower():
                    profile_dict[key] = str(value)
                # Handle lists of enums
                elif isinstance(value, list) and all(hasattr(item, "__module__") and "enum" in item.__module__.lower() for item in value if hasattr(item, "__module__")):
                    profile_dict[key] = [str(item) for item in value]
                else:
                    profile_dict[key] = value
        else:
            profile_dict = self.student_profile
        
        # Convert scenario to JSON serializable format
        scenario_dict = {}
        if isinstance(self.scenario, dict):
            for key, value in self.scenario.items():
                # Handle enum values
                if hasattr(value, "__module__") and "enum" in value.__module__.lower():
                    scenario_dict[key] = str(value)
                else:
                    scenario_dict[key] = value
        else:
            scenario_dict = {"description": str(self.scenario)}
        
        # Prepare the data to save
        data = {
            "student_profile": profile_dict,
            "scenario": scenario_dict,
            "conversation_history": self.student_bot.get_conversation_history(),
            "evaluation_results": self.evaluation_results
        }
        
        # Save the data
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Saved conversation to {filename}")
        return filename


# Helper functions for Streamlit integration
def initialize_conversation_manager(
    profile: Union[Dict[str, Any], StudentProfile],
    scenario: Dict[str, Any],
    model_name: str = "gpt-4o-mini",
    evaluator_model: str = "gpt-4o-mini",
    log_level: LogLevel = LogLevel.INFO
) -> ConversationManager:
    """Initialize a conversation manager for Streamlit integration.
    
    Args:
        profile: The student profile.
        scenario: The scenario context.
        model_name: The model for the student bot.
        evaluator_model: The model for the evaluator.
        log_level: The logging level.
        
    Returns:
        The initialized conversation manager.
    """
    # Set up logging
    AgentLogger.set_level(log_level)
    logger = AgentLogger.get_logger("ConversationManager")
    
    # Handle enum values in the profile if it's a StudentProfile
    if hasattr(profile, 'interests') and isinstance(profile.interests, list):
        for i, interest in enumerate(profile.interests):
            if hasattr(interest, "__module__") and "enum" in interest.__module__.lower():
                logger.debug(f"Converting interest enum to string: {interest}")
    
    # Handle enum values in the scenario
    scenario_copy = {}
    if isinstance(scenario, dict):
        for key, value in scenario.items():
            if hasattr(value, "__module__") and "enum" in value.__module__.lower():
                logger.debug(f"Converting scenario enum value to string: {key}={value}")
                scenario_copy[key] = str(value)
            else:
                scenario_copy[key] = value
    else:
        scenario_copy = scenario
    
    # Initialize the conversation manager
    try:
        manager = ConversationManager(
            student_profile=profile,
            scenario=scenario_copy,
            model_name=model_name,
            evaluator_model=evaluator_model
        )
        logger.info("ConversationManager initialized successfully")
        return manager
    except Exception as e:
        logger.error(f"Error initializing ConversationManager: {str(e)}")
        raise

def process_streamlit_message(
    conversation_manager: ConversationManager,
    message: str
) -> Dict[str, Any]:
    """
    Process a message from Streamlit.
    
    Args:
        conversation_manager: The conversation manager.
        message: The message from the teacher.
        
    Returns:
        The response data.
    """
    return conversation_manager.process_message(message)

def continue_streamlit_conversation(
    conversation_manager: ConversationManager,
    continue_flag: bool
) -> bool:
    """
    Handle the continuation of the conversation after evaluation.
    
    Args:
        conversation_manager: The conversation manager.
        continue_flag: Whether to continue the conversation or not.
        
    Returns:
        True if the conversation was continued, False otherwise.
    """
    return conversation_manager.continue_conversation(continue_flag) 