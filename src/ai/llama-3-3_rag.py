from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
from langchain_openai import ChatOpenAI
from langchain_community.llms.ollama import Ollama
import transformers
import torch

import os
import textwrap
import pandas as pd
from dotenv import load_dotenv
import json
import glob

load_dotenv()


class LlamaRAG:
    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct"):
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
        self.llm = Ollama(model='deepseek-r1:14b')

        # Initialize embeddings model with correct device
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        self.vectorstore = None

    def generate_response(self, query, k=3):
        """
        Generate a response using RAG methodology.

        Args:
            query (str): User query
            k (int): Number of relevant documents to retrieve

        Returns:
            str: Generated response
        """
        if not self.vectorstore:
            raise ValueError(
                "No documents loaded. Please load documents first.")

        # Retrieve relevant documents
        retrieved_docs = self.vectorstore.similarity_search(query, k=k)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Create messages with context
        messages = [
            {"role": "system", "content": "You are a 2nd grader. Match your words and language to sound like one. The provided context\
             can help you know how to act and respond. If the context doesn't contain relevant information, please decide how to best respond.\
             The user is your teacher. Respond as if you are a 2nd grader talking to your teacher."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]

        response = self.llm.invoke(messages)
        # print(response)
        return response

# Load data from different sources and combine into a single DataFrame
def load_data_sources():
    # Load CSV data
    print("loading csv")
    csv_path = "data/collection/question-responses/second_grade_qa.csv"
    df = pd.read_csv(csv_path)

    # Load JSON data
    print("loading json")
    json_path = "data/collection/question-responses/second-grade_qa.json"
    with open(json_path, 'r') as f:
        qa_data = json.load(f)
        json_df = pd.DataFrame([{
            'question': qa['question'],
            'answer': qa['answer']
        } for qa in qa_data])

    print("loading examples.json")
    json_path = "data/collection/writing_example/examples.json"
    with open(json_path, 'r') as f:
        examples_data = json.load(f)
        examples_rows = []
        for example in examples_data['Examples']:
            for example_key, example_value in example.items():
                capabilities = example_value.get(
                    'writing-capabilities', [{}])[0]
                text = example_value.get('text', '')
                row = {
                    'example': example_key,
                    'text': text,
                    **capabilities
                }
                examples_rows.append(row)
        examples_df = pd.DataFrame(examples_rows)

    # Load markdown files
    markdown_rows = []
    markdown_dir = "data/collection/markdown_files"

    for file in glob.glob(f"{markdown_dir}/**/*.md", recursive=True):
        with open(file, 'r', encoding='utf-8') as f:
            markdown_rows.append({
                'file': os.path.basename(file),
                'content': f.read()
            })

    # Combine all data sources
    if markdown_rows:
        print("Combining data sources")
        markdown_df = pd.DataFrame(markdown_rows)
        df = pd.concat([df, markdown_df, json_df,
                        examples_df], ignore_index=True)
    else:
        print("no markdown files")
        print("Combining data sources")
        df = pd.concat([df, json_df, examples_df], ignore_index=True)

    return df


class GPTRAG:
    def __init__(self, model_name='gpt-4o-mini') -> None:
        """
        Initialize the RAG system with OpenAI's models.

        Args:
            api_key (str): OpenAI API key
            model_name (str): OpenAI model name
        """

        # Initialize language model
        self.client = ChatOpenAI(
            api_key=os.getenv("GPT_API_KEY"),
            model=model_name,
            max_tokens=500,
            temperature=0.5,
            streaming=True,
        )

        # Initialize embeddings model with correct device
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        self.vectorstore = None

    def load_documents(self, documents):
        """
        Load and process documents into the vector store.

        Args:
            documents (list): List of document texts
        """
        # Split documents into chunks
        texts = self.text_splitter.create_documents(documents)

        # Create vector store
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)

    def generate_response(self, query, k=3):
        """
        Generate a response using RAG methodology.

        Args:
            query (str): User query
            k (int): Number of relevant documents to retrieve

        Returns:
            str: Generated response
        """
        if not self.vectorstore:
            raise ValueError(
                "No documents loaded. Please load documents first.")

        # Retrieve relevant documents
        retrieved_docs = self.vectorstore.similarity_search(query, k=k)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Create messages with context
        messages = [{"role": "assistant", "content": "You are a 2nd grader designed to help teachers practice classroom managment. \
             Use the following context to help you know how to act and respond. If the context doesn't contain relevant information,\
              please decided how to best respond while keeping your role."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
                    ]

        response = self.client.invoke(messages)
        print(response.content)
        return response

    # Load data from different sources and combine into a single DataFrame
    def load_data_sources(self):
        # Load CSV data
        print("loading csv")
        csv_path = "data/collection/question-responses/second_grade_qa.csv"
        df = pd.read_csv(csv_path)

        # Load JSON data
        print("loading json")
        json_path = "data/collection/question-responses/second-grade_qa.json"
        with open(json_path, 'r') as f:
            qa_data = json.load(f)
            json_df = pd.DataFrame([{
                'question': qa['question'],
                'answer': qa['answer']
            } for qa in qa_data])

        # Load markdown files
        markdown_rows = []
        # markdown_dir = "data/collection/markdown_files"

        # for file in glob.glob(f"{markdown_dir}/**/*.md", recursive=True):
        #     with open(file, 'r', encoding='utf-8') as f:
        #         markdown_rows.append({
        #             'file': os.path.basename(file),
        #             'content': f.read()
        #         })

        # Combine all data sources
        if markdown_rows:
            print("Combining data sources")
            markdown_df = pd.DataFrame(markdown_rows)
            df = pd.concat([df, markdown_df, json_df], ignore_index=True)
        else:
            print("no markdown files")
            print("Combining data sources")
            df = pd.concat([df, json_df], ignore_index=True)

        return df


def main():
    # Initialize RAG system
    rag = LlamaRAG()
    # rag = GPTRAG()

    # Load and combine all data
    print("loading data")
    df = load_data_sources()
    # Convert DataFrame to text format
    # Adjust this based on which columns you want to include
    documents = []
    for _, row in df.iterrows():
        # Convert each row to a string, joining all columns
        doc = " ".join(str(value) for value in row)
        documents.append(doc)

    # Load documents
    print("loading documents")
    # load_documents(documents)

    while True:
        # Example query
        query = input("Enter your question (type 'quit' to quit): ")
        if query.lower() == 'quit':
            break

        # Generate response
        # print("\nQuery:", query)
        print("\nResponse:")
        response = rag.generate_response(query)
        print(response)


if __name__ == "__main__":
    main()
