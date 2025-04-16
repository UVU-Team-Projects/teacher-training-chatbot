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

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai.embeddings import OpenAIEmbeddings

from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import numpy as np
# import pandas as pd
# import json
# import glob
import os
import torch


"""
Text Chunking Utility

This module provides functionality to intelligently chunk text documents into semantically coherent sections
using sentence embeddings and cosine similarity. It's particularly useful for processing large documents
while maintaining contextual relationships between sentences.

Requirements:
    - nltk
    - sentence-transformers
    - scikit-learn
    - numpy
    - matplotlib
"""

import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# import matplotlib.pyplot as plt

# Ensure NLTK data is downloaded (only needs to run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK 'punkt' tokenizer data...")
    nltk.download('punkt')
    nltk.download('punkt_tab')


class TextChunker:
    def __init__(self, model_name='sentence-transformers/all-mpnet-base-v1'):
        """Initialize the TextChunker with a specified sentence transformer model."""
        print(f"Initializing TextChunker with model: {model_name}")
        # Check if CUDA is available and set the device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"TextChunker using device: {device}")
        self.model = SentenceTransformer(model_name, device=device)
        self.pool = self.model.start_multi_process_pool()

    def process_text(self, text_content: str, context_window=1, percentile_threshold=95, min_chunk_size=3) -> list[str]:
        """
        Process text content and split it into semantically meaningful chunks.

        Args:
            text_content: The text content to process.
            context_window: Number of sentences to consider on either side for context.
            percentile_threshold: Percentile threshold for identifying breakpoints.
            min_chunk_size: Minimum number of sentences in a chunk.

        Returns:
            list: Semantically coherent text chunk strings.
        """
        if not text_content or not isinstance(text_content, str):
             print("Warning: process_text received empty or invalid content. Returning empty list.")
             return []

        # Tokenize the input text
        sentences = sent_tokenize(text_content)
        if not sentences:
            print("Warning: No sentences found after tokenization. Returning empty list.")
            return []

        contextualized = self._add_context(sentences, context_window)
        if not contextualized:
             print("Warning: Contextualization resulted in empty list. Returning empty list.")
             return []
             
        print(f"  Encoding {len(contextualized)} contextualized sentences...")
        embeddings = self.model.encode_multi_process(contextualized, self.pool, show_progress_bar=True) # Added progress bar

        # Create and refine chunks
        distances = self._calculate_distances(embeddings)
        if not distances:
             print("Warning: Could not calculate distances (likely only one sentence). Returning original text as single chunk.")
             return [text_content] # Return original text if no distances

        breakpoints = self._identify_breakpoints(distances, percentile_threshold)
        initial_chunks = self._create_chunks(sentences, breakpoints)

        # Encode initial chunks for merging step
        if len(initial_chunks) <= 1:
             print("  Only one initial chunk created. Skipping merge step.")
             return initial_chunks # No merging needed if only one chunk

        print(f"  Encoding {len(initial_chunks)} initial chunks for merging...")
        chunk_embeddings = self.model.encode_multi_process(initial_chunks, self.pool, show_progress_bar=True)

        # Merge small chunks for better coherence
        final_chunks = self._merge_small_chunks(initial_chunks, chunk_embeddings, min_chunk_size)

        return final_chunks

    def _add_context(self, sentences, window_size):
        contextualized = []
        for i in range(len(sentences)):
            start = max(0, i - window_size)
            end = min(len(sentences), i + window_size + 1)
            context = ' '.join(sentences[start:end])
            contextualized.append(context)
        return contextualized

    def _calculate_distances(self, embeddings):
        distances = []
        for i in range(len(embeddings) - 1):
            similarity = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            distance = 1 - similarity
            distances.append(distance)
        return distances

    def _identify_breakpoints(self, distances, threshold_percentile):
        threshold = np.percentile(distances, threshold_percentile)
        return [i for i, dist in enumerate(distances) if dist > threshold]

    def _create_chunks(self, sentences, breakpoints):
        chunks = []
        start_idx = 0
        
        for breakpoint in breakpoints:
            chunk = ' '.join(sentences[start_idx:breakpoint + 1])
            chunks.append(chunk)
            start_idx = breakpoint + 1
            
        # Add the final chunk
        final_chunk = ' '.join(sentences[start_idx:])
        if final_chunk: # Ensure final chunk is not empty
            chunks.append(final_chunk)
        
        return chunks

    def _merge_small_chunks(self, chunks, embeddings, min_size):
        if len(chunks) <= 1:
            return chunks # No merging needed if only one chunk

        final_chunks = [chunks[0]]
        merged_embeddings = [embeddings[0]] if len(embeddings) > 0 else [] # Handle empty embeddings

        if not merged_embeddings: # If no embeddings, can't merge based on similarity
             print("Warning: No embeddings provided for merging. Returning initial chunks.")
             return chunks

        for i in range(1, len(chunks)): # Iterate up to the last chunk
            current_chunk_size = len(sent_tokenize(chunks[i])) # Use sentence count for size check

            if current_chunk_size < min_size and i < len(chunks): # Ensure there's a chunk to merge with
                if i + 1 < len(chunks): # Check if a next chunk exists
                     # Calculate similarities with previous (in final_chunks) and next
                     prev_similarity = cosine_similarity([embeddings[i]], [merged_embeddings[-1]])[0][0]
                     next_similarity = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]

                     if prev_similarity >= next_similarity:
                         # Merge with previous chunk
                         print(f"  Merging chunk {i} (size {current_chunk_size}) with previous.")
                         final_chunks[-1] = f"{final_chunks[-1]} {chunks[i]}"
                         # Simple averaging for merged embedding - might need refinement
                         merged_embeddings[-1] = (merged_embeddings[-1] + embeddings[i]) / 2
                     else:
                         # Merge with next chunk (modify the *next* chunk in the original list)
                         print(f"  Merging chunk {i} (size {current_chunk_size}) with next.")
                         chunks[i + 1] = f"{chunks[i]} {chunks[i + 1]}"
                         embeddings[i + 1] = (embeddings[i] + embeddings[i + 1]) / 2
                         # This merged chunk will be processed in the next iteration
                else: # No next chunk, merge with previous
                     print(f"  Merging last small chunk {i} (size {current_chunk_size}) with previous.")
                     final_chunks[-1] = f"{final_chunks[-1]} {chunks[i]}"
                     merged_embeddings[-1] = (merged_embeddings[-1] + embeddings[i]) / 2
            elif i < len(chunks): # If chunk is large enough or it's the last one after potential merge
                final_chunks.append(chunks[i])
                merged_embeddings.append(embeddings[i])


        return final_chunks


