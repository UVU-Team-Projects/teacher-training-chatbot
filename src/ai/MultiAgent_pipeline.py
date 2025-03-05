# Project files
try:
    from student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from embedding import EmbeddingGenerator
    from profile_builder import StudentProfileBuilder
    from scenario_generator import ScenarioGenerator, generate_random_scenario, StudentBackground, ClassroomContext
except ImportError:
    from .student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from .embedding import EmbeddingGenerator
    from .profile_builder import StudentProfileBuilder
    from .scenario_generator import ScenarioGenerator, generate_random_scenario, StudentBackground, ClassroomContext

# External imports
from dotenv import load_dotenv
from colorama import Fore, Style
import time
from typing import Literal, Optional, List, TypedDict, Dict, Any, Union
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate

# Langgraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

import sys
import os
import pprint
import json

# Get the absolute path of the project root
root_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the src directory
src_dir = os.path.join(root_dir, 'src')
# Add the src to sys.path
sys.path.append(src_dir)

# Load environment variables
load_dotenv()
# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Define state types using TypedDict


class MessageStateType(TypedDict, total=False):
    messages: List[Any]
    context: str

# Define the multi-agent state type


class ScenarioType(TypedDict, total=False):
    title: str
    description: str
    grade_level: str
    subject: str
    challenge_type: str


class StudentProfileType(TypedDict, total=False):
    name: str
    grade_level: str
    personality_traits: List[str]
    typical_moods: List[str]
    behavioral_patterns: str
    learning_style: str
    interests: List[str]
    academic_strengths: str
    academic_challenges: str
    support_strategies: str
    social_dynamics: str


class MultiAgentStateType(TypedDict, total=False):
    messages: List[Any]  # Compatible with MessagesState
    context: str
    scenario: Optional[ScenarioType]
    student_profile: Optional[StudentProfileType]
    teacher_actions: Optional[List[str]]
    feedback: Optional[str]
    _flags: List[str]  # Internal flags for controlling flow

# Helper functions to convert between types


def scenario_to_dict(scenario) -> ScenarioType:
    """Convert Scenario object to ScenarioType dictionary."""
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
    """Convert StudentProfile object to StudentProfileType dictionary."""
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

# Function to create a new MultiAgentState


