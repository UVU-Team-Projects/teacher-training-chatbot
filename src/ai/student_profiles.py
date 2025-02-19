from typing import Dict, List, Optional
from enum import Enum


class Mood(Enum):
    HAPPY = "happy"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    TIRED = "tired"
    DISTRACTED = "distracted"
    FOCUSED = "focused"
    CONFUSED = "confused"


class Interest(Enum):
    SCIENCE = "science"
    ARTS = "arts"
    MATH = "math"
    READING = "reading"
    SPORTS = "sports"
    MUSIC = "music"
    TECHNOLOGY = "technology"
    NATURE = "nature"


class StudentProfile:
    def __init__(
        self,
        name: str,
        grade_level: int,
        personality_traits: List[str],
        learning_style: str,
        interests: List[Interest],
        typical_moods: List[Mood],
        behavioral_patterns: Dict[str, str],
        academic_strengths: List[str],
        academic_challenges: List[str],
        social_dynamics: Dict[str, str],
        support_strategies: List[str]
    ):
        self.name = name
        self.grade_level = grade_level
        self.personality_traits = personality_traits
        self.learning_style = learning_style
        self.interests = interests
        self.typical_moods = typical_moods
        self.behavioral_patterns = behavioral_patterns
        self.academic_strengths = academic_strengths
        self.academic_challenges = academic_challenges
        self.social_dynamics = social_dynamics
        self.support_strategies = support_strategies


# Pre-defined student profile templates
STUDENT_TEMPLATES = {
    "active_learner": {
        "personality_traits": ["energetic", "enthusiastic", "talkative", "curious"],
        "learning_style": "kinesthetic",
        "typical_moods": [Mood.EXCITED, Mood.DISTRACTED, Mood.HAPPY],
        "behavioral_patterns": {
            "morning": "High energy, needs movement breaks",
            "afternoon": "May become restless",
            "during_group_work": "Takes leadership role",
            "during_independent_work": "Struggles to stay seated",
            "transitions": "Often rushes through transitions"
        },
        "social_dynamics": {
            "peer_interactions": "Popular, but can be overwhelming",
            "group_work": "Natural leader but may dominate",
            "teacher_interaction": "Seeks frequent attention and validation"
        }
    },

    "quiet_observer": {
        "personality_traits": ["reserved", "thoughtful", "careful", "observant"],
        "learning_style": "visual",
        "typical_moods": [Mood.FOCUSED, Mood.ANXIOUS, Mood.TIRED],
        "behavioral_patterns": {
            "morning": "Takes time to warm up",
            "afternoon": "Most comfortable and engaged",
            "during_group_work": "Prefers listening role",
            "during_independent_work": "Highly focused",
            "transitions": "Moves carefully and deliberately"
        },
        "social_dynamics": {
            "peer_interactions": "Small, close-knit friend group",
            "group_work": "Contributes when directly asked",
            "teacher_interaction": "May need encouragement to participate"
        }
    },

    "struggling_student": {
        "personality_traits": ["persistent", "sensitive", "determined", "self-conscious"],
        "learning_style": "multimodal",
        "typical_moods": [Mood.FRUSTRATED, Mood.ANXIOUS, Mood.CONFUSED],
        "behavioral_patterns": {
            "morning": "Often arrives frustrated",
            "afternoon": "Fatigue affects performance",
            "during_group_work": "Hesitant to contribute",
            "during_independent_work": "Frequently seeks help",
            "transitions": "May need extra time"
        },
        "social_dynamics": {
            "peer_interactions": "Sometimes feels left out",
            "group_work": "Prefers partnering with friends",
            "teacher_interaction": "Needs regular reassurance"
        }
    }
}


def create_student_profile(
    template_name: str,
    name: str,
    grade_level: int,
    interests: List[Interest],
    academic_strengths: List[str],
    academic_challenges: List[str],
    support_strategies: List[str]
) -> StudentProfile:
    """Create a student profile based on a template with custom details."""
    if template_name not in STUDENT_TEMPLATES:
        raise ValueError(f"Template {template_name} not found")

    template = STUDENT_TEMPLATES[template_name]

    return StudentProfile(
        name=name,
        grade_level=grade_level,
        personality_traits=template["personality_traits"],
        learning_style=template["learning_style"],
        interests=interests,
        typical_moods=template["typical_moods"],
        behavioral_patterns=template["behavioral_patterns"],
        academic_strengths=academic_strengths,
        academic_challenges=academic_challenges,
        social_dynamics=template["social_dynamics"],
        support_strategies=support_strategies
    )
