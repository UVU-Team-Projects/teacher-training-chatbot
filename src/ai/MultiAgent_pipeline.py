# ============================================================
# IMPORTS AND SETUP
# ============================================================
# Project files - handles both direct and relative imports
try:
    # Direct imports (when running the file directly)
    from student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from embedding import EmbeddingGenerator
    from profile_builder import StudentProfileBuilder
    from scenario_generator import ScenarioGenerator, generate_random_scenario, StudentBackground, ClassroomContext
except ImportError:
    # Relative imports (when imported as a module)
    from .student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from .embedding import EmbeddingGenerator
    from .profile_builder import StudentProfileBuilder
    from .scenario_generator import ScenarioGenerator, generate_random_scenario, StudentBackground, ClassroomContext

# External imports
from dotenv import load_dotenv
from colorama import Fore, Style  # For terminal color output
import time
from typing import Literal, Optional, List, TypedDict, Dict, Any, Union
from langchain_openai import ChatOpenAI  # OpenAI API integration
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import BaseTool

# Langgraph imports - for building the multi-agent system
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

import sys
import os
import pprint
import json

# ============================================================
# PATH CONFIGURATION
# ============================================================
# Get the absolute path of the project root
root_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the src directory
src_dir = os.path.join(root_dir, 'src')
# Add the src to sys.path
sys.path.append(src_dir)

# ============================================================
# ENVIRONMENT SETUP
# ============================================================
# Load environment variables from .env file
load_dotenv()
# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# ============================================================
# TYPE DEFINITIONS
# ============================================================
# Define state types using TypedDict for type checking and documentation

# Basic message state type


class MessageStateType(TypedDict, total=False):
    messages: List[Any]  # List of message objects
    context: str         # Additional context for the conversation

# Scenario type definition - represents a classroom scenario


class ScenarioType(TypedDict, total=False):
    title: str           # Title of the scenario
    description: str     # Detailed description of the scenario
    grade_level: str     # Grade level (e.g., "ELEMENTARY", "MIDDLE_SCHOOL")
    subject: str         # Subject matter (e.g., "MATH", "SCIENCE")
    challenge_type: str  # Type of challenge (e.g., "BEHAVIORAL", "ACADEMIC")

# Student profile type definition - represents a student's characteristics


class StudentProfileType(TypedDict, total=False):
    name: str                    # Student's name
    grade_level: str             # Student's grade level
    personality_traits: List[str]  # List of personality traits
    typical_moods: List[str]     # List of typical moods
    behavioral_patterns: str     # Description of behavioral patterns
    learning_style: str          # Learning style (e.g., "visual", "auditory")
    interests: List[str]         # List of interests
    academic_strengths: str      # Description of academic strengths
    academic_challenges: str     # Description of academic challenges
    support_strategies: str      # Strategies that help the student
    social_dynamics: str         # Description of social interactions

# Main state type for the multi-agent system


class MultiAgentStateType(TypedDict, total=False):
    # List of message objects (compatible with MessagesState)
    messages: List[Any]
    decision: str                         # Decision from the router
    context: str                         # Additional context for the conversation
    scenario: Optional[ScenarioType]     # The classroom scenario
    student_profile: Optional[StudentProfileType]  # The student profile
    teacher_actions: Optional[List[str]]  # List of teacher actions
    feedback: Optional[str]              # Feedback on teacher performance
    # Notification message for Streamlit UI
    notification: Optional[str]
    _flags: List[str]                    # Internal flags for controlling flow

# ============================================================
# HELPER FUNCTIONS
# ============================================================
# Convert between object types and dictionaries


def scenario_to_dict(scenario) -> ScenarioType:
    """Convert Scenario object to ScenarioType dictionary.

    This function handles both dictionary inputs and Scenario class objects,
    ensuring the output conforms to the ScenarioType structure.
    """
    if not scenario:
        return None

    # Handle the case where the scenario is already a dictionary
    if isinstance(scenario, dict):
        # Ensure it has all the required fields of ScenarioType
        return {
            "title": scenario.get("title", ""),
            "description": scenario.get("description", ""),
            "grade_level": scenario.get("grade_level", ""),
            "subject": scenario.get("subject", ""),
            "challenge_type": scenario.get("challenge_type", "")
        }

    # Handle full Scenario class from scenario_generator.py
    # We only keep the top-level fields that match ScenarioType
    return {
        "title": scenario.title,
        "description": scenario.description,
        "grade_level": getattr(scenario.grade_level, 'value', scenario.grade_level),
        "subject": getattr(scenario.subject, 'value', scenario.subject),
        "challenge_type": getattr(scenario.challenge_type, 'value', scenario.challenge_type)
    }


