# Student Profile and Scenario Agent System

This module provides a robust way to format student profiles and classroom scenarios for use with the LangGraph agent system.

## Core Components

### Profile and Scenario Formatting

The system includes utilities to convert profile and scenario objects into formatted strings for use in the agent state:

- `format_student_profile(profile)`: Converts a `StudentProfile` object to a formatted string
- `format_scenario(scenario)`: Converts a scenario object or dictionary to a formatted string

### State Management

Helper functions to manage the agent state:

- `set_student_profile_in_state(state, profile)`: Adds a formatted profile to the state
- `set_scenario_in_state(state, scenario)`: Adds a formatted scenario to the state
- `initialize_agent_state(profile, scenario)`: Creates a complete agent state with both components

### Agent Tools

LangGraph tools for accessing state information:

- `get_student_profile(state)`: Tool to retrieve the current profile from state
- `get_scenario(state)`: Tool to retrieve the current scenario from state

## Usage Example

```python
from src.ai.student_profiles import create_student_profile, Interest
from src.ai.pipeline.agentTools import initialize_agent_state
from src.ai.pipeline.supervisor import Supervisor

# Create a student profile
profile = create_student_profile(
    template_name="active_learner",
    name="Alex",
    grade_level=4,
    interests=[Interest.SCIENCE, Interest.SPORTS],
    academic_strengths=["math", "science"],
    academic_challenges=["writing", "sitting still"],
    support_strategies=["movement breaks", "visual aids"]
)

# Create or load a scenario
scenario = {
    "title": "Math Class Disruption",
    "description": "Student disruption during fractions lesson",
    "grade_level": "elementary",
    "subject": "mathematics",
    "challenge_type": "behavioral"
}

# Initialize the agent state
state = initialize_agent_state(profile=profile, scenario=scenario)

# Create and run the agent graph
supervisor = Supervisor()
graph = supervisor.create_supervisor_graph()
result = graph.invoke(state)
```

## Integration with Streamlit

This system can be integrated with a Streamlit interface to:

1. Let users select or create student profiles
2. Allow users to choose or generate scenarios
3. Initialize the agent with the selected profile and scenario
4. Maintain state between interactions

See `example_usage.py` for a complete working example.
