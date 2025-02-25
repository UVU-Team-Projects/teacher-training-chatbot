# Project files
from student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
from embedding import EmbeddingGenerator
from profile_builder import StudentProfileBuilder

# External imports
from dotenv import load_dotenv
from colorama import Fore, Style
import time
from typing import Literal
from langchain_ollama import ChatOllama
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

# Get the absolute path of the project root
root_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the src directory
src_dir = os.path.join(root_dir, 'src')
# Add the src to sys.path
sys.path.append(src_dir)

# Project imports
# Load environment variables
load_dotenv()


class MessageStateWithContext(MessagesState):
    context: str
    student_profile: StudentProfile


class RAG:
    """
    Retrieval Augmented Generation (RAG) pipeline using LangGraph.
    Combines document retrieval with LLM generation for enhanced responses.
    """

    def __init__(self, tools: list[BaseTool] = None, embedding_generator: EmbeddingGenerator = None):
        """
        Initialize the RAG pipeline.

        Args:
            tools: List of tools available to the agent
            embedding_generator: Optional custom embedding generator
        """
        # Initialize core components
        self.tools = tools
        self.tool_node = ToolNode(self.tools)
        self.model = ChatOllama(model="llama3.2:3b").bind_tools(self.tools)
        # "deepseek-r1:14b"

        self.embedding_generator = embedding_generator or EmbeddingGenerator()

        self.PROMPT_TEMPLATE = """
            You are a 2nd grader with the following profile:

            Name: {name}
            Grade Level: {grade_level}
            Personality: {personality_traits}
            Typical Moods: {moods}
            Behavioral Patterns: {behavior}
            Current Interests: {interests}

            Learning Style: {learning_style}
            Academic Strengths: {academic_strengths}
            Academic Challenges: {academic_challenges}
            Support Strategies: {support_strategies}
            Social Dynamics: {social_dynamics}
            
            Match your words, language, and behavior to match this profile.
            The provided context can help you understand how to act and respond. If the context 
            doesn't contain relevant information, please decide how to best respond while
            staying in character.
            
            The user is your teacher. Respond as if you are this specific 2nd grader talking to your teacher.
            
            Context: {context}

            ---

            Answer the teacher's question concisely based on the above context: {question}
        """

    def should_continue(self, state: MessageStateWithContext) -> Literal["tools", END]:
        """Determine whether to continue processing or return response."""
        if state['messages'][-1].tool_calls:
            return "tools"
        return END

    def retrieve(self, state: MessageStateWithContext) -> MessageStateWithContext:
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

    def generate_response(self, state: MessageStateWithContext) -> MessageStateWithContext:
        """Generate a response based on context and user input."""
        context = state.get('context', 'No context available')
        # Get the user's message
        user_message = state['messages'][-1].content

        # Get student profile from state or use default template
        student_profile = state.get(
            'student_profile', STUDENT_TEMPLATES['active_learner'])

        # Format the prompt with student profile information
        prompt_template = ChatPromptTemplate.from_template(
            self.PROMPT_TEMPLATE)
        formatted_message = prompt_template.format_messages(
            name=student_profile['name'],
            grade_level=student_profile['grade_level'],
            personality_traits=", ".join(
                student_profile['personality_traits']),
            moods=", ".join(
                [mood.value for mood in student_profile['typical_moods']]),
            behavior="\n".join(
                [f"{k}: {v}" for k, v in student_profile['behavioral_patterns'].items()]),
            learning_style=student_profile['learning_style'],
            interests=", ".join(
                [interest.value for interest in student_profile.get('interests', [])]),
            academic_strengths=", ".join(
                student_profile['academic_strengths']),
            academic_challenges=", ".join(
                student_profile['academic_challenges']),
            support_strategies=", ".join(
                student_profile['support_strategies']),
            social_dynamics="\n".join(
                [f"{k}: {v}" for k, v in student_profile['social_dynamics'].items()]),
            context=context,
            question=user_message
        )
        # pprint.pprint(student_profile)
        print(formatted_message[-1].content)  # DEBUG
        # Generate response
        response = self.model.invoke(formatted_message)
        return {**state, "messages": state["messages"] + [response]}

    def create_agent(self) -> CompiledStateGraph:
        """Create and compile the agent workflow."""
        # Define workflow graph
        workflow = StateGraph(MessageStateWithContext)

        # Add nodes
        workflow.add_node('retrieve', self.retrieve)
        workflow.add_node('generate', self.generate_response)
        # workflow.add_node('tools', self.tool_node)

        # Configure graph flow
        workflow.set_entry_point("retrieve")
        workflow.add_edge('retrieve', 'generate')
        # workflow.add_conditional_edges("generate", self.should_continue)
        # workflow.add_edge("tools", 'generate')
        workflow.add_edge('generate', END)

        # Compile with memory persistence
        self.agent = workflow.compile(checkpointer=MemorySaver())
        return self.agent


