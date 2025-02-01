from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
import transformers
import torch

import os
import textwrap
import pandas as pd
from dotenv import load_dotenv
import json

load_dotenv()


class OpenAIRAG:
    def __init__(self, model_name="meta-llama/Llama-3.2-3B"):
        """
        Initialize the RAG system with OpenAI's models.

        Args:
            api_key (str): OpenAI API key
            model_name (str): OpenAI model name
        """

        # Initialize language model
        self.model = model_name
        # self.client = InferenceClient(
        #     api_key=os.getenv("HUGGINGFACE_API_KEY"),)
        
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=model_name,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
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

        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the following context to answer the question. "
             "If the context doesn't contain relevant information, please indicate that."),
            ("user", "Context: {context}\n\nQuestion: {question}")
        ])

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
        messages = [
            {"role": "system", "content": "You are a 2nd grader designed to help teachers practice classroom managment. \
             Use the following context to help you know how to act and respond. If the context doesn't contain relevant information,\
              please decided how to best respond while keeping your role."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]

        # Generate response
        # response = self.client.chat.completions.create(model=self.model,
        #                                                messages=messages,
        #                                                max_tokens=500)
        # return response.choices[0].message.content

        response = self.pipeline(messages, max_new_tokens=256)
        return response[0]["generated_text"][-1]

        


def main():
    # Initialize RAG system
    rag = OpenAIRAG()

    # Load and prepare CSV document
    csv_path = "data/collection/question-responses/second_grade_qa.csv"
    df = pd.read_csv(csv_path)

    # Load and prepare JSON document
    json_path = "data/collection/question-responses/second-grade_qa.json"
    with open(json_path, 'r') as f:
        qa_data = json.load(f)

    # Convert JSON data to DataFrame
    json_rows = []
    for qa in qa_data:
        json_rows.append({
            'question': qa['question'],
            'answer': qa['answer']
        })
    json_df = pd.DataFrame(json_rows)

    # Combine DataFrames
    df = pd.concat([df, json_df], ignore_index=True)
    # Convert DataFrame to text format
    # Adjust this based on which columns you want to include
    documents = []
    for _, row in df.iterrows():
        # Convert each row to a string, joining all columns
        doc = " ".join(str(value) for value in row)
        documents.append(doc)

    # Load documents
    rag.load_documents(documents)

    # Example query
    query = "Do you like school?"

    # Generate response
    response = rag.generate_response(query)

    # Print wrapped response
    print("\nQuery:", query)
    print("\nResponse:")
    print(response)
    # print(textwrap.fill(response, width=80))


if __name__ == "__main__":
    main()
