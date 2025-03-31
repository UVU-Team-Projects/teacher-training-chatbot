from langchain_core.tools import tool, BaseTool, Tool as LangchainTool
from src.ai.student_profiles import StudentProfile
from src.ai.pipeline.agent_state import AgentState
from typing import Optional, Dict, Any, List
from src.logging import AgentLogger
from src.ai.embedding import EmbeddingGenerator
from langchain_openai import ChatOpenAI
from colorama import Fore, Style

# Initialize logger
logger = AgentLogger.get_logger("AgentTools")


def format_student_profile(profile: StudentProfile) -> str:
    """
    Convert a StudentProfile object to a formatted string for use in AgentState.

    Args:
        profile: A StudentProfile object with student information

    Returns:
        A formatted string representation of the student profile
    """
    logger.debug(f"Formatting student profile for: {profile.name}")

    # Format interests and moods which are enum objects
    interests = ", ".join([i.value for i in profile.interests])
    moods = ", ".join([m.value for m in profile.typical_moods])

    # Format dictionary fields
    behavior_str = "\n".join(
        [f"- {k}: {v}" for k, v in profile.behavioral_patterns.items()])
    social_str = "\n".join(
        [f"- {k}: {v}" for k, v in profile.social_dynamics.items()])

    # Format list fields
    strengths = ", ".join(profile.academic_strengths)
    challenges = ", ".join(profile.academic_challenges)
    strategies = ", ".join(profile.support_strategies)
    traits = ", ".join(profile.personality_traits)

    # Create the formatted string
    formatted_profile = f"""
STUDENT PROFILE:
Name: {profile.name}
Grade Level: {profile.grade_level}
Personality Traits: {traits}
Learning Style: {profile.learning_style}

Interests: {interests}
Typical Moods: {moods}

Academic Strengths: {strengths}
Academic Challenges: {challenges}
Support Strategies: {strategies}

Behavioral Patterns:
{behavior_str}

Social Dynamics:
{social_str}
"""
    logger.debug(f"Created formatted profile ({len(formatted_profile)} chars)")
    return formatted_profile


def format_scenario(scenario) -> str:
    """
    Convert a scenario object to a formatted string for use in AgentState.

    Args:
        scenario: A scenario object with classroom scenario information

    Returns:
        A formatted string representation of the scenario
    """
    logger.debug("Formatting scenario")

    # Handle both dictionary and object types
    if isinstance(scenario, dict):
        logger.debug("Scenario is a dictionary")
        title = scenario.get('title', 'Unknown')
        description = scenario.get('description', 'No description available')
        grade_level = scenario.get('grade_level', 'Unknown')
        subject = scenario.get('subject', 'Unknown')
        challenge_type = scenario.get('challenge_type', 'Unknown')
    else:
        # It's an object with attributes
        logger.debug("Scenario is an object")
        title = getattr(scenario, 'title', 'Unknown')
        description = getattr(scenario, 'description',
                              'No description available')

        # Handle enum values
        grade_level_obj = getattr(scenario, 'grade_level', None)
        grade_level = getattr(grade_level_obj, 'value', str(
            grade_level_obj)) if grade_level_obj else 'Unknown'

        subject_obj = getattr(scenario, 'subject', None)
        subject = getattr(subject_obj, 'value', str(
            subject_obj)) if subject_obj else 'Unknown'

        challenge_obj = getattr(scenario, 'challenge_type', None)
        challenge_type = getattr(challenge_obj, 'value', str(
            challenge_obj)) if challenge_obj else 'Unknown'

    logger.info(f"Scenario: {title} ({subject}, {grade_level})")

    # Create the formatted string
    formatted_scenario = f"""
CLASSROOM SCENARIO:
Title: {title}
Grade Level: {grade_level}
Subject: {subject}
Challenge Type: {challenge_type}

Description:
{description}
"""
    logger.debug(
        f"Created formatted scenario ({len(formatted_scenario)} chars)")
    return formatted_scenario


@tool
def get_student_profile(state: Dict[str, Any]) -> str:
    """
    Get the current student profile from the agent state.

    Returns:
        The student profile as a formatted string or a message if no profile is set
    """
    logger.debug("Tool called: get_student_profile")

    if state and "studentProfile" in state and state["studentProfile"]:
        logger.info("Retrieved student profile from state")
        return state["studentProfile"]

    logger.warning("No student profile found in state")
    return "No student profile has been set in the current state."


@tool
def get_scenario(state: AgentState) -> str:
    """
    Get the current classroom scenario from the agent state.

    Returns:
        The scenario as a formatted string or a message if no scenario is set
    """
    logger.debug("Tool called: get_scenario")

    if state and "scenario" in state and state["scenario"]:
        logger.info("Retrieved scenario from state")
        return state["scenario"]

    logger.warning("No scenario found in state")
    return "No scenario has been set in the current state."