def create_multi_agent_state(
    messages=None,
    context="",
    scenario=None,
    student_profile=None,
    teacher_actions=None,
    feedback=None,
    generate_missing=False
) -> MultiAgentStateType:
    """Create a new MultiAgentState dictionary with default values.

    Args:
        messages: List of message objects
        context: String context for the conversation
        scenario: ScenarioType dictionary or Scenario object
        student_profile: StudentProfileType dictionary or StudentProfile object
        teacher_actions: List of teacher action strings
        feedback: Feedback string
        generate_missing: If True, sets flags to generate missing components

    Returns:
        MultiAgentStateType dictionary
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

    # Initialize flags for explicit generation when components are missing
    flags = []
    if generate_missing:
        if scenario is None:
            flags.append("_generate_scenario")
        if student_profile is None:
            flags.append("_generate_profile")

    return {
        "messages": messages or [],
        "context": context,
        "scenario": scenario,
        "student_profile": student_profile,
        "teacher_actions": teacher_actions,
        "feedback": feedback,
        "_flags": flags  # Internal flags for controlling flow
    }


class RAG:
    """
    Retrieval Augmented Generation (RAG) pipeline using LangGraph.
    Combines document retrieval with LLM generation for enhanced responses.
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

        # self.model = ChatOllama(model="llama3.2:3b").bind_tools(self.tools)
        # "deepseek-r1:14b"

        self.embedding_generator = embedding_generator or EmbeddingGenerator()

        # self.PROMPT_TEMPLATE = """
        #     You are a 2nd grader with the following profile:

        #     Name: {name}
        #     Grade Level: {grade_level}
        #     Personality: {personality_traits}
        #     Typical Moods: {moods}
        #     Behavioral Patterns: {behavior}
        #     Current Interests: {interests}

        #     Learning Style: {learning_style}
        #     Academic Strengths: {academic_strengths}
        #     Academic Challenges: {academic_challenges}
        #     Support Strategies: {support_strategies}
        #     Social Dynamics: {social_dynamics}

        #     Match your words, language, and behavior to match this profile.
        #     The provided context can help you understand how to act and respond. If the context
        #     doesn't contain relevant information, please decide how to best respond while
        #     staying in character.

        #     The user is your teacher. Respond as if you are this specific 2nd grader talking to your teacher.

        #     Context: {context}

        #     ---

        #     Answer the teacher's question concisely based on the above context: {question}
        # """

    # def should_continue(self, state: Dict[str, Any]) -> Literal["tools", "end"]:
    #     """Determine whether to continue processing or return response."""
    #     if state['messages'][-1].tool_calls:
    #         return "tools"
    #     return END

    def router(self, state: MultiAgentStateType) -> Literal["scenario", "profile", "student", "feedback", "end"]:
        """Determine the next node in the multi-agent graph.

        This router respects existing data in the state and only generates
        missing components when absolutely necessary.
        """
        try:
            # Extract message and the last message content
            messages = state.get("messages", [])

            # Check if we EXPLICITLY need to generate a scenario or profile
            # This respects existing data from Streamlit session state

            # ONLY route to scenario generation if scenario is None (not empty dict)
            # This ensures we don't override existing scenarios from Streamlit
            if state.get("scenario") is None and "_generate_scenario" in state.get("_flags", []):
                print(
                    "Routing to scenario generation because scenario is missing and flag is set")
                return "scenario"

            # ONLY route to profile generation if profile is None (not empty dict)
            # This ensures we don't override existing profiles from Streamlit
            if state.get("student_profile") is None and "_generate_profile" in state.get("_flags", []):
                print(
                    "Routing to profile generation because profile is missing and flag is set")
                return "profile"

            # Generate student response if we have a profile
            # (scenario is optional but preferred)
            if state.get("student_profile") is not None:
                # Check if we need to generate feedback
                last_message = messages[-1] if messages else None

                # If last message was from human, generate student response
                if last_message and isinstance(last_message, HumanMessage):
                    return "student"

                # If we've already generated student response, generate feedback
                return "feedback"

            # Default to end if nothing else matches
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

    # def create_agent(self) -> CompiledStateGraph:
    #     """Create and compile the agent workflow."""
    #     # Define workflow graph with a factory function to create a dict
    #     workflow = StateGraph(lambda: {"messages": [], "context": ""})

    #     # Add nodes
    #     workflow.add_node('retrieve', self.retrieve)
    #     workflow.add_node('generate', self.generate_response)
    #     # workflow.add_node('tools', self.tool_node)

    #     # Configure graph flow
    #     workflow.set_entry_point("retrieve")
    #     # workflow.set_entry_point("generate")
    #     workflow.add_edge('retrieve', 'generate')
    #     # workflow.add_conditional_edges("generate", self.should_continue)
    #     # workflow.add_edge("tools", 'generate')
    #     workflow.add_edge('generate', END)

    #     # Compile with memory persistence
    #     self.agent = workflow.compile(checkpointer=MemorySaver())
    #     return self.agent

    def create_multi_agent(self) -> CompiledStateGraph:
        """Create and compile the multi-agent workflow."""
        # Create component instances
        scenario_generator = ScenarioGenerator()
        profile_selector = StudentProfileSelector()
        student_simulator = StudentSimulator()
        feedback_generator = TeacherFeedbackGenerator()

        # Define scenario handler function to ensure we only generate a scenario when needed
        def generate_scenario_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            # Only generate if scenario is explicitly None (not an empty dict)
            # This respects existing scenarios from Streamlit
            if state.get("scenario") is None:
                scenario = scenario_generator.generate_random_scenario()
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
                # Remove the generate flag since we've handled it
                if "_flags" in new_state and "_generate_scenario" in new_state["_flags"]:
                    new_state["_flags"].remove("_generate_scenario")
                return new_state
            # If scenario already exists, just return the state unchanged
            return state

        # Define profile handler that respects existing profiles
        def profile_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            # Only generate if profile is explicitly None (not an empty dict)
            # This respects existing profiles from Streamlit
            if state.get("student_profile") is None:
                new_state = profile_selector.select_profile(state)
                # Remove the generate flag since we've handled it
                if "_flags" in new_state and "_generate_profile" in new_state["_flags"]:
                    new_state["_flags"].remove("_generate_profile")
                return new_state
            # If profile already exists, just return the state unchanged
            return state

        # Define workflow graph using factory function to create default state
        workflow = StateGraph(MultiAgentStateType)

        # Add all nodes
        workflow.add_node('router_node', self.router)

        # Add components as nodes
        workflow.add_node('scenario_node', generate_scenario_handler)
        workflow.add_node('profile_node', profile_handler)
        workflow.add_node('student_retrieve_node',
                          student_simulator.retrieve_context)
        workflow.add_node('student_respond_node',
                          student_simulator.generate_response)
        workflow.add_node(
            'feedback_node', feedback_generator.generate_feedback)

        # Configure graph flow
        workflow.set_entry_point("router_node")

        # Define conditional edges from router
        workflow.add_conditional_edges(
            "router_node",
            # The router function needs to be wrapped to ensure it's called correctly
            # This passes the state object to the router
            lambda x: self.router(x),
            {
                "scenario": "scenario_node",
                "profile": "profile_node",
                "student": "student_retrieve_node",
                "feedback": "feedback_node",
                "end": END
            }
        )

        # Connect student simulation components
        workflow.add_edge('student_retrieve_node', 'student_respond_node')

        # All components return to router after completion
        workflow.add_edge('scenario_node', 'router_node')
        workflow.add_edge('profile_node', 'router_node')
        workflow.add_edge('student_respond_node', 'router_node')
        workflow.add_edge('feedback_node', 'router_node')

        # Compile with memory persistence
        return workflow.compile()


