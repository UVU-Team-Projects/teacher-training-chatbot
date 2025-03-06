# RAG and LLM Fine-tuning Guide

## Overview

This guide explains how to implement Retrieval-Augmented Generation (RAG) and fine-tune Large Language Models for the Teacher Training Chatbot.

## RAG Implementation

### 1. Document Preparation
```python
# ai/document_processor.py
from typing import List, Dict
from ai.embedding import EmbeddingGenerator

class DocumentProcessor:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        
    def process_teaching_documents(self, documents: List[Dict]):
        """Process teaching documents for RAG"""
        processed_docs = []
        for doc in documents:
            # Split document into chunks
            chunks = self._chunk_document(doc['content'])
            
            # Generate embeddings for chunks
            chunk_embeddings = self.embedder.batch_generate_embeddings(chunks)
            
            # Store chunks with metadata
            for chunk, embedding in zip(chunks, chunk_embeddings):
                processed_docs.append({
                    'content': chunk,
                    'embedding': embedding,
                    'metadata': {
                        'source': doc['source'],
                        'category': doc['category'],
                        'topic': doc['topic']
                    }
                })
        return processed_docs
    
    def _chunk_document(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split document into chunks with overlap"""
        # Implementation of text chunking logic
        # Returns list of text chunks
```

### 2. RAG Query Pipeline
```python
# ai/rag_pipeline.py
from typing import List, Dict
from ai.document_processor import DocumentProcessor
from ai.llm_service import LLMService

class RAGPipeline:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.llm = LLMService()
        self.vector_ops = VectorOperations()
        
    async def process_query(self, query: str) -> Dict:
        """Process query using RAG pipeline"""
        # 1. Generate query embedding
        query_embedding = self.doc_processor.embedder.generate_embedding(query)
        
        # 2. Retrieve relevant documents
        relevant_docs = await self.vector_ops.find_similar_documents(
            query_embedding,
            threshold=0.7,
            limit=3
        )
        
        # 3. Prepare context from retrieved documents
        context = self._prepare_context(relevant_docs)
        
        # 4. Generate response using LLM
        response = await self.llm.generate_response(
            query=query,
            context=context
        )
        
        return {
            'response': response,
            'sources': [doc['metadata'] for doc in relevant_docs]
        }
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        for doc in documents:
            context_parts.append(
                f"Source: {doc['metadata']['source']}\n"
                f"Content: {doc['content']}\n"
            )
        return "\n\n".join(context_parts)
```

### 3. Document Management
```python
# ai/document_manager.py
class DocumentManager:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_ops = VectorOperations()
    
    async def add_teaching_resource(self, resource: Dict):
        """Add new teaching resource to RAG system"""
        # Process document
        processed_chunks = self.processor.process_teaching_documents([resource])
        
        # Store chunks with embeddings
        for chunk in processed_chunks:
            await self.vector_ops.store_document(
                content=chunk['content'],
                embedding=chunk['embedding'],
                metadata=chunk['metadata']
            )
```

## LLM Fine-tuning

### 1. Dataset Preparation
```python
# ai/dataset_preparation.py
from typing import List, Dict
import pandas as pd

class DatasetPreparator:
    def prepare_training_data(self, scenarios: List[Dict]) -> pd.DataFrame:
        """Prepare scenarios for fine-tuning"""
        training_data = []
        for scenario in scenarios:
            # Format as instruction-response pair
            training_example = {
                'instruction': (
                    f"Scenario: {scenario['name']}\n"
                    f"Description: {scenario['description']}\n"
                    "Provide an appropriate teacher response:"
                ),
                'response': scenario['expected_response'],
                'category': scenario['category']
            }
            training_data.append(training_example)
        return pd.DataFrame(training_data)
    
    def validate_dataset(self, df: pd.DataFrame) -> bool:
        """Validate training dataset"""
        # Check required columns
        required_cols = ['instruction', 'response']
        if not all(col in df.columns for col in required_cols):
            return False
        
        # Check for empty values
        if df[required_cols].isna().any().any():
            return False
        
        # Check text lengths
        if (df['instruction'].str.len() < 10).any():
            return False
            
        return True
```

### 2. Fine-tuning Pipeline
```python
# ai/fine_tuning.py
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
import torch

class ModelFineTuner:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
    def prepare_model(self):
        """Prepare model for fine-tuning"""
        # Add special tokens if needed
        special_tokens = {
            "pad_token": "[PAD]",
            "sep_token": "[SEP]",
            "scenario_token": "[SCENARIO]",
            "response_token": "[RESPONSE]"
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def train(self, 
             train_dataset,
             validation_dataset,
             output_dir: str,
             num_epochs: int = 3):
        """Fine-tune the model"""
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_steps=500,
            logging_dir="./logs",
            logging_steps=100,
            eval_steps=500,
            save_steps=1000,
            evaluation_strategy="steps"
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=validation_dataset
        )
        
        trainer.train()
```

### 3. Model Evaluation
```python
# ai/model_evaluation.py
from typing import List, Dict
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

class ModelEvaluator:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
    
    def evaluate_responses(self, 
                         predictions: List[str],
                         ground_truth: List[str]) -> Dict:
        """Evaluate model responses"""
        # Calculate embedding similarities
        similarities = []
        for pred, truth in zip(predictions, ground_truth):
            pred_emb = self.embedder.generate_embedding(pred)
            truth_emb = self.embedder.generate_embedding(truth)
            similarity = cosine_similarity(pred_emb, truth_emb)
            similarities.append(similarity)
        
        # Calculate metrics
        avg_similarity = np.mean(similarities)
        
        return {
            'average_similarity': avg_similarity,
            'min_similarity': min(similarities),
            'max_similarity': max(similarities),
            'std_similarity': np.std(similarities)
        }
```

## Usage Examples

### 1. Using RAG Pipeline
```python
# Example: Process a teaching query using RAG
rag_pipeline = RAGPipeline()
result = await rag_pipeline.process_query(
    "How should I handle a student who consistently disrupts class?"
)
print(f"Response: {result['response']}")
print(f"Sources used: {result['sources']}")
```

### 2. Fine-tuning Model
```python
# Example: Fine-tune model on teaching scenarios
# 1. Prepare dataset
preparator = DatasetPreparator()
df = preparator.prepare_training_data(teaching_scenarios)

# 2. Fine-tune model
fine_tuner = ModelFineTuner()
fine_tuner.prepare_model()
fine_tuner.train(
    train_dataset=train_data,
    validation_dataset=val_data,
    output_dir="./fine_tuned_model",
    num_epochs=3
)

# 3. Evaluate results
evaluator = ModelEvaluator()
metrics = evaluator.evaluate_responses(predictions, ground_truth)
print(f"Evaluation metrics: {metrics}")
```

## Best Practices

### 1. RAG Implementation
- Maintain diverse and high-quality teaching resources
- Implement proper document chunking strategies
- Regular updates to the document store
- Monitor retrieval quality and relevance

### 2. Fine-tuning
- Start with a pre-trained model suitable for instruction following
- Use high-quality, diverse teaching scenarios
- Implement proper validation splits
- Monitor for overfitting
- Regular evaluation of model performance

### 3. Performance Optimization
- Batch process documents for RAG
- Implement caching for frequently accessed documents
- Use gradient accumulation for fine-tuning
- Monitor GPU memory usage 