def set_student_profile_in_state(state: AgentState, profile: StudentProfile) -> AgentState:
    """
    Sets a StudentProfile in the agent state.

    Args:
        state: The current agent state dictionary
        profile: The StudentProfile object to use

    Returns:
        Updated state with formatted student profile string
    """
    logger.info(f"Setting student profile in state: {profile.name}")
    formatted_profile = format_student_profile(profile)
    state["studentProfile"] = formatted_profile
    return state


def set_scenario_in_state(state: AgentState, scenario) -> AgentState:
    """
    Sets a scenario in the agent state.

    Args:
        state: The current agent state dictionary
        scenario: The scenario object to use

    Returns:
        Updated state with formatted scenario string
    """
    if hasattr(scenario, 'title'):
        title = scenario.title
    elif isinstance(scenario, dict) and 'title' in scenario:
        title = scenario['title']
    else:
        title = "Unknown scenario"

    logger.info(f"Setting scenario in state: {title}")
    formatted_scenario = format_scenario(scenario)
    state["scenario"] = formatted_scenario
    return state


def retrieve_classroom_management_insights(state, query=None):
    """
    Retrieve relevant classroom management insights from the knowledge base.
    
    Args:
        state: Current agent state
        query: Optional specific query. If not provided, will use recent conversation.
    
    Returns:
        Updated state with classroom management insights
    """
    logger = AgentLogger.get_logger("KnowledgeBaseRetrieval")
    logger.info("Retrieving classroom management insights")
    
    # Initialize the embedding generator
    embedding_generator = EmbeddingGenerator()
    
    # If no specific query is provided, generate it from recent messages
    if not query:
        messages = state.get("messages", [])
        if len(messages) < 2:
            logger.warning("Not enough context to generate insights")
            return {**state, "kb_insights": "Not enough conversation context for insights."}
        
        # Use last 3 messages or all available if fewer
        recent_messages = messages[-min(3, len(messages)):]
        conversation_context = "\n".join([
            f"{msg.name if hasattr(msg, 'name') else 'Unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
            for msg in recent_messages
        ])
        
        # Create search query from context
        llm = ChatOpenAI(model="gpt-4o-mini")
        query_prompt = f"""
        Based on this recent conversation between a teacher and student, identify 
        the main classroom management topic or challenge.
        Return a concise search query (5-10 words) that would help find relevant 
        classroom management strategies.
        
        CONVERSATION:
        {conversation_context}
        """
        
        query_result = llm.invoke(query_prompt)
        query = query_result.content if hasattr(query_result, 'content') else str(query_result)
        logger.info(f"Generated search query: {query}")
    
    # Retrieve relevant documents
    try:
        chroma_client = embedding_generator.return_chroma()
        search_results = chroma_client.similarity_search_with_score(
            query=query, 
            k=3  # Get top 3 results
        )
        
        if not search_results:
            logger.warning("No relevant insights found")
            return {**state, "kb_insights": "No relevant classroom management insights found."}
        
        # Format the insights
        insights = []
        for doc, score in search_results:
            source = doc.metadata.get('source', 'Unknown source')
            insights.append({
                "content": doc.page_content,
                "source": source,
                "relevance": score
            })
        
        # Generate a summary of the insights
        documents_text = "\n\n".join([insight["content"] for insight in insights])
        llm = ChatOpenAI(model="gpt-4o-mini")
        
        summary_prompt = f"""
        Summarize these classroom management insights into practical advice 
        for a teacher dealing with this situation:
        
        {documents_text}
        
        FORMAT YOUR RESPONSE AS:
        1. Key insight: [concise statement]
        2. Practical strategy: [brief actionable tip]
        3. Implementation: [how to apply this in the classroom]
        """
        
        summary_result = llm.invoke(summary_prompt)
        summary = summary_result.content if hasattr(summary_result, 'content') else str(summary_result)
        
        logger.info(f"Generated knowledge base insights: {summary[:100]}...")
        
        # Add insights to state
        kb_data = {
            "summary": summary,
            "detailed_insights": insights,
            "query": query
        }
        
        # Print the insights for reference
        print(f"\n{Fore.GREEN}CLASSROOM MANAGEMENT INSIGHTS:{Style.RESET_ALL}")
        print(f"Query: {query}")
        print(f"{summary}")
        print("="*50)
        
        return {**state, "kb_insights": kb_data}
        
    except Exception as e:
        logger.error(f"Error retrieving classroom management insights: {str(e)}")
        return {**state, "kb_insights": f"Error retrieving insights: {str(e)}"}

# Add the new tool to the tools list
get_classroom_management_insights = LangchainTool.from_function(
    func=retrieve_classroom_management_insights,
    name="get_classroom_management_insights",
    description="Retrieve relevant classroom management insights from the knowledge base to help respond to the current situation",
)
