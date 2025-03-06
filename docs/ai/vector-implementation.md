# AI Components with Vector Storage Guide

## Overview

This guide details how to implement AI components that utilize vector storage for the Teacher Training Chatbot. The system uses embeddings for semantic search and similarity matching of educational scenarios.

## Components

### 1. Embedding Generation
```python
# ai/embedding.py
from sentence_transformers import SentenceTransformer
from typing import List, Union
import torch

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Matches database schema
        
    def generate_embedding(self, text: Union[str, List[str]]) -> List[float]:
        """Generate embeddings for text input"""
        with torch.no_grad():
            embeddings = self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_tensor=True
            )
            return embeddings.cpu().numpy().tolist()
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return self.generate_embedding(texts)
```

### 2. Scenario Manager
```python
# ai/scenario_manager.py
from typing import Dict, List
from database.vector_ops import VectorOperations
from ai.embedding import EmbeddingGenerator

class ScenarioManager:
    def __init__(self):
        self.vector_ops = VectorOperations()
        self.embedder = EmbeddingGenerator()
        
    async def create_scenario(self, scenario_data: Dict[str, str]):
        """Create a new teaching scenario with embeddings"""
        # Generate embedding for scenario description
        embedding = self.embedder.generate_embedding(
            f"{scenario_data['name']} {scenario_data['description']}"
        )
        
        # Store scenario with embedding
        scenario_id = await self.vector_ops.store_scenario(
            name=scenario_data['name'],
            description=scenario_data['description'],
            expected_response=scenario_data['expected_response'],
            embedding=embedding
        )
        return scenario_id
    
    async def find_similar_scenarios(self, query: str, threshold: float = 0.8):
        """Find similar teaching scenarios"""
        # Generate embedding for query
        query_embedding = self.embedder.generate_embedding(query)
        
        # Search for similar scenarios
        similar_scenarios = await self.vector_ops.find_similar_scenarios(
            query_embedding=query_embedding,
            threshold=threshold
        )
        return similar_scenarios
```

### 3. Response Generator
```python
# ai/response_generator.py
from typing import List, Dict
from ai.llm_service import LLMService
from ai.scenario_manager import ScenarioManager

class ResponseGenerator:
    def __init__(self):
        self.llm = LLMService()
        self.scenario_manager = ScenarioManager()
        
    async def generate_response(self, query: str) -> Dict:
        """Generate response using similar scenarios as context"""
        # Find similar scenarios
        similar_scenarios = await self.scenario_manager.find_similar_scenarios(
            query=query,
            threshold=0.8
        )
        
        # Prepare context from similar scenarios
        context = self._prepare_context(similar_scenarios)
        
        # Generate response using LLM
        response = await self.llm.generate_response(
            query=query,
            context=context
        )
        
        return {
            'response': response,
            'similar_scenarios': similar_scenarios
        }
    
    def _prepare_context(self, scenarios: List[Dict]) -> str:
        """Prepare context from similar scenarios"""
        context_parts = []
        for scenario in scenarios:
            context_parts.append(
                f"Scenario: {scenario['name']}\n"
                f"Description: {scenario['description']}\n"
                f"Expected Response: {scenario['expected_response']}\n"
            )
        return "\n".join(context_parts)
```

### 4. Feedback Generator
```python
# ai/feedback_generator.py
from typing import Dict
from database.vector_ops import VectorOperations
from ai.embedding import EmbeddingGenerator

class FeedbackGenerator:
    def __init__(self):
        self.vector_ops = VectorOperations()
        self.embedder = EmbeddingGenerator()
        
    async def generate_feedback(self, 
                              teacher_response: str,
                              expected_response: str) -> Dict:
        """Generate feedback for teacher response"""
        # Generate embeddings
        response_embedding = self.embedder.generate_embedding(teacher_response)
        expected_embedding = self.embedder.generate_embedding(expected_response)
        
        # Calculate similarity
        similarity = self._calculate_similarity(
            response_embedding,
            expected_embedding
        )
        
        # Find relevant feedback template
        feedback = await self._get_feedback_template(
            similarity,
            teacher_response
        )
        
        return {
            'similarity': similarity,
            'feedback': feedback,
            'areas_for_improvement': self._identify_improvements(similarity)
        }
    
    def _calculate_similarity(self, 
                            embedding1: List[float],
                            embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        return cosine_similarity(embedding1, embedding2)
    
    async def _get_feedback_template(self,
                                   similarity: float,
                                   response: str) -> str:
        """Get appropriate feedback template based on similarity"""
        category = self._get_feedback_category(similarity)
        
        # Find relevant feedback template
        template = await self.vector_ops.find_similar_feedback_template(
            response_embedding=self.embedder.generate_embedding(response),
            category=category
        )
        return template['template_text']
    
    def _get_feedback_category(self, similarity: float) -> str:
        """Determine feedback category based on similarity score"""
        if similarity >= 0.9:
            return 'excellent'
        elif similarity >= 0.7:
            return 'good'
        elif similarity >= 0.5:
            return 'needs_improvement'
        else:
            return 'requires_revision'
    
    def _identify_improvements(self, similarity: float) -> List[str]:
        """Identify areas for improvement based on similarity score"""
        improvements = []
        if similarity < 0.9:
            improvements.append("Consider incorporating more specific examples")
        if similarity < 0.7:
            improvements.append("Review the key teaching principles")
        if similarity < 0.5:
            improvements.append("Focus on alignment with expected outcomes")
        return improvements
```

