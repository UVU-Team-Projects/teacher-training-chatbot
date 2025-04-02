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

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import numpy as np
import pandas as pd
import json
import glob
import os
import torch

'''
ssh d19559
username:
password:
'''


class EmbeddingGenerator:
    """
    A class to generate embeddings for text using SentenceTransformer.

    This class handles the initialization of the embedding model and provides
    methods for generating embeddings for both single texts and batches.

    Attributes:
        model (SentenceTransformer): The loaded sentence transformer model
        dimension (int): The dimension of generated embeddings (default: 384)
    """

    def __init__(self, model_name: str = 'all-MiniLM-L12-v2'):
        """
        Initialize the EmbeddingGenerator with a specified model.

        Args:
            model_name (str): Name of the sentence transformer model to use
                            Defaults to 'all-MiniLM-L6-v2'
        """
        self.CHROMA_PATH = "data/vectorstore/chroma_db"
        self.embedding_model = model_name
        self.dimension = 384  # Default dimension for the specified model

        self.embeddings = self.get_embedding_function()

    def normalize_text(self, document: Document) -> Document:
        """
        Normalize document content into uniform plain text.

        Args:
            document (Document): Input document to normalize

        Returns:
            Document: Normalized document
        """
        # Extract text content
        text = document.page_content

        # Convert to lowercase
        text = text.lower()

        # Replace multiple spaces with single space
        text = ' '.join(text.split())

        # Remove special characters but keep basic punctuation
        text = ''.join(char for char in text if char.isalnum()
                       or char in ' .,?!-')

        # Create new document with normalized text
        return Document(
            page_content=text,
            metadata=document.metadata
        )

    def load_data_sources(self) -> list:
        """Load documents from multiple data sources using Langchain document loaders."""
        from langchain_community.document_loaders import (
            CSVLoader, JSONLoader, DirectoryLoader,
            UnstructuredMarkdownLoader, PyPDFLoader
        )

        # data_dir = "data/collection"
        data_dir = "data/books"

        # Track files that failed to load
        failed_files = []

        json_documents = []
        # # Load JSON data without normalization
        # print("Loading JSON files...")
        # json_files = [
        #     # {
        #     #     'path': f"{data_dir}/question-responses/second-grade_qa.json",
        #     #     'jq_schema': '.[] | {question: .question, answer: .answer}'
        #     # },
        #     {
        #         'path': f"{data_dir}/writing_example/examples.json",
        #         'jq_schema': '.Examples[] | .[] | {text: .text, capabilities: ."writing-capabilities"[]}'
        #     }
        # ]

        # for json_file in json_files:
        #     if os.path.exists(json_file['path']):
        #         json_loader = JSONLoader(
        #             file_path=json_file['path'],
        #             jq_schema=json_file['jq_schema'],
        #             text_content=False
        #         )
        #         # JSON documents added without normalization
        #         json_documents.extend(json_loader.load())

        # Load and normalize other document types
        documents = []

        # Load Markdown files
        # print("Loading Markdown files...")
        # markdown_dir = f"{data_dir}/markdown_files"
        # if os.path.exists(markdown_dir):
        #     md_loader = DirectoryLoader(
        #         markdown_dir,
        #         glob="**/*.md",
        #         loader_cls=UnstructuredMarkdownLoader
        #     )
        #     documents.extend(md_loader.load())

        # Load PDF files
        print("Loading PDF files...")
        # pdf_dir = f"{data_dir}/pdf_files"
        pdf_dir = data_dir  # Temp for the books

        if os.path.exists(pdf_dir):
            # Get list of PDF files
            pdf_files = glob.glob(os.path.join(
                pdf_dir, "**/*.pdf"), recursive=True)
            print(f"Found {len(pdf_files)} PDF files")

            for pdf_file in pdf_files:
                try:
                    # Load each PDF file individually to isolate errors
                    loader = PyPDFLoader(pdf_file)
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    print(f"Successfully loaded: {pdf_file}")
                except Exception as e:
                    # Record failure and continue
                    failed_files.append(pdf_file)
                    print(f"Error loading file {pdf_file}")
                    print(f"Error details: {str(e)}")

        # If any files failed to load, print a summary
        if failed_files:
            print("\nFailed to load the following files:")
            for failed_file in failed_files:
                print(f" - {failed_file}")
            print(f"Total failed files: {len(failed_files)}")

        # Only normalize non-JSON documents
        normalized_docs = [self.normalize_text(doc) for doc in documents]

        if json_documents:
            return json_documents + normalized_docs
        else:
            return normalized_docs

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks of text.

        Args:
            documents (list[Document]): List of documents to split
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def calculate_chunk_ids(self, chunks: list[Document]) -> list[Document]:
        """
        Calculate unique IDs for each chunk based on its source and sequence number.

        Args:
            chunks (list[Document]): List of document chunks to calculate IDs for
        """
        last_id = None
        current_chunk_index = 0

        for chunk in chunks:
            # Clean up source path to be relative to project root
            full_path = chunk.metadata['source']
            # Find the index of 'data' in the path and slice from there
            data_index = full_path.find('data')
            if data_index != -1:
                source = full_path[data_index:]
            else:
                source = os.path.basename(full_path)

            if source.endswith('second-grade_qa.json'):
                chunk.metadata['source'] = 'question-response'
                seq_num = chunk.metadata['seq_num']
                current_id = f"question-response:{seq_num}"
            else:
                current_id = source

            if current_id == last_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            chunk.metadata['chunk_id'] = f"{current_id}:{current_chunk_index}"
            last_id = current_id
            chunk.metadata['source'] = source

        return chunks

    def get_embedding_function(self):
        """
        Get the embedding function for the Chroma vector store.
        """
        # Initialize embeddings model with correct device
        device = 'cuda' if torch.cuda.is_available(
        ) else 'mps' if torch.backends.mps.is_available() else 'cpu'
        embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        return embeddings

    def add_to_chroma(self, chunks: list[Document]) -> None:
        """
        Add documents to the Chroma vector store.

        Args:
            chunks (list[Document]): List of document chunks to add
        """
        db = Chroma(
            collection_name="rag_db",
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )

        chunks_with_ids = self.calculate_chunk_ids(chunks)

        # Add or Update the documents
        # IDs are always included by default
        existing_items = db.get(include=[])
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        # Only add new documents that don't exist in the DB
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["chunk_id"] not in existing_ids:
                new_chunks.append(chunk)

        # Add new documents to the DB
        if new_chunks:
            new_chunk_ids = [chunk.metadata["chunk_id"]
                             for chunk in new_chunks]
            db.add_documents(new_chunks, ids=new_chunk_ids)
            # db.persist()
            print(f"Added {len(new_chunks)} new chunks to the DB")
        else:
            print("No new chunks to add :)")

    def return_chroma(self):
        """
        Return the Chroma vector store.
        """
        return Chroma(
            collection_name="rag_db",
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )

    def clear_chroma(self):
        """
        Clear the Chroma vector store.
        """
        db = Chroma(
            collection_name="rag_db",
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )
        db.delete_collection()
        # db.persist()

    def construct_chroma(self):
        """
        Construct the Chroma vector store.
        """
        documents = embedder.load_data_sources()
        print(f"Loaded {len(documents)} documents")
        # print(documents[0])
        chunks = embedder.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        # print(chunks[0])
        embedder.add_to_chroma(chunks)


if __name__ == "__main__":
    embedder = EmbeddingGenerator()
    embedder.construct_chroma()
    # embedder.clear_chroma()
