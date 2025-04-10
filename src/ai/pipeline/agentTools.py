from langchain_core.tools import tool
from src.ai.student_profiles import StudentProfile
from agent_state import AgentState
from typing import Optional, Dict, Any
from src.logging import AgentLogger

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