def student_profile_to_dict(profile) -> StudentProfileType:
    """Convert StudentProfile object to StudentProfileType dictionary.

    This function transforms a StudentProfile class object into a dictionary
    that conforms to the StudentProfileType structure.
    """
    if not profile:
        return None
    return {
        "name": profile.name,
        "grade_level": profile.grade_level,
        "personality_traits": profile.personality_traits,
        "typical_moods": [getattr(mood, 'value', mood) for mood in profile.typical_moods] if hasattr(profile, 'typical_moods') else profile.typical_moods,
        "behavioral_patterns": profile.behavioral_patterns,
        "learning_style": profile.learning_style,
        "interests": [getattr(interest, 'value', interest) for interest in profile.interests] if hasattr(profile, 'interests') else profile.interests,
        "academic_strengths": profile.academic_strengths,
        "academic_challenges": profile.academic_challenges,
        "support_strategies": profile.support_strategies,
        "social_dynamics": profile.social_dynamics
    }

# ============================================================
# STATE MANAGEMENT
# ============================================================


def create_multi_agent_state(
    messages=None,
    context="",
    scenario=None,
    student_profile=None,
    teacher_actions=None,
    feedback=None,
    notification=None
) -> MultiAgentStateType:
    """Create a new MultiAgentState dictionary with default values.

    This function initializes the state object used throughout the multi-agent system.
    It handles conversion between object types and dictionaries.

    Args:
        messages: List of message objects
        context: String context for the conversation
        scenario: ScenarioType dictionary or Scenario object
        student_profile: StudentProfileType dictionary or StudentProfile object
        teacher_actions: List of teacher action strings
        feedback: Feedback string
        notification: Notification message for Streamlit UI

    Returns:
        MultiAgentStateType dictionary with all components initialized
    """
    # Convert scenario and student_profile to dictionaries if they're objects
    try:
        if scenario and not isinstance(scenario, dict):
            scenario = scenario_to_dict(scenario)

        if student_profile and not isinstance(student_profile, dict):
            student_profile = student_profile_to_dict(student_profile)
    except Exception as e:
        print(f"Error converting state objects to dictionaries: {e}")
        # Fallback to empty dictionaries if conversion fails
        if scenario and not isinstance(scenario, dict):
            scenario = {}
        if student_profile and not isinstance(student_profile, dict):
            student_profile = {}

    return {
        "messages": messages or [],
        "context": context,
        "scenario": scenario,
        "student_profile": student_profile,
        "teacher_actions": teacher_actions,
        "feedback": feedback,
        "notification": notification,
        "_flags": []  # Empty flags list - no longer used for generation control
    }


class RAG:
    """
    Retrieval Augmented Generation (RAG) pipeline using LangGraph.
    Combines document retrieval with LLM generation for enhanced responses.
    This is the main orchestrator for the multi-agent system.
    """

    def __init__(self, llm=None, model_name="gpt-4o-mini", tools: list[BaseTool] = [], embedding_generator: EmbeddingGenerator = None):
        """
        Initialize the RAG pipeline.

        Args:
            tools: List of tools available to the agent
            embedding_generator: Optional custom embedding generator
        """
        # Initialize core components
        self.tools = tools
        self.tool_node = ToolNode(self.tools)
        # Initialize language model
        self.llm = llm or ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000
        ).bind_tools(self.tools)

        self.embedding_generator = embedding_generator or EmbeddingGenerator()

    def llm_call_router(self, state: MultiAgentStateType):
        """Route the input to the correct node"""
        print(Fore.YELLOW +
              f"STATE: {state.get('messages', [])[-1].content}" + Style.RESET_ALL)
        decision = self.llm.invoke([
            SystemMessage(
                content="Route the input to the correct node, scenario, profile, student, or feedback based on the state of the conversation."),
            HumanMessage(content=state.get("messages", [])[-1].content)
        ])
        print(Fore.YELLOW + f"DECISION: {decision.content}" + Style.RESET_ALL)
        return {"decision": decision.content}

