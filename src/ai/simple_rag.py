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
        print(Fore.LIGHTGREEN_EX + f"Searching for {k} relevant documents..." + Style.RESET_ALL)
        dbResults = self.chroma_db.similarity_search_with_score(query, k=k)
        context = "\n\n---\n\n".join([doc.page_content for doc,
                                     _score in dbResults])
        print(Fore.LIGHTGREEN_EX + f"Found {len(dbResults)} relevant documents." + Style.RESET_ALL)

        # Create messages with context
        messages = [
            {"role": "system", "content": "You are a helpful assistant that can help the user understand your knowledge base. Please provide many details. Cite your sources from the context provided."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]

        print(Fore.LIGHTGREEN_EX + f"Generating response..." + Style.RESET_ALL)
        response = self.llm.invoke(messages)
        print(Fore.LIGHTGREEN_EX + f"Response generated." + Style.RESET_ALL)
        return response, context


def main():
    # Initialize RAG system
    rag = SimpleRAG(model_name='gpt-4o') #gpt-4.5-preview-2025-02-27
    printContext = False

    while True:
        # Example query
        query = input(
            Fore.GREEN + "Enter your question (type 'quit' or 'q' to quit): " + Style.RESET_ALL)
        if query.lower() == 'quit' or query.lower() == 'q':
            break
        if query.lower() == 'context' or query.lower() == 'c':
            printContext = True if not printContext else False
            continue
        # Generate response
        print(Fore.LIGHTBLUE_EX, end=" ")
        print("\nResponse:")

        response, context = rag.generate_response(query)
        print(response.content)
        if printContext:
            print(Fore.LIGHTYELLOW_EX + f"\nContext: {context}" + Style.RESET_ALL)
        print(Style.RESET_ALL)


if __name__ == "__main__":
    main()
