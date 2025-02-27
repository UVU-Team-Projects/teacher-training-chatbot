# Project files
from .embedding import EmbeddingGenerator

# External imports
from langchain_ollama import ChatOllama
from colorama import Fore, Style
import pprint
from dotenv import load_dotenv
import os


load_dotenv()


class LlamaRAG:
    def __init__(self, model_name="llama3.2:3b"):
        """
        Initialize the RAG system with Meta's llama models.

        Args:
            model_name (str): llama model name
        """

        # Initialize language model
        self.model = model_name
        # self.client = InferenceClient(
        #     api_key=os.getenv("HUGGINGFACE_API_KEY"),)

        # Initialize Ollama client for local inference
        # or whichever model you have pulled in Ollama
        self.llm = ChatOllama(model=model_name)

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
            {"role": "system", "content": "You are a helpful assistant that can help the user understand your knowledge base. Please provide many details."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]

        response = self.llm.invoke(messages)
        return response


def main():
    # Initialize RAG system
    rag = LlamaRAG(model_name='deepseek-r1:14b')

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