# TODO: Add human-in-the-loop to the router so the conversation can be steered

    def router(self, state: MultiAgentStateType) -> Literal["scenario", "profile", "student", "feedback", "end"]:
        """Determine the next node in the multi-agent graph.

        This router checks if components are missing and routes accordingly.
        """
        try:
            # Extract message and the last message content
            messages = state.get("messages", [])

            # Check if we need to generate a student profile
            # This is the highest priority - we need a profile to do anything
            if state.get("student_profile") is None:
                print("Routing to profile generation because profile is missing")
                # Add notification to state
                state["notification"] = "Generating a student profile since none was provided..."
                return "profile"

            # Check if we need to generate a scenario
            # This is the second priority - we need a scenario for context
            if state.get("scenario") is None:
                print(Fore.GREEN + "ROUTER: Create Scenario" + Style.RESET_ALL)
                print("Routing to scenario generation because scenario is missing")
                # Add notification to state
                state["notification"] = "Generating a classroom scenario since none was provided..."
                return "scenario"

            # Generate student response if we have a profile and scenario
            # Check if we need to generate feedback
            last_message = messages[-1] if messages else None

            # If we've already generated student response, generate feedback
            if last_message and last_message.content == "/feedback":
                print(Fore.GREEN + "ROUTER: Generate Feedback" + Style.RESET_ALL)
                return "feedback"

            # If last message was from human, generate student response
            if last_message and isinstance(last_message, HumanMessage):
                print(Fore.GREEN + "ROUTER: Generate Student Response" +
                      Style.RESET_ALL)
                return "student"

            # If we've already generated feedback, end the conversation
            if state.get("feedback"):
                print(Fore.GREEN + "ROUTER: End Conversation" + Style.RESET_ALL)
                return "end"

        except Exception as e:
            print(f"Error in router function: {e}")
            # Default to end in case of any error
            return "end"

    def retrieve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for the current query."""

        query = state['messages'][-1].content if isinstance(
            state['messages'][-1], HumanMessage) else state['messages']
        # Get Chroma DB and search for relevant chunks
        db = self.embedding_generator.return_chroma()
        results = db.similarity_search_with_score(query, k=5)
        context = "\n\n---\n\n".join([doc.page_content for doc,
                                      _score in results])
        print("Results:\n ")
        for result in results:
            print(result, end="\n\n")  # DEBUG
        return {**state, "context": context}

    def generate_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response based on context and user input."""
        context = state.get('context', 'No context available')
        # Get the user's message
        user_message = state['messages'][-1].content

        response = self.model.invoke(user_message)
        return {**state, "messages": state["messages"] + [response]}

    def create_multi_agent(self) -> CompiledStateGraph:
        """Create and compile the multi-agent workflow."""
        # Create component instances
        scenario_generator = ScenarioGenerator()
        profile_selector = StudentProfileSelector()
        student_simulator = StudentSimulator()
        feedback_generator = TeacherFeedbackGenerator()

        # Define scenario handler function
        def generate_scenario_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            # Generate a random scenario
            scenario = generate_random_scenario()

            # Convert scenario to dictionary format
            new_state = {
                **state,
                "scenario": {
                    "title": scenario.title,
                    "description": scenario.description,
                    "grade_level": str(scenario.grade_level.value),
                    "subject": str(scenario.subject.value),
                    "challenge_type": str(scenario.challenge_type.value)
                }
            }

            # Keep the notification in the state for Streamlit to display
            if "notification" in new_state:
                new_state["notification"] = f"Generated scenario: {scenario.title}"

            return new_state

        # Define profile handler
        def profile_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            # Generate a student profile
            new_state = profile_selector.select_profile(state)

            # Keep the notification in the state for Streamlit to display
            if "notification" in new_state and new_state.get("student_profile"):
                profile_name = new_state["student_profile"].get(
                    "name", "Student")
                new_state["notification"] = f"Generated profile for {profile_name}"

            return new_state

        # Define workflow graph using factory function to create default state
        workflow = StateGraph(MultiAgentStateType)

        # Add all nodes
        workflow.add_node('router_node', self.llm_call_router)

        # Add components as nodes
        workflow.add_node('scenario_node', generate_scenario_handler)
        workflow.add_node('profile_node', profile_handler)
        workflow.add_node('student_retrieve_node',
                          student_simulator.retrieve_context)
        workflow.add_node('student_respond_node',
                          student_simulator.generate_response)
        # TODO: Add user node for human-in-the-loop
        # workflow.add_node('feedback_node', feedback_generator.generate_feedback)

        # Configure graph flow
        print("start entry point")
        workflow.set_entry_point("router_node")

        # Define conditional edges from router
        workflow.add_conditional_edges(
            "router_node",
            # Router method directly handles state routing
            self.router,
            {
                "scenario": "scenario_node",
                "profile": "profile_node",
                "student": "student_retrieve_node",
                # "feedback": "feedback_node",
                "end": END
            }
        )

        # Connect student simulation components
        workflow.add_edge('student_retrieve_node', 'student_respond_node')

        # All components return to router after completion
        workflow.add_edge('scenario_node', 'router_node')
        workflow.add_edge('profile_node', 'router_node')
        workflow.add_edge('student_respond_node', END)

        # Compile with memory persistence
        return workflow.compile()


