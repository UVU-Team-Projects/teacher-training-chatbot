from langchain_ollama import OllamaLLM
from typing import Dict, List, Optional
from embedding import EmbeddingGenerator
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
'''
Make sure ollama is running:
ollama serve
Install ollama model if needed:
ollama pull llama3.2:3b
'''
class TeacherTrainingChatbot:
    def __init__(self):
        """Initialize the teacher training chatbot with Llama model and educational components"""
        try:
            self.llm = OllamaLLM(model="llama3.2:3b")
            logger.info("Successfully initialized Llama model")
        except Exception as e:
            logger.error(f"Failed to initialize Llama model: {str(e)}")
            raise

        self.embedding_generator = EmbeddingGenerator()
        # Conversation history for context
        self.conversation_history = []

    def retrieve_context(self, query: str, k: int = 5) -> str:
        """Retrieve context from the embedding generator
        Args:
            query (str): The query to search for
            k (int): The number of results to return
        Returns:
            str: The context
        """
        db = self.embedding_generator.return_chroma()
        results = db.similarity_search_with_score(query, k=k)
        context = "\n\n---\n\n".join([doc.page_content for doc,
                                     _score in results])
        return context

    def invoke_agent(self, query: str, student_profile: Dict = None, scenario: Dict = None) -> str:
        """Invoke the agent to generate a response
        Args:
            query (str): The query to search for
        Returns:
            str: The response
        """
        context = self.retrieve_context(query)
        prompt = self.format_prompt(query, student_profile, scenario, context)
        response = self.llm.invoke(prompt)
        self.conversation_history.append({"role": "user", "query": query})
        self.conversation_history.append({"role": "assistant", "response": response})
        return response

    def format_prompt(self, query: str, student_profile: Dict = None, scenario: Dict = None, context: str = None) -> str:
        """Format the prompt for the agent
        Args:
            query (str): The query to search for
            student_profile (Dict): The student profile
            scenario (Dict): The scenario
            context (str): The context
        """
        prompt = f"""
        You are a teacher training chatbot.
        You are given a query. A student profile, and a scenario may be provided.
        You need to generate a response to the query based on the student profile and scenario if provided.
        If no student profile or scenario is provided, you need to generate a response to the query based on the context.
        Here is the query:
        {query}
        Here is the student profile:
        {student_profile}
        Here is the scenario:
        {scenario}
        Here is the context:
        {context}
        """
        return prompt

def main():
    """Test the chatbot functionality"""
    try:
        # Initialize chatbot
        chatbot = TeacherTrainingChatbot()
        
        response = chatbot.invoke_agent("What should students accomplish while at school?")
        print(response)
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 