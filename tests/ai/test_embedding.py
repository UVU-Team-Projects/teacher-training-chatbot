import pytest
from ai.embedding import EmbeddingGenerator

def test_embedding_initialization():
    """Test embedding generator initialization"""
    embedder = EmbeddingGenerator()
    assert embedder.dimension == 384
    assert embedder.model is not None

def test_single_embedding():
    """Test generating embedding for single text"""
    embedder = EmbeddingGenerator()
    text = "How to handle classroom disruption?"
    embedding = embedder.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)

def test_batch_embedding():
    """Test generating embeddings for multiple texts"""
    embedder = EmbeddingGenerator()
    texts = [
        "How to handle classroom disruption?",
        "What are effective teaching strategies?",
        "How to engage students in online learning?"
    ]
    embeddings = embedder.batch_generate_embeddings(texts)
    
    assert len(embeddings) == len(texts)
    assert all(len(emb) == 384 for emb in embeddings)

def test_embedding_normalization():
    """Test that embeddings are normalized"""
    embedder = EmbeddingGenerator()
    text = "Test normalization"
    embedding = embedder.generate_embedding(text)
    
    # Calculate L2 norm
    import numpy as np
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 1e-6  # Should be approximately 1 