def create_multi_agent_pipeline(tools: list[BaseTool] = None) -> CompiledStateGraph:
    """Create a multi-agent pipeline for teacher-student interaction.

    This pipeline respects existing data from Streamlit session state and only
    generates missing components when explicitly requested.

    Args:
        tools: Optional list of tools to provide to the agent

    Returns:
        A compiled state graph that can be invoked with a state dictionary
    """
    # Initialize tools if not provided
    if tools is None:
        tools = []

    # Use the RAG class's implementation directly
    return RAG(tools=tools).create_multi_agent()


def typing_effect(text: str, delay: float = 0.01) -> None:
    """Print text with a typing animation effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


class StudentProfileSelector:
    """Selects or generates a student profile for the scenario."""

    def __init__(self, llm=None, model_name="gpt-4o-mini"):
        # Initialize language model
        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.7
            )

    def select_profile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Select or generate a student profile for the scenario."""
        # If a profile already exists, use it
        if state.get("student_profile") is not None:
            return state

        # Get scenario information
        scenario = state.get("scenario", {})

        if not scenario:
            # Use active_learner as default template
            student_profile = create_student_profile(
                template_name="active_learner",
                name="Alex",
                grade_level=2,
                interests=[Interest.MATH, Interest.SCIENCE, Interest.READING],
                academic_strengths=[
                    'Speaking in front of the class', 'Math', 'History'],
                academic_challenges=[
                    'Writing long passages', 'Science experiments', 'paying attention in class', 'ADHD'],
                support_strategies=['Positive reinforcement',
                                    'Small group work', 'Breakout rooms']
            )
        else:
            # If there's a scenario, generate an appropriate profile
            system_prompt = f"""
            You are a teacher trainer creating a student profile for a simulated scenario.
            Based on the scenario details, create a realistic student profile that would 
            be appropriate for the situation.
            
            Scenario Title: {scenario.get('title', 'Unknown')}
            Scenario Description: {scenario.get('description', 'No description')}
            Grade Level: {scenario.get('grade_level', 'Unknown')}
            Subject: {scenario.get('subject', 'Unknown')}
            Challenge Type: {scenario.get('challenge_type', 'Unknown')}
            
            Create a student profile with the following information:
            1. Name (appropriate for the grade level)
            2. Grade level (specific number, not range)
            3. Personality traits (list)
            4. Learning style (visual, auditory, kinesthetic, etc.)
            5. Interests (list)
            6. Typical moods (list)
            7. Behavioral patterns (challenges, consistencies, triggers)
            8. Academic strengths (list)
            9. Academic challenges (list)
            10. Social dynamics (how they interact with peers/teachers)
            11. Support strategies (what works well for this student)
            
            Provide your answer as a JSON object.
            """

            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content="Generate a student profile for this scenario."),
            ])

            # Extract and clean profile data from the response
            try:
                # Clean up response to extract JSON
                cleaned_content = response.content
                # Remove "```json" and "```" if present
                if "```json" in cleaned_content:
                    cleaned_content = cleaned_content.replace(
                        "```json", "").replace("```", "").strip()
                elif "```" in cleaned_content:
                    cleaned_content = cleaned_content.replace(
                        "```", "").strip()

                # Parse JSON
                student_profile = json.loads(cleaned_content)

                # Ensure required fields exist
                required_fields = [
                    "name", "grade_level", "personality_traits", "learning_style",
                    "interests", "typical_moods", "behavioral_patterns",
                    "academic_strengths", "academic_challenges",
                    "social_dynamics", "support_strategies"
                ]

                for field in required_fields:
                    if field not in student_profile:
                        student_profile[field] = [] if field in ["personality_traits", "interests",
                                                                 "typical_moods", "academic_strengths",
                                                                 "academic_challenges", "support_strategies"] else {}
            except:
                # Fallback to default profile
                template = STUDENT_TEMPLATES["active_learner"]
                student_profile = {
                    "name": "Jamie",
                    "grade_level": int(scenario.get('grade_level', 'elementary').split('_')[0][0]) + 5,
                    "personality_traits": template["personality_traits"],
                    "learning_style": template["learning_style"],
                    "interests": [interest.value for interest in template["interests"]],
                    "typical_moods": [mood.value for mood in template["typical_moods"]],
                    "behavioral_patterns": template["behavioral_patterns"],
                    "academic_strengths": template["academic_strengths"],
                    "academic_challenges": template["academic_challenges"],
                    "social_dynamics": template["social_dynamics"],
                    "support_strategies": template["support_strategies"]
                }

        # Update state with the profile
        return {**state, "student_profile": student_profile}


