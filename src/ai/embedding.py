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
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma

from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import numpy as np
import pandas as pd
import json
import glob
import os
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Change to ERROR to reduce output

'''
ssh d19559
username:
password:
'''

from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
import numpy as np
import os
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)

class EmbeddingGenerator(Embeddings):
    """Custom embedding generator that adapts SentenceTransformer to LangChain interface"""
    
    def __init__(self):
        # Set cache directory explicitly
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = os.path.join(os.path.expanduser("~"), ".cache", "sentence_transformers")
        self.CHROMA_PATH = "data/vectorstore/chroma_db"
        self.embedding_model = "all-MiniLM-L6-v2"
        self.dimension = 384  # Default dimension for the specified model

        self.embeddings = self.get_embedding_function()
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logging.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def embed_documents(self, texts):
        """Embed a list of documents using SentenceTransformer"""
        if not self.model:
            return [[0.0] * 384 for _ in texts]  # Return empty embeddings as fallback
        
        return self.model.encode(texts).tolist()
    
    def embed_query(self, text):
        """Embed a query text using SentenceTransformer"""
        if not self.model:
            return [0.0] * 384  # Return empty embedding as fallback
        
        return self.model.encode(text).tolist()
    
    # Keep original method for backward compatibility
    def generate_embedding(self, text):
        """Legacy method for backwards compatibility"""
        return self.embed_query(text)
    
    # Add method to return a Chroma collection
    def return_chroma(self):
        """Return a placeholder Chroma collection"""
        from chromadb.config import Settings
        import chromadb
        try:
            client = chromadb.Client(Settings(anonymized_telemetry=False))
            # Get collection if it exists or create a new one
            try:
                collection = client.get_collection("teacher_training")
            except:
                collection = client.create_collection("teacher_training")
            # return collection
            return Chroma(
            collection_name="rag_db",
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )
        except Exception as e:
            logging.error(f"Failed to create Chroma collection: {e}")
            # Return a mock collection to prevent crashes
            return type('MockCollection', (), {'similarity_search_with_score': lambda *args, **kwargs: []})

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

        json_documents = []
        data_dir = "data/collection"

        # Load JSON data without normalization
        print("Loading JSON files...")
        json_files = [
            # {
            #     'path': f"{data_dir}/question-responses/second-grade_qa.json",
            #     'jq_schema': '.[] | {question: .question, answer: .answer}'
            # },
            {
                'path': f"{data_dir}/writing_example/examples.json",
                'jq_schema': '.Examples[] | .[] | {text: .text, capabilities: ."writing-capabilities"[]}'
            }
        ]

        for json_file in json_files:
            if os.path.exists(json_file['path']):
                json_loader = JSONLoader(
                    file_path=json_file['path'],
                    jq_schema=json_file['jq_schema'],
                    text_content=False
                )
                # JSON documents added without normalization
                json_documents.extend(json_loader.load())

        # Load and normalize other document types
        documents = []

        # Load Markdown files
        print("Loading Markdown files...")
        markdown_dir = f"{data_dir}/markdown_files"
        if os.path.exists(markdown_dir):
            md_loader = DirectoryLoader(
                markdown_dir,
                glob="**/*.md",
                loader_cls=UnstructuredMarkdownLoader
            )
            documents.extend(md_loader.load())

        # Load PDF files
        print("Loading PDF files...")
        pdf_dir = f"{data_dir}/pdf_files"
        if os.path.exists(pdf_dir):
            pdf_loader = DirectoryLoader(
                pdf_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())

        # Only normalize non-JSON documents
        normalized_docs = [self.normalize_text(doc) for doc in documents]

        return json_documents + normalized_docs

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
        embeddings = HuggingFaceBgeEmbeddings(
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
        existing_items = db.get(include=[]) # IDs are always included by default
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        # Only add new documents that don't exist in the DB
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["chunk_id"] not in existing_ids:
                new_chunks.append(chunk)

        # Add new documents to the DB
        if new_chunks:
            new_chunk_ids = [chunk.metadata["chunk_id"] for chunk in new_chunks]
            db.add_documents(new_chunks, ids=new_chunk_ids)
            # db.persist()
            print(f"Added {len(new_chunks)} new chunks to the DB")
        else:
            print("No new chunks to add :)")

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

    def load_classroom_management_data(self, force_reload=False) -> list:
        """
        Load documents from classroom management sources using Langchain document loaders.
        
        Args:
            force_reload: Whether to force rebuild the vector database even if it exists
            
        Returns:
            List of loaded documents
        """
        from langchain_community.document_loaders import (
            UnstructuredMarkdownLoader, PyPDFLoader, DirectoryLoader
        )
        
        documents = []
        data_dir = "data/books"
        
        # Load classroom management books and resources
        print("Loading classroom management books...")
        book_files = [
            "classroom_management_that_works_research_based_strategies_for_every_teacher.pdf",
            "effective_classroom_management_a_teacher_s_guide.pdf",
            "a_teachers_guide_to_successful_classroom_management_and_differentiated_instruction.pdf",
            "classroom_teacher_s_behavior_management_toolbox_the_roger_pierangelo_george_giuliani.pdf"
        ]
        
        for book in book_files:
            book_path = f"{data_dir}/{book}"
            if os.path.exists(book_path):
                print(f"Loading {book}...")
                try:
                    loader = PyPDFLoader(book_path)
                    book_docs = loader.load()
                    # Add source information to metadata
                    for doc in book_docs:
                        doc.metadata["source"] = book
                    documents.extend(book_docs)
                    print(f"Loaded {len(book_docs)} pages from {book}")
                except Exception as e:
                    print(f"Error loading {book}: {e}")
        
        # Load any additional classroom management markdown files
        markdown_dir = "data/collection/markdown_files"
        if os.path.exists(markdown_dir):
            md_loader = DirectoryLoader(
                markdown_dir,
                glob="**/*classroom*.md",  # Only load files with "classroom" in the name
                loader_cls=UnstructuredMarkdownLoader
            )
            markdown_docs = md_loader.load()
            print(f"Loaded {len(markdown_docs)} markdown files about classroom management")
            documents.extend(markdown_docs)
        
        # Normalize and split the documents
        print(f"Splitting {len(documents)} documents into chunks...")
        chunks = self.split_documents(documents)
        print(f"Created {len(chunks)} chunks for indexing")
        
        # Add to Chroma vector store if requested
        if force_reload:
            print("Adding classroom management content to vector store...")
            self.add_to_chroma(chunks)
            print("Classroom management content added to vector store")
        
        return chunks
        
    def construct_classroom_management_db(self):
        """
        Construct a dedicated vector database for classroom management content.
        """
        print("Building classroom management knowledge base...")
        chunks = self.load_classroom_management_data(force_reload=True)
        print(f"Loaded and processed {len(chunks)} chunks")
        print("Classroom management knowledge base is ready for use")
        
    def construct_chroma(self):
        """
        Construct the Chroma vector store.
        """
        documents = self.load_data_sources()
        print(f"Loaded {len(documents)} documents")
        # print(documents[0])
        chunks = self.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        # print(chunks[0])
        self.add_to_chroma(chunks)
        
        # Also load classroom management content
        self.load_classroom_management_data()

if __name__ == "__main__":
    embedder = EmbeddingGenerator()
    # Choose what to build
    # embedder.construct_chroma()  # Build general knowledge base
    embedder.construct_classroom_management_db()  # Build classroom management knowledge base
    # embedder.clear_chroma()