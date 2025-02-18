"""
Embedding Generation Module for Teacher Training Chatbot

This module handles the generation of embeddings for scenarios, responses, and queries
using the SentenceTransformer model. It provides both single and batch embedding
generation capabilities.

Classes:
    EmbeddingGenerator: Main class for generating and managing embeddings.

Example:
    embedder = EmbeddingGenerator()
    embedding = embedder.generate_embedding("How to handle classroom disruption?")
"""

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import json
import glob
import os
import torch


class EmbeddingGenerator:
    """
    A class to generate embeddings for text using SentenceTransformer.

    This class handles the initialization of the embedding model and provides
    methods for generating embeddings for both single texts and batches.

    Attributes:
        model (SentenceTransformer): The loaded sentence transformer model
        dimension (int): The dimension of generated embeddings (default: 384)
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the EmbeddingGenerator with a specified model.

        Args:
            model_name (str): Name of the sentence transformer model to use
                            Defaults to 'all-MiniLM-L6-v2'
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Default dimension for the specified model

        # Initialize embeddings model with correct device
        device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

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

        # Convert DataFrame to text format
        # Adjust this based on which columns you want to include
        documents = []
        for _, row in df.iterrows():
            # Convert each row to a string, joining all columns
            doc = " ".join(str(value) for value in row)
            documents.append(doc)

        return documents

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

    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding for a single text input.

        Args:
            text (str): The input text to generate embedding for

        Returns:
            list: A normalized embedding vector of dimension self.dimension

        Raises:
            ValueError: If text is empty or not a string
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string")

        embedding = self.model.encode(text)
        return self._normalize_embedding(embedding)

    def batch_generate_embeddings(self, texts: list) -> list:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts (list): List of input texts to generate embeddings for

        Returns:
            list: List of normalized embedding vectors

        Raises:
            ValueError: If texts is empty or contains invalid entries
        """
        if not texts or not all(isinstance(t, str) and t.strip() for t in texts):
            raise ValueError("All inputs must be non-empty strings")

        embeddings = self.model.encode(texts)
        return [self._normalize_embedding(emb) for emb in embeddings]

    def _normalize_embedding(self, embedding: np.ndarray) -> list:
        """
        Normalize an embedding vector to unit length.

        Args:
            embedding (np.ndarray): The embedding vector to normalize

        Returns:
            list: Normalized embedding vector as a list
        """
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()

# ... existing code ...