def create_pipeline(tools: list[BaseTool] = None) -> CompiledStateGraph:
    """Create and return a compiled RAG pipeline with specified student profile."""
    return RAG(tools=tools or []).create_agent()


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
            # If no scenario, create a default profile
            from src.ai.student_profiles import STUDENT_TEMPLATES

            # Use active_learner as default template
            template = STUDENT_TEMPLATES["active_learner"]
            student_profile = {
                "name": "Alex",
                "grade_level": 2,
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
                from src.ai.student_profiles import STUDENT_TEMPLATES
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
            max_tokens=2000
        )
        self.embedding_generator = embedding_generator or EmbeddingGenerator()

    def retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for the current query."""
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

            last_teacher_message = teacher_messages[-1].content if teacher_messages else ""
            last_student_response = student_messages[-1].content if student_messages else ""

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


def main_multi_agent() -> None:
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
    3. Allow you to interact with the simulated student
    4. Provide feedback on your teaching approach
    
    Commands:
    - Type 'generate scenario' to create a new scenario
    - Type 'select profile' to choose a different student profile
    - Type '/feedback' to get teaching feedback
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


# def main() -> None:
#     """Run the RAG pipeline in interactive mode."""
#     # Create a student profile
#     print("Creating student profile...")
#     builder = StudentProfileBuilder()
#     description = """
#     Sarah is a bright but sometimes anxious 2nd grader who loves science experiments
#     and reading about nature. She's usually focused in the morning but gets tired
#     and distracted in the afternoon. She works well in small groups but can be
#     hesitant to speak up in larger class discussions. Sarah excels at math but
#     struggles with writing long passages. She benefits from visual aids and
#     frequent positive reinforcement.
#     """
#     student = builder.build_profile_from_text(description)
#     print(f"Student profile created: {student}")
#     agent = create_pipeline()
#     print(Fore.GREEN + f"Student {student.name} is ready! ")

#     while True:
#         print(Fore.RED + 'Enter "q" to quit.')
#         query = input(Fore.GREEN + "Your input: " + Style.RESET_ALL)

#         if query.lower() == 'q':
#             break

#         # Initialize state with both messages and student profile
#         initial_state = {
#             "messages": [HumanMessage(content=query)],
#             "context": "",
#             "student_profile": {
#                 "name": student.name,
#                 "grade_level": student.grade_level,
#                 "personality_traits": student.personality_traits,
#                 "typical_moods": student.typical_moods,
#                 "behavioral_patterns": student.behavioral_patterns,
#                 "learning_style": student.learning_style,
#                 "interests": student.interests,
#                 "academic_strengths": student.academic_strengths,
#                 "academic_challenges": student.academic_challenges,
#                 "support_strategies": student.support_strategies,
#                 "social_dynamics": student.social_dynamics
#             }
#         }

