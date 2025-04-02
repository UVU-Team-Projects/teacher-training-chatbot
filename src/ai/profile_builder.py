from typing import Dict, List, Optional
from .student_profiles import StudentProfile, Interest, Mood
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json


class StudentProfileBuilder:
    """
    Builds detailed student profiles from text descriptions using LLM.
    """

    def __init__(self):
        self.model = ChatOllama(model="deepseek-r1:14b")

        self.PROFILE_PROMPT: str = '''As an educational expert, analyze the following student description and create a detailed student profile.
Extract key characteristics and format them according to the specified structure.

Student Description: {description}

Create a profile with these exact categories. Use only the provided enums for interests and moods.
Available Interests: science, arts, math, reading, sports, music, technology, nature
Available Moods: happy, frustrated, anxious, excited, tired, distracted, focused, confused

Return the profile as a JSON object with these exact keys and no other text before or after:
{{
    "name": "Sarah",
    "grade_level": 2,
    "personality_traits": ["bright", "anxious", "hesitant"],
    "learning_style": "visual",
    "interests": ["science", "nature", "math"],
    "typical_moods": ["focused", "tired", "distracted"],
    "behavioral_patterns": {{
        "morning": "focused and attentive",
        "afternoon": "becomes tired and distracted",
        "during_group_work": "works well in small groups",
        "during_independent_work": "can maintain focus but may need support",
        "transitions": "handles smoothly with structure"
    }},
    "academic_strengths": ["math", "science experiments"],
    "academic_challenges": ["writing long passages", "speaking in large groups"],
    "social_dynamics": {{
        "peer_interactions": "comfortable in small groups",
        "group_work": "participates well in small settings",
        "teacher_interaction": "may need encouragement to speak up"
    }},
    "support_strategies": ["visual aids", "positive reinforcement", "small group settings"]
}}'''

    def _validate_interests(self, interests: List[str]) -> List[Interest]:
        """Validate and convert interest strings to Interest enums."""
        valid_interests = []
        for interest in interests:
            try:
                valid_interests.append(Interest[interest.upper()])
            except KeyError:
                continue
        return valid_interests

    def _validate_moods(self, moods: List[str]) -> List[Mood]:
        """Validate and convert mood strings to Mood enums."""
        valid_moods = []
        for mood in moods:
            try:
                valid_moods.append(Mood[mood.upper()])
            except KeyError:
                continue
        return valid_moods

    def build_profile_from_text(self, description: str) -> StudentProfile:
        """
        Build a student profile from a text description.

        Args:
            description (str): Natural language description of the student

        Returns:
            StudentProfile: Structured student profile
        """
        # Create prompt for profile generation
        prompt = ChatPromptTemplate.from_template(self.PROFILE_PROMPT)

        messages = prompt.format_messages(description=description.strip())
        # Get LLM response
        response = self.model.invoke(messages)
        # print(f"LLM Response: {response.content}")  # Debug print

        try:
            # Clean up the response content
            cleaned_content = response.content
            if "</think>" in cleaned_content:
                cleaned_content = cleaned_content.split("</think>")[1]
            if "json" in cleaned_content.lower():
                cleaned_content = cleaned_content.replace(
                    "```json", "").strip()
                cleaned_content = cleaned_content.replace("```", "").strip()
            response.content = cleaned_content
            print(f"Cleaned Content: {response.content}")
            # Parse JSON response
            profile_data = json.loads(response.content)

            # Validate and convert enums
            interests = self._validate_interests(
                profile_data.get('interests', []))
            moods = self._validate_moods(profile_data.get('typical_moods', []))

            # Create StudentProfile instance
            return StudentProfile(
                name=profile_data.get('name', 'Student'),
                grade_level=profile_data.get('grade_level', 2),
                personality_traits=profile_data.get('personality_traits', []),
                learning_style=profile_data.get('learning_style', 'visual'),
                interests=interests,
                typical_moods=moods,
                behavioral_patterns=profile_data.get(
                    'behavioral_patterns', {}),
                academic_strengths=profile_data.get('academic_strengths', []),
                academic_challenges=profile_data.get(
                    'academic_challenges', []),
                social_dynamics=profile_data.get('social_dynamics', {}),
                support_strategies=profile_data.get('support_strategies', [])
            )

        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse LLM response: {e}")


def main():
    # Example usage
    builder = StudentProfileBuilder()

    # Example description
    description = """
    Sarah is a bright but sometimes anxious 2nd grader who loves science experiments 
    and reading about nature. She's usually focused in the morning but gets tired 
    and distracted in the afternoon. She works well in small groups but can be 
    hesitant to speak up in larger class discussions. Sarah excels at math but 
    struggles with writing long passages. She benefits from visual aids and 
    frequent positive reinforcement.
    """

    try:
        profile = builder.build_profile_from_text(description)
        print(f"Created profile for {profile.name}")
        print(f"Interests: {[i.value for i in profile.interests]}")
        print(f"Learning style: {profile.learning_style}")
        print(
            f"Key personality traits: {', '.join(profile.personality_traits)}")
    except Exception as e:
        print(f"Error creating profile: {e}")


if __name__ == "__main__":
    main()