class EmbeddingGenerator:
    """
    A class to generate embeddings for text using SentenceTransformer.

    This class handles the initialization of the embedding model and provides
    methods for generating embeddings for both single texts and batches.

    Attributes:
        model (SentenceTransformer): The loaded sentence transformer model
        dimension (int): The dimension of generated embeddings (default: 384)
    """

    def __init__(self):
        """
        Initialize the EmbeddingGenerator with a specified model.

        Args:
            model_name (str): Name of the sentence transformer model to use
                            Defaults to 'all-MiniLM-L6-v2'
        """
        self.CHROMA_PATH = "data/vectorstore/chroma_db"
        # self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.embeddings = HuggingFaceBgeEmbeddings(model_name="all-MiniLM-L6-v2")

        if __name__ == "__main__":
            self.text_chunker = TextChunker()

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
            UnstructuredMarkdownLoader, PyMuPDFLoader, TextLoader
        )

        json_documents = []
        data_dir = "data/"
        all_docs = []

        # Load JSON data (specific handling, no normalization applied here)
        print("Loading JSON files...")
        json_files_config = [
            {
                'path': f"{data_dir}/writing_example/examples.json",
                'jq_schema': '.Examples[] | .[] | {text: .text, capabilities: ."writing-capabilities"[]}'
            }
        ]

        for config in json_files_config:
            if os.path.exists(config['path']):
                try:
                    json_loader = JSONLoader(
                        file_path=config['path'],
                        jq_schema=config['jq_schema'],
                        text_content=False
                    )
                    loaded_json_docs = json_loader.load()
                    print(f"  Loaded {len(loaded_json_docs)} documents from {os.path.basename(config['path'])}")
                    json_documents.extend(loaded_json_docs)
                except Exception as e:
                    print(f"  Error loading JSON file {config['path']}: {e}")
            else:
                print(f"  JSON file not found: {config['path']}")

        # Load and normalize other document types using DirectoryLoader
        print("\nLoading and normalizing other file types...")
        directory_loaders_config = [
            {
                "path": f"{data_dir}/markdown_files",
                "glob": "**/*.md",
                "loader_cls": UnstructuredMarkdownLoader,
                "type": "Markdown"
            },
            {
                "path": f"{data_dir}/pdf_files",
                "glob": "**/*.pdf",
                "loader_cls": PyMuPDFLoader,
                "type": "PDF"
            },
            {
                "path": f"{data_dir}/books",
                "glob": "**/*.pdf",
                "loader_cls": PyMuPDFLoader,
                "type": "PDF"
            },
            {
                "path": f"{data_dir}/education_resources/cult_of_pedagogy/cleaned_texts",
                "glob": "**/*.txt",
                "loader_cls": TextLoader,
                "loader_kwargs": {"encoding": "utf-8"},
                "type": "Text"
            }
        ]

        normalized_docs = []
        for config in directory_loaders_config:
            dir_path = config["path"]
            print(f"Checking for {config['type']} files in: {dir_path}")
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                try:
                    loader_kwargs = config.get("loader_kwargs", {})
                    dir_loader = DirectoryLoader(
                        dir_path,
                        glob=config["glob"],
                        loader_cls=config["loader_cls"],
                        loader_kwargs=loader_kwargs,
                        show_progress=True,
                        use_multithreading=True
                    )
                    loaded_docs = dir_loader.load()
                    if loaded_docs:
                        print(f"  Loaded {len(loaded_docs)} {config['type']} documents. Normalizing...")
                        # Normalize documents loaded by DirectoryLoader
                        normalized_batch = [self.normalize_text(doc) for doc in loaded_docs]
                        normalized_docs.extend(normalized_batch)
                        print(f"  Finished normalizing {len(normalized_batch)} documents.")
                    else:
                        print(f"  No {config['type']} files found matching glob '{config['glob']}' in {dir_path}.")
                except Exception as e:
                    print(f"  Error loading {config['type']} files from {dir_path}: {e}")
            else:
                print(f"  Directory not found: {dir_path}")

        # Combine JSON (un-normalized) and other (normalized) documents
        all_docs = json_documents + normalized_docs
        print(f"\nTotal documents loaded: {len(all_docs)} ({len(json_documents)} JSON, {len(normalized_docs)} normalized)")

        return all_docs

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks using the TextChunker.

        Args:
            documents (list[Document]): List of documents to split.

        Returns:
            list[Document]: List of chunked documents with preserved metadata.
        """
        all_chunk_docs = []
        print(f"\nStarting chunking of {len(documents)} documents...")
        for i, doc in enumerate(documents):
            print(f"Chunking document {i+1}/{len(documents)}: source='{doc.metadata.get('source', 'Unknown')}'")
            if not doc.page_content or not isinstance(doc.page_content, str) or len(doc.page_content.strip()) == 0:
                 print(f"  Skipping document {i+1} due to empty or invalid content.")
                 continue

            try:
                # Use the initialized text_chunker instance
                chunk_strings = self.text_chunker.process_text(doc.page_content)

                doc_chunks = []
                for chunk_text in chunk_strings:
                    # Create new Document objects for each chunk
                    # Crucially, copy metadata from the original document
                    chunk_doc = Document(page_content=chunk_text, metadata=doc.metadata.copy())
                    doc_chunks.append(chunk_doc)

                print(f"  Document split into {len(doc_chunks)} chunks.")
                all_chunk_docs.extend(doc_chunks)

            except Exception as e:
                print(f"  Error chunking document {i+1} (source: {doc.metadata.get('source', 'Unknown')}): {e}")
                # Optionally, add the original document as a single chunk on error
                # all_chunk_docs.append(doc)

        print(f"Finished chunking. Total chunks created: {len(all_chunk_docs)}")
        return all_chunk_docs

    def calculate_chunk_ids(self, chunks: list[Document]) -> list[Document]:
        """
        Calculate unique IDs for each chunk based on its source and sequence number.

        Args:
            chunks (list[Document]): List of document chunks to calculate IDs for
        """
        last_source_doc_path = None # Track the source document path
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get('source', 'unknown_source') # Use get with default

            # Check if this chunk comes from the same original document as the last one
            if source == last_source_doc_path:
                current_chunk_index += 1
            else:
                # Reset index for a new source document
                current_chunk_index = 0
                last_source_doc_path = source # Update the last source path

            # Create chunk ID: source_path:chunk_index
            # Ensure source path is a valid string for ID creation
            source_id_part = str(source).replace(":", "_").replace("\\", "/").replace(" ", "_") # Basic sanitization
            chunk.metadata['chunk_id'] = f"{source_id_part}:{current_chunk_index}"


        return chunks

    def add_to_chroma(self, chunks: list[Document]) -> None:
        """
        Add documents to the Chroma vector store.

        Args:
            chunks (list[Document]): List of document chunks to add
        """
        # Ensure chunks are not empty before proceeding
        if not chunks:
            print("No chunks provided to add_to_chroma. Skipping.")
            return

        db = Chroma(
            collection_name="rag_db",
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )

        # Recalculate chunk IDs after potential splitting changes
        print("Calculating chunk IDs...")
        chunks_with_ids = self.calculate_chunk_ids(chunks)
        print(f"Finished calculating IDs for {len(chunks_with_ids)} chunks.")


        # Add or Update the documents
        try:
             existing_items = db.get(include=[]) # IDs are always included by default
             existing_ids = set(existing_items["ids"])
             print(f"Number of existing documents in DB: {len(existing_ids)}")
        except Exception as e:
             print(f"Error getting existing items from ChromaDB (maybe collection doesn't exist yet?): {e}")
             existing_ids = set() # Assume empty if error

        # Only add new documents that don't exist in the DB
        new_chunks = []
        added_ids = set() # Track IDs we plan to add in this run
        for chunk in chunks_with_ids:
            chunk_id = chunk.metadata.get("chunk_id")
            if chunk_id is None:
                 print(f"Warning: Chunk missing 'chunk_id' metadata. Skipping. Content: {chunk.page_content[:50]}...")
                 continue
            if chunk_id not in existing_ids and chunk_id not in added_ids:
                new_chunks.append(chunk)
                added_ids.add(chunk_id) # Mark as planned for addition

        # Add new documents to the DB
        if new_chunks:
            new_chunk_ids = [chunk.metadata["chunk_id"] for chunk in new_chunks]
            print(f"Attempting to add {len(new_chunks)} new chunks to the DB...")
            try:
                db.add_documents(new_chunks, ids=new_chunk_ids)
                # db.persist() # Persist is often handled automatically or not needed depending on Chroma version/setup
                print(f"Successfully added {len(new_chunks)} new chunks to the DB.")
            except Exception as e:
                print(f"Error adding documents to ChromaDB: {e}")
                # Optional: Log failed chunk IDs or content
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
        print(f"Attempting to delete Chroma collection 'rag_db' from {self.CHROMA_PATH}...")
        try:
            db = Chroma(
                collection_name="rag_db",
                persist_directory=self.CHROMA_PATH,
                embedding_function=self.embeddings
            )
            db.delete_collection()
            print("Chroma collection 'rag_db' deleted successfully.")
            # Persisting might not be necessary after deletion, but check ChromaDB docs if issues arise
            # db.persist()
        except Exception as e:
            # Catch potential errors if the collection doesn't exist
            print(f"Could not delete Chroma collection (it might not exist): {e}")


    def construct_chroma(self):
        """
        Construct the Chroma vector store.
        """
        documents = self.load_data_sources() # Use self.load_data_sources
        print(f"Loaded {len(documents)} documents")
        chunks = self.split_documents(documents) # Use self.split_documents
        print(f"Split into {len(chunks)} chunks")
        self.add_to_chroma(chunks) # Use self.add_to_chroma


if __name__ == "__main__":
    embedder = EmbeddingGenerator()
    # embedder.clear_chroma() # Uncomment to clear DB before constructing
    embedder.construct_chroma() # Uncomment to run the full pipeline