#         response = agent.invoke(
#             initial_state,
#             config={"configurable": {"thread_id": 42}}
#         )

#         print(Fore.LIGHTBLUE_EX, end=" ")
#         # typing_effect(response["messages"][-1].content)
#         print(response["messages"][-1].content)
#         print(Style.RESET_ALL)


if __name__ == "__main__":
    # main()  # Run the original RAG pipeline
    main_multi_agent()  # Run the multi-agent system

# Functions to help Streamlit integration


def create_profile_for_streamlit(
    profile_type: str,
    **kwargs
) -> StudentProfileType:
    """
    Create a student profile for use in Streamlit.

    Args:
        profile_type: One of "template", "custom", or "from_description"
        **kwargs: Parameters specific to the profile type

    Returns:
        StudentProfileType dictionary ready for Streamlit state
    """
    student_profile = None

    if profile_type == "template":
        # Create from template
        student_profile = create_student_profile(
            template_name=kwargs.get("template_name", "active_learner"),
            name=kwargs.get("name", "Student"),
            grade_level=kwargs.get("grade_level", 5),
            interests=kwargs.get("interests", []),
            academic_strengths=kwargs.get("academic_strengths", []),
            academic_challenges=kwargs.get("academic_challenges", []),
            support_strategies=kwargs.get("support_strategies", [])
        )

    elif profile_type == "custom":
        # Create custom profile
        template = STUDENT_TEMPLATES.get(
            kwargs.get("template_base", "active_learner"))
        student_profile = StudentProfile(
            name=kwargs.get("name", "Student"),
            grade_level=kwargs.get("grade_level", 5),
            personality_traits=kwargs.get("personality_traits", []),
            learning_style=kwargs.get("learning_style", "visual"),
            interests=kwargs.get("interests", []),
            typical_moods=kwargs.get("typical_moods", []),
            behavioral_patterns=kwargs.get(
                "behavioral_patterns", template["behavioral_patterns"]) if template else {},
            academic_strengths=kwargs.get("academic_strengths", []),
            academic_challenges=kwargs.get("academic_challenges", []),
            social_dynamics=kwargs.get(
                "social_dynamics", template["social_dynamics"]) if template else {},
            support_strategies=kwargs.get("support_strategies", [])
        )

    elif profile_type == "from_description":
        # Use profile builder
        description = kwargs.get("description", "")
        if description:
            builder = StudentProfileBuilder()
            student_profile = builder.build_profile_from_text(description)

    # Convert to dictionary format
    if student_profile:
        return student_profile_to_dict(student_profile)
    return None


def create_scenario_for_streamlit(
    scenario_type: str,
    **kwargs
) -> ScenarioType:
    """
    Create a scenario for use in Streamlit.

    Args:
        scenario_type: Either "random" or "custom"
        **kwargs: Parameters specific to the scenario type

    Returns:
        ScenarioType dictionary ready for Streamlit state
    """
    scenario = None

    if scenario_type == "random":
        # Generate a random scenario
        scenario = generate_random_scenario()

    elif scenario_type == "custom":
        # Create a custom scenario
        student_background = StudentBackground(
            age=kwargs.get("age", 8),
            grade=kwargs.get("grade", 3),
            learning_style=kwargs.get("learning_style", "visual"),
        )

        classroom_context = ClassroomContext(
            class_size=kwargs.get("class_size", 20),
            time_of_day=kwargs.get("time_of_day", "Morning"),
            class_duration=kwargs.get("class_duration", 45),
            previous_activities=kwargs.get(
                "previous_activities", ["reading", "math"]),
            classroom_setup=kwargs.get("classroom_setup", "traditional desks"),
            available_resources=kwargs.get("available_resources", [
                                           "whiteboard", "computers"])
        )

        # Initialize scenario generator
        grade_level = kwargs.get("grade_level")
        subject = kwargs.get("subject")
        challenge_type = kwargs.get("challenge_type")

        if grade_level and subject and challenge_type:
            scenario_gen = ScenarioGenerator()
            scenario = scenario_gen.generate_scenario(
                grade_level=grade_level,
                subject=subject,
                challenge_type=challenge_type,
                student_background=student_background,
                classroom_context=classroom_context
            )

    # Convert to dictionary format
    if scenario:
        return scenario_to_dict(scenario)
    return None