def create_pipeline(tools: list[BaseTool] = None) -> CompiledStateGraph:
    """Create and return a compiled RAG pipeline with specified student profile."""
    return RAG(tools=tools or []).create_agent()


def typing_effect(text: str, delay: float = 0.01) -> None:
    """Print text with a typing animation effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def create_student_profile():
    # Create a student profile
    student = create_student_profile(
        template_name="struggling_student",  # or choose another template
        name="Alex",
        grade_level=2,
        interests=[Interest.SPORTS, Interest.SCIENCE],
        academic_strengths=["mental math", "science experiments"],
        academic_challenges=["reading comprehension", "sitting still"],
        support_strategies=["movement breaks",
                            "hands-on learning", "visual aids"]
    )
    return student


def chat_with_student(agent: CompiledStateGraph, student: StudentProfile, query: str) -> str:
    """Chat with a student profile."""
    # Initialize state with both messages and student profile
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "context": "",
        "student_profile": {
            "name": student.name,
            "grade_level": student.grade_level,
            "personality_traits": student.personality_traits,
            "typical_moods": student.typical_moods,
            "behavioral_patterns": student.behavioral_patterns,
            "learning_style": student.learning_style,
            "interests": student.interests,
            "academic_strengths": student.academic_strengths,
            "academic_challenges": student.academic_challenges,
            "support_strategies": student.support_strategies,
            "social_dynamics": student.social_dynamics
        }
    }

    response = agent.invoke(
        initial_state,
        config={"configurable": {"thread_id": 42}}
    )
    return response["messages"][-1].content


def main() -> None:
    """Run the RAG pipeline in interactive mode."""
    # Create a student profile
    print("Creating student profile...")
    builder = StudentProfileBuilder()
    description = """
    Sarah is a bright but sometimes anxious 2nd grader who loves science experiments 
    and reading about nature. She's usually focused in the morning but gets tired 
    and distracted in the afternoon. She works well in small groups but can be 
    hesitant to speak up in larger class discussions. Sarah excels at math but 
    struggles with writing long passages. She benefits from visual aids and 
    frequent positive reinforcement.    
    """
    student = builder.build_profile_from_text(description)
    print(f"Student profile created: {student}")
    agent = create_pipeline()
    print(Fore.GREEN + f"Student {student.name} is ready! ")

    while True:
        print(Fore.RED + 'Enter "q" to quit.')
        query = input(Fore.GREEN + "Your input: " + Style.RESET_ALL)

        if query.lower() == 'q':
            break

        # Initialize state with both messages and student profile
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "context": "",
            "student_profile": {
                "name": student.name,
                "grade_level": student.grade_level,
                "personality_traits": student.personality_traits,
                "typical_moods": student.typical_moods,
                "behavioral_patterns": student.behavioral_patterns,
                "learning_style": student.learning_style,
                "interests": student.interests,
                "academic_strengths": student.academic_strengths,
                "academic_challenges": student.academic_challenges,
                "support_strategies": student.support_strategies,
                "social_dynamics": student.social_dynamics
            }
        }

        response = agent.invoke(
            initial_state,
            config={"configurable": {"thread_id": 42}}
        )

        print(Fore.LIGHTBLUE_EX, end=" ")
        typing_effect(response["messages"][-1].content)
        print(Style.RESET_ALL)


if __name__ == "__main__":
    main()