class StudentSimulator:
    """
    Component that simulates student responses based on their profile
    and the current scenario.
    """

    def __init__(self, llm=None, model_name="gpt-4o-mini", embedding_generator=None):
        # Initialize language model
        self.llm = llm or ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
        )
        self.embedding_generator = embedding_generator or EmbeddingGenerator()

    def retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for the current query."""
        print(f"RETRIEVE CONTEXT!")
        # Similar to the retrieve method in RAG
        query = state['messages'][-1].content if isinstance(
            state['messages'][-1], HumanMessage) else state['messages']

        db = self.embedding_generator.return_chroma()
        results = db.similarity_search_with_score(query, k=5)
        context = "\n\n---\n\n".join([doc.page_content for doc,
                                     _score in results])

        return {**state, "context": context}

    def generate_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response based on the student profile and context."""
        print(f"GENERATE RESPONSE!")
        try:
            student_profile = state.get("student_profile", {})
            context = state.get("context", "")
            scenario = state.get("scenario", {})

            # Scenario-specific information to include if available
            scenario_info = ""
            if scenario:
                scenario_info = f"""
                Current Scenario: {scenario.get('title', 'General classroom interaction')}
                Scenario Description: {scenario.get('description', 'No specific scenario')}
                Subject: {scenario.get('subject', 'General')}
                Grade Level: {scenario.get('grade_level', student_profile.get('grade_level', 'Unknown'))}
                Challenge Type: {scenario.get('challenge_type', 'General interaction')}
                """

            # Handle different types of behavioral_patterns and social_dynamics
            # (they might be strings or dictionaries)
            behavioral_patterns_text = ""
            if isinstance(student_profile.get('behavioral_patterns', {}), dict):
                behavioral_patterns_text = chr(10).join(
                    [f"- {k}: {v}" for k, v in student_profile.get('behavioral_patterns', {}).items()])
            else:
                behavioral_patterns_text = student_profile.get(
                    'behavioral_patterns', 'None')

            social_dynamics_text = ""
            if isinstance(student_profile.get('social_dynamics', {}), dict):
                social_dynamics_text = chr(10).join(
                    [f"- {k}: {v}" for k, v in student_profile.get('social_dynamics', {}).items()])
            else:
                social_dynamics_text = student_profile.get(
                    'social_dynamics', 'None')

            # Handle interests and moods which might be lists or not
            interests = student_profile.get('interests', [])
            interests_text = ', '.join(str(interest) for interest in interests) if isinstance(
                interests, list) else interests

            moods = student_profile.get('typical_moods', [])
            moods_text = ', '.join(str(mood) for mood in moods) if isinstance(
                moods, list) else moods

            # Handle academic fields which might be strings or lists
            academic_strengths = student_profile.get('academic_strengths', '')
            strengths_text = ', '.join(academic_strengths) if isinstance(
                academic_strengths, list) else academic_strengths

            academic_challenges = student_profile.get(
                'academic_challenges', '')
            challenges_text = ', '.join(academic_challenges) if isinstance(
                academic_challenges, list) else academic_challenges

            support_strategies = student_profile.get('support_strategies', '')
            strategies_text = ', '.join(support_strategies) if isinstance(
                support_strategies, list) else support_strategies

            personality_traits = student_profile.get('personality_traits', [])
            traits_text = ', '.join(personality_traits) if isinstance(
                personality_traits, list) else personality_traits

            # Create a comprehensive structured prompt with all profile attributes
            system_prompt = f"""
            You are a student with the following profile:
            
            Name: {student_profile.get('name', 'Unknown')}
            Grade Level: {student_profile.get('grade_level', 'Unknown')}
            Personality Traits: {traits_text}
            Learning Style: {student_profile.get('learning_style', 'Mixed')}
            
            Typical Moods: {moods_text}
            Interests: {interests_text}
            
            Academic Strengths: {strengths_text}
            Academic Challenges: {challenges_text}
            Support Strategies: {strategies_text}
            
            Behavioral Patterns:
            {behavioral_patterns_text}
            
            Social Dynamics:
            {social_dynamics_text}
            
            {scenario_info}
            
            Speak and behave like this student would, keeping your language appropriate for your grade level.
            Consider your typical moods, behavioral patterns, and social dynamics in your responses.
            Use the provided context to help shape your response, but stay in character at all times.
            Let the user know what your actions are by saying what the student is doing. Example: *raises hand*, *stands up and moves to the front of the class*
            
            Context: {context}
            """
        except Exception as e:
            # Fallback to a simpler prompt if there are issues with the profile structure
            print(f"Error formatting student profile: {e}")
            system_prompt = f"""
            You are a student named {student_profile.get('name', 'Unknown')} in grade {student_profile.get('grade_level', 'Unknown')}.
            Respond to the teacher's message as this student would.
            
            Context: {context}
            """

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state['messages'][-1].content)
        ])
        print(Fore.GREEN + f"RESPONSE: {response.content}" + Style.RESET_ALL)

        # Return a proper AIMessage object instead of just the content string
        return {**state, "messages": state["messages"] + [response]}


