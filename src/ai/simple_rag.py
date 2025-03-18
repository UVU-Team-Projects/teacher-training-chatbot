# Project files
try:
    from .embedding import EmbeddingGenerator
except ImportError:
    from embedding import EmbeddingGenerator

# External imports
from langchain_openai import ChatOpenAI
from colorama import Fore, Style
import pprint
from dotenv import load_dotenv
import os


load_dotenv()


class SimpleRAG:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the RAG system with OpenAI models.

        Args:
            model_name (str): OpenAI model name (default: gpt-4o-mini)
        """
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Initialize language model
        self.model = model_name
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000
        )

        # Initialize embeddings model with correct device
        self.embeddings_generator = EmbeddingGenerator()
        self.chroma_db = self.embeddings_generator.return_chroma()

    def generate_response(self, query: str, k: int = 5):
        """
        Generate a response using RAG methodology.

        Args:
            query (str): User query
            k (int): Number of relevant documents to retrieve

        Returns:
            str: Generated response
        """
        # Retrieve relevant documents
        dbResults = self.chroma_db.similarity_search_with_score(query, k=k)
        context = "\n\n---\n\n".join([doc.page_content for doc,
                                     _score in dbResults])

        # Create messages with context
        messages = [
            {"role": "system", "content": "You are a helpful assistant to help the teacher. When given a question, use the context to provide a concise answer. No more than three answers."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]

        response = self.llm.invoke(messages)
        return response


def main():
    # Initialize RAG system
    rag = SimpleRAG(model_name='gpt-4o-mini')

    while True:
        # Example query
        query = input(
            Fore.GREEN + "Enter your question (type 'quit' or 'q' to quit): " + Style.RESET_ALL)
        if query.lower() == 'quit' or query.lower() == 'q':
            break

        # Generate response
        print(Fore.LIGHTBLUE_EX, end=" ")
        print("\nResponse:")

        response = rag.generate_response(query)
        print(response.content)
        print(Style.RESET_ALL)


if __name__ == "__main__":
    main()
