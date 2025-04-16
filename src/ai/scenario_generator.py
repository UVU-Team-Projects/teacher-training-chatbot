from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import random
from langchain_openai import ChatOpenAI
try:
    # Direct imports (when running the file directly)
    from embedding import EmbeddingGenerator
except ImportError:
    # Relative imports (when imported as a module)
    from .embedding import EmbeddingGenerator
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")


class GradeLevel(Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"


class SubjectMatter(Enum):
    MATH = "mathematics"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    ART = "art"
    MUSIC = "music"
    PHYSICAL_EDUCATION = "physical_education"
    SPECIAL_EDUCATION = "special_education"


class ChallengeType(Enum):
    BEHAVIORAL = "behavioral"
    ACADEMIC = "academic"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    CLASSROOM_MANAGEMENT = "classroom_management"
    DIFFERENTIATION = "differentiation"


@dataclass
class StudentBackground:
    age: int
    grade: int
    learning_style: str
    special_needs: Optional[List[str]] = None
    cultural_background: Optional[str] = None
    language_background: Optional[str] = None


@dataclass
class ClassroomContext:
    class_size: int
    time_of_day: str
    class_duration: int
    previous_activities: List[str]
    classroom_setup: str
    available_resources: List[str]


@dataclass
class Scenario:
    title: str
    description: str
    grade_level: GradeLevel
    subject: SubjectMatter
    challenge_type: ChallengeType
    student_background: StudentBackground
    classroom_context: ClassroomContext
    key_considerations: List[str]
    evidence_based_strategies: List[str]
    research_sources: List[str]


class ScenarioGenerator:
    def __init__(self, llm=None, model_name="gpt-4o-mini"):
        self.llm = llm or ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000
        )
        self.embedding_generator = EmbeddingGenerator()

    def generate_scenario(
        self,
        grade_level: GradeLevel,
        subject: SubjectMatter,
        challenge_type: ChallengeType,
        student_background: StudentBackground,
        classroom_context: ClassroomContext
    ) -> Scenario:
        """
        Generate a realistic classroom management scenario based on provided parameters
        and retrieved knowledge chunks.
        """
        # Retrieve relevant knowledge chunks for the scenario
        context_query = f"classroom management {challenge_type.value} {grade_level.value} {subject.value}"
        response = self.embedding_generator.return_chroma().similarity_search_with_score(
            context_query, k=5)
        knowledge_chunks = "\n\n---\n\n".join(
            [doc.page_content for doc, _score in response])

        # Generate scenario components using the knowledge chunks
        title = self._generate_title(grade_level, subject, challenge_type)
        description = self._generate_description(
            grade_level, subject, challenge_type,
            student_background, classroom_context, knowledge_chunks
        )

        # Extract evidence-based strategies and research sources
        strategies = self._extract_strategies(knowledge_chunks)
        sources = self._extract_sources(knowledge_chunks)

        # Generate key considerations
        considerations = self._generate_considerations(
            student_background, classroom_context, knowledge_chunks
        )

        return Scenario(
            title=title,
            description=description,
            grade_level=grade_level,
            subject=subject,
            challenge_type=challenge_type,
            student_background=student_background,
            classroom_context=classroom_context,
            key_considerations=considerations,
            evidence_based_strategies=strategies,
            research_sources=sources
        )

    def _generate_title(
        self,
        grade_level: GradeLevel,
        subject: SubjectMatter,
        challenge_type: ChallengeType
    ) -> str:
        """Generate a descriptive title for the scenario."""
        return f"{grade_level.value.title()} {subject.value.title()} {challenge_type.value.title()} Challenge"

    def _generate_description(
        self,
        grade_level: GradeLevel,
        subject: SubjectMatter,
        challenge_type: ChallengeType,
        student_background: StudentBackground,
        classroom_context: ClassroomContext,
        knowledge_chunks: str
    ) -> str:
        """Generate a detailed scenario description using the knowledge chunks."""
        # Create a prompt for the LLM to generate a realistic scenario
        prompt = f"""Generate a detailed classroom management scenario with the following parameters:
        - Grade Level: {grade_level.value}
        - Subject: {subject.value}
        - Challenge Type: {challenge_type.value}
        - Student Background: {student_background}
        - Classroom Context: {classroom_context}
        
        Use the following research-based knowledge to inform the scenario:
        {knowledge_chunks}
        
        Create a detailed, realistic scenario that:
        1. Describes the specific situation and context
        2. Includes relevant student behaviors and interactions
        3. Reflects real classroom dynamics
        4. Incorporates evidence-based teaching practices
        5. Addresses the specific challenge type
        """

        # Use the LlamaRAG to generate the description
        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=knowledge_chunks)
        ])
        return response.content

    def _extract_strategies(self, knowledge_chunks: str) -> List[str]:
        """Extract evidence-based strategies from knowledge chunks."""
        prompt = f"""Analyze the following knowledge chunks and extract specific evidence-based teaching strategies:
        {knowledge_chunks}
        
        For each strategy identified:
        1. Ensure it is research-based
        2. Include specific implementation details
        3. Note the expected outcomes
        """
        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=knowledge_chunks)
        ])
        # Parse the response to extract individual strategies
        strategies = [s.strip()
                      for s in response.content.split('\n') if s.strip()]
        return strategies

    def _extract_sources(self, knowledge_chunks: str) -> List[str]:
        """Extract research sources from knowledge chunks."""
        prompt = f"""Identify and extract research sources and references from the following knowledge chunks:
        {knowledge_chunks}
        
        For each source:
        1. Include the author(s)
        2. Include the publication year
        3. Include the title or journal name
        4. Note the relevance to the scenario
        """

        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=knowledge_chunks)
        ])
        # Parse the response to extract individual sources
        sources = [s.strip()
                   for s in response.content.split('\n') if s.strip()]
        return sources

    def _generate_considerations(
        self,
        student_background: StudentBackground,
        classroom_context: ClassroomContext,
        knowledge_chunks: str
    ) -> List[str]:
        """Generate key considerations based on the scenario parameters."""
        prompt = f"""Generate key considerations for this classroom scenario based on:
        Student Background: {student_background}
        Classroom Context: {classroom_context}
        Research Knowledge: {knowledge_chunks}
        
        Consider:
        1. Individual student needs and accommodations
        2. Classroom environment and setup
        3. Cultural and linguistic factors
        4. Available resources and time constraints
        5. Evidence-based best practices
        """

        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=knowledge_chunks)
        ])
        # Parse the response to extract individual considerations
        considerations = [c.strip()
                          for c in response.content.split('\n') if c.strip()]
        return considerations