class TeacherFeedbackGenerator:
    """
    Component that provides feedback to the teacher on their interactions
    with the student, offering advice on classroom management and teaching strategies.
    """

    def __init__(self, llm=None, model_name="gpt-4o-mini"):
        # Initialize language model
        self.llm = llm or ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000
        )

    def generate_feedback(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the interaction between teacher and student,
        then generate helpful feedback and suggestions.
        """
        print(Fore.RED + "GENERATE FEEDBACK!" + Style.RESET_ALL)
        try:
            # Extract conversation history
            conversation = state.get("messages", [])
            student_profile = state.get("student_profile", {})
            scenario = state.get("scenario", {})

            # Get the last teacher message and student response
            teacher_messages = [
                msg for msg in conversation if isinstance(msg, HumanMessage)]
            student_messages = [
                msg for msg in conversation if not isinstance(msg, HumanMessage)]

            print(Fore.GREEN +
                  f"TEACHER MESSAGES: {teacher_messages}" + Style.RESET_ALL)
            print(Fore.GREEN +
                  f"STUDENT MESSAGES: {student_messages}" + Style.RESET_ALL)

            last_teacher_message = teacher_messages[-1].content if teacher_messages else ""
            last_student_response = student_messages[-1].content if student_messages else ""

            print(
                Fore.GREEN + f"LAST TEACHER MESSAGE: {last_teacher_message}" + Style.RESET_ALL)
            print(
                Fore.GREEN + f"LAST STUDENT RESPONSE: {last_student_response}" + Style.RESET_ALL)

            # Format profile and scenario data safely
            student_name = student_profile.get('name', 'the student')
            grade_level = student_profile.get('grade_level', 'Unknown')

            # Include scenario information if available
            scenario_context = ""
            if scenario:
                scenario_title = scenario.get('title', 'the current scenario')
                scenario_desc = scenario.get(
                    'description', 'No description available')
                scenario_context = f"""
                Scenario: {scenario_title}
                Description: {scenario_desc}
                """

            # Create a prompt for the LLM to analyze the interaction
            system_prompt = f"""
            You are an experienced teacher trainer providing feedback on a teacher's interaction with {student_name}, a {grade_level} student.
            
            {scenario_context}
            
            The teacher said:
            "{last_teacher_message}"
            
            The student responded:
            "{last_student_response}"
            
            Analyze this interaction and provide constructive feedback to the teacher.
            Focus on:
            1. What worked well in the teacher's approach
            2. What could be improved
            3. Specific suggestions for more effective communication
            4. How the approach aligns with the student's profile and needs
            5. Alternative strategies that might work better
            
            Keep feedback professional, specific, and actionable.
            """

            # Generate feedback
            feedback_message = self.llm.invoke([
                SystemMessage(content=system_prompt)
            ])

            # Return original state with added feedback
            return {**state, "feedback": feedback_message.content}
        except Exception as e:
            print(f"Error generating teacher feedback: {e}")
            # Return a generic feedback message if there's an error
            return {**state, "feedback": "Unable to generate specific feedback. Please review the interaction and consider how your approach matched the student's needs and the scenario requirements."}


def main() -> None:
    """Run the multi-agent pipeline in interactive mode."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Initialize the RAG pipeline
    print(Fore.CYAN + "Initializing Multi-Agent Teacher Training System..." + Style.RESET_ALL)
    agent = create_multi_agent_pipeline()

    # Initial state just needs messages
    state = create_multi_agent_state(messages=[])

    print(Fore.GREEN + """
    Multi-Agent System Ready!
    
    This system will:
    1. Generate a teaching scenario
    2. Select an appropriate student profile
    3. Allow you to interact with the simulated student in an ongoing conversation
    4. Provide feedback on your teaching approach when requested
    
    Commands:
    - Type any message to talk to the student
    - Type '/feedback' when you want to get teaching feedback on your conversation
    - Type 'generate scenario' to create a new scenario
    - Type 'select profile' to choose a different student profile
    - Type 'q' to quit
    """ + Style.RESET_ALL)

    while True:
        query = input(Fore.GREEN + "Teacher: " + Style.RESET_ALL)

        if query.lower() == 'q':
            break

        # Update state with new message
        state["messages"] = state.get(
            "messages", []) + [HumanMessage(content=query)]

        # Process through the agent
        result = agent.invoke(
            state,
            config={"configurable": {"thread_id": 43}}
        )

        # Update our state with the result
        state = result

        # Display relevant information based on what happened
        if result.get("scenario") and not result.get("_displayed_scenario"):
            print(Fore.YELLOW + "\n--- SCENARIO ---")
            print(
                f"Title: {result['scenario'].get('title', 'Unnamed Scenario')}")
            print(
                f"Description: {result['scenario'].get('description', 'No description')}")
            print("---\n" + Style.RESET_ALL)
            state["_displayed_scenario"] = True

        if result.get("student_profile") and not result.get("_displayed_profile"):
            print(Fore.MAGENTA + "\n--- STUDENT PROFILE ---")
            print(f"Name: {result['student_profile'].get('name', 'Unknown')}")
            print(
                f"Grade: {result['student_profile'].get('grade_level', 'Unknown')}")
            print("---\n" + Style.RESET_ALL)
            state["_displayed_profile"] = True

        if result.get("feedback"):
            print(Fore.CYAN + "\n--- TEACHER FEEDBACK ---")
            print(result["feedback"])
            print("---\n" + Style.RESET_ALL)

        # Display the last message (should be student response)
        if result["messages"] and len(result["messages"]) > 0:
            last_msg = result["messages"][-1]
            if isinstance(last_msg, HumanMessage):
                # Skip displaying the teacher's message (which we just typed)
                pass
            else:
                print(Fore.BLUE +
                      f"Student: {last_msg.content}" + Style.RESET_ALL)


# Add a main function to demonstrate usage when run directly
if __name__ == "__main__":
    print(Fore.RESET)
    print("Initializing Multi-Agent Teacher Training System...")

    # Create a simple test function to demonstrate the pipeline
    def test_pipeline():
        import time

        print("\n=== Testing Multi-Agent Pipeline ===\n")

        # Create a simple state with a test message
        print("Creating initial state with a test message...")
        state = create_multi_agent_state(
            messages=[HumanMessage(
                content="Hi Alex! Tell me what you like to do in class.")],
            scenario={
                'title': 'Elementary Mathematics Behavioral Challenge',
                'description': """**Classroom Management Scenario: Grade 3 Mathematics**\n\n**Context Overview:**\nIn Ms. Thompson\'s third-grade classroom, there are 20 students, and it is a sunny morning. The class has just transitioned from a reading session to a mathematics lesson that will last for 45 minutes. The desks are arranged in traditional rows, and Ms. Thompson has a whiteboard at the front for instruction and a few computers at the back for interactive math games. The classroom atmosphere is generally positive, but today, one particular student, Jason, is displaying some challenging behaviors.\n\n**Student Background:**\nJason is 8 years old and has a visual learning style, which means he benefits from visual aids, diagrams, and hands-on activities. He does not have any special needs or language barriers but comes from a culturally diverse background. Recently, Jason has been having difficulty focusing during math lessons, which is unusual for him. \n\n**Specific Situation:**\nAs Ms. Thompson begins the lesson on addition and subtraction, she notices that Jason is fidgeting in his seat, tapping his pencil loudly against the desk, and whispering to a classmate. The lesson involves a visual presentation on the whiteboard, where Ms. Thompson demonstrates how to solve word problems using pictures and diagrams. Despite the engaging content, Jason seems disengaged and is not following along.\n\n**Relevant Behaviors and Interactions:**\n1. **Disruption:** Jason\'s tapping is distracting not only to himself but also to the students nearby. A couple of students glance over at him, visibly irritated.\n2. **Off-Task Behavior:** Instead of focusing on the lesson, Jason is leaning over to his neighbor, Emily, and whispering about a video game, causing her to lose focus as well.\n3. **Non-Verbal Cues:** Ms. Thompson notices that when she makes eye contact with Jason, he does not respond and instead looks down at his desk, indicating that he may be feeling overwhelmed or disengaged.\n4. **Peer Influence:** A few other students are starting to mimic Jason\'s behavior, which is creating a ripple effect of distraction in the classroom.\n\n**Classroom Dynamics:**\nThe rest of the class is generally attentive and engaged with the material, especially those who are visual learners like Jason. They seem to enjoy the interactive elements of the lesson, such as the use of visual aids. Ms. Thompson has established a positive rapport with her students, making it essential for her to address Jason\'s behavior promptly without disrupting the flow of the lesson.\n\n**Evidence-Based Teaching Practices:**\n1. **Visual Supports:** Ms. Thompson decides to incorporate more visual supports into the lesson, such as a colorful chart that outlines the steps for solving word problems and encourages students to refer to it.\n2. **Positive Reinforcement:** She acknowledges the students who are following along and quietly praises them, which may motivate Jason to return to the task at hand.\n3. **Classroom Management Techniques:** Ms. Thompson uses a calm voice to address Jason directly, saying, "Jason, I'd love for you to join us at the board. Can you come up and help me solve this problem using the chart?"\n4. **Engagement Strategies:** By inviting Jason to participate actively, Ms. Thompson not only redirects his attention but also engages him in a way that leverages his visual learning style. \n\n**Addressing the Challenge:**\nAs Jason stands up and approaches the whiteboard, Ms. Thompson provides him with a marker and asks him to illustrate the problem visually. This approach not only captures his interest but also helps him re-engage with the lesson. The other students watch attentively, and soon, Jason is leading the class in solving the problem, which boosts his confidence and refocuses his energy positively.\n\nAfter the lesson, Ms. Thompson takes a moment to check in with Jason individually. She expresses her appreciation for his help and asks if there is anything specific that would help him stay focused during math lessons. This open line of communication allows her to understand his needs better and provides an opportunity for Jason to express himself, ensuring that he feels supported moving forward.\n\nBy implementing these strategies, Ms. Thompson effectively manages the behavioral challenges while maintaining a positive learning environment for all students.""",
                'grade_level': 'elementary',
                'subject': 'mathematics',
                'challenge_type': 'behavioral',
            },
            student_profile={
                'name': 'Alex',
                'grade_level': 2,
                'personality_traits': ['energetic', 'enthusiastic', 'talkative', 'curious'],
                'typical_moods': ['excited', 'distracted', 'happy'],
                'behavioral_patterns': {
                    'morning': 'High energy, needs movement breaks',
                    'afternoon': 'May become restless',
                    'during_group_work': 'Takes leadership role',
                    'during_independent_work': 'Struggles to stay seated',
                    'transitions': 'Often rushes through transitions'
                },
                'learning_style': 'kinesthetic',
                'interests': ['science', 'sports'],
                'academic_strengths': ['math', 'science'],
                'academic_challenges': ['reading', 'writing'],
                'support_strategies': ['visual aids', 'frequent breaks'],
                'social_dynamics': {
                    'peer_interactions': 'Popular, but can be overwhelming',
                    'group_work': 'Natural leader but may dominate',
                    'teacher_interaction': 'Seeks frequent attention and validation'
                }
            }
        )

        # Create and invoke the agent
        print("Creating and invoking the multi-agent pipeline...")
        agent = create_multi_agent_pipeline()

        # Set a timeout for the agent invocation
        start_time = time.time()

        try:
            result = agent.invoke(
                state,
                config={"configurable": {"thread_id": 1}}
            )

            # Print the result
            print("\n=== Pipeline Results ===\n")

            if result.get("notification"):
                print(f"Notification: {result['notification']}")

            if result.get("scenario"):
                print(f"\nGenerated Scenario: {result['scenario']['title']}")
                print(
                    f"Description: {result['scenario']['description'][:200]}...\n")

            if result.get("student_profile"):
                print(
                    f"\nGenerated Profile: {result['student_profile']['name']}")
                print(
                    f"Grade Level: {result['student_profile']['grade_level']}")
                print(
                    f"Learning Style: {result['student_profile']['learning_style']}")
                print(
                    f"Interests: {', '.join(result['student_profile']['interests'])}\n")

            if result["messages"] and len(result["messages"]) > 0:
                print(
                    f"\nResponse: {result['messages'][-1].content[:300]}...\n")

            print(f"\nExecution time: {time.time() - start_time:.2f} seconds")

        except Exception as e:
            print(f"\nError occurred: {e}")
            print(
                f"Execution time before error: {time.time() - start_time:.2f} seconds")

        print("\n=== Test Complete ===\n")

    # Run the test
    test_pipeline()

    print("Pipeline test completed.")