## Integration Example

### Complete Interaction Flow
```python
# ai/interaction_handler.py
from typing import Dict
from ai.scenario_manager import ScenarioManager
from ai.response_generator import ResponseGenerator
from ai.feedback_generator import FeedbackGenerator

class InteractionHandler:
    def __init__(self):
        self.scenario_manager = ScenarioManager()
        self.response_generator = ResponseGenerator()
        self.feedback_generator = FeedbackGenerator()
    
    async def handle_interaction(self, query: str) -> Dict:
        """Handle complete interaction flow"""
        try:
            # Generate response
            response_data = await self.response_generator.generate_response(query)
            
            # Generate feedback
            feedback_data = await self.feedback_generator.generate_feedback(
                teacher_response=response_data['response'],
                expected_response=response_data['similar_scenarios'][0]['expected_response']
            )
            
            # Store interaction
            await self._store_interaction(
                query=query,
                response=response_data['response'],
                feedback=feedback_data
            )
            
            return {
                'response': response_data['response'],
                'feedback': feedback_data['feedback'],
                'similarity': feedback_data['similarity'],
                'improvements': feedback_data['areas_for_improvement']
            }
            
        except Exception as e:
            logger.error(f"Error handling interaction: {str(e)}")
            raise
    
    async def _store_interaction(self,
                               query: str,
                               response: str,
                               feedback: Dict):
        """Store interaction details"""
        await self.vector_ops.store_interaction(
            query=query,
            response=response,
            similarity_score=feedback['similarity']
        )
```

## Performance Optimization

### 1. Batch Processing
```python
# ai/batch_processor.py
from typing import List, Dict
import asyncio
from ai.embedding import EmbeddingGenerator

class BatchProcessor:
    def __init__(self, batch_size: int = 32):
        self.embedder = EmbeddingGenerator()
        self.batch_size = batch_size
    
    async def process_scenarios(self, scenarios: List[Dict]):
        """Process scenarios in batches"""
        for i in range(0, len(scenarios), self.batch_size):
            batch = scenarios[i:i + self.batch_size]
            
            # Generate embeddings in parallel
            embeddings = await asyncio.gather(*[
                self.embedder.generate_embedding(
                    f"{s['name']} {s['description']}"
                )
                for s in batch
            ])
            
            # Store scenarios with embeddings
            await self.vector_ops.batch_store_scenarios([
                {**s, 'embedding': e}
                for s, e in zip(batch, embeddings)
            ])
```

### 2. Caching
```python
# ai/caching.py
from functools import lru_cache
from ai.embedding import EmbeddingGenerator

class CachedEmbedding:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
    
    @lru_cache(maxsize=1000)
    def get_cached_embedding(self, text: str):
        """Get cached embedding for text"""
        return self.embedder.generate_embedding(text)
```

## Testing

### 1. Unit Tests
```python
# tests/ai/test_vector_components.py
import pytest
from ai.embedding import EmbeddingGenerator
from ai.scenario_manager import ScenarioManager

async def test_embedding_generation():
    embedder = EmbeddingGenerator()
    text = "How to handle classroom disruption?"
    embedding = embedder.generate_embedding(text)
    
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)

async def test_similar_scenarios():
    manager = ScenarioManager()
    query = "classroom management techniques"
    results = await manager.find_similar_scenarios(query)
    
    assert len(results) > 0
    assert all('similarity' in r for r in results)
```

### 2. Integration Tests
```python
# tests/ai/test_integration.py
async def test_complete_interaction():
    handler = InteractionHandler()
    query = "How to engage students in online learning?"
    
    result = await handler.handle_interaction(query)
    
    assert 'response' in result
    assert 'feedback' in result
    assert 'similarity' in result
    assert 'improvements' in result
``` 