def generate_random_scenario() -> Scenario:
    """Generate a random scenario with randomized parameters."""
    generator = ScenarioGenerator()

    # Randomly select parameters
    grade_level = random.choice(list(GradeLevel))
    subject = random.choice(list(SubjectMatter))
    challenge_type = random.choice(list(ChallengeType))

    # Create random student background
    student_background = StudentBackground(
        age=random.randint(7,8),
        grade=2,
        learning_style=random.choice(
            ["visual", "auditory", "kinesthetic", "reading/writing"]),
        special_needs=random.choice(
            [None, ["ADHD"], ["Dyslexia"], ["Autism Spectrum"]]),
        cultural_background=random.choice(
            [None, "Hispanic", "Asian", "African American", "Caucasian"]),
        language_background=random.choice(
            [None, "English", "Spanish", "Mandarin"])
    )

    # Create random classroom context
    classroom_context = ClassroomContext(
        class_size=random.randint(15, 35),
        time_of_day=random.choice(["morning", "afternoon", "evening"]),
        class_duration=random.choice([45, 60, 90]),
        previous_activities=["Previous lesson",
                             "Group work", "Individual practice"],
        classroom_setup=random.choice(
            ["Traditional rows", "Group tables", "U-shaped", "Circle"]),
        available_resources=["Textbooks", "Technology",
                             "Manipulatives", "Visual aids"]
    )

    return generator.generate_scenario(
        grade_level=grade_level,
        subject=subject,
        challenge_type=challenge_type,
        student_background=student_background,
        classroom_context=classroom_context
    )


# Move the scenario generation code into a main block
if __name__ == "__main__":
    # This code will only run when scenario_generator.py is executed directly
    scenario = generate_random_scenario()
    print(scenario)

