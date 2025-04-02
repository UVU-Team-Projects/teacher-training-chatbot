import pytest
from ai.rag_pipeline import RAGPipeline
from ai.document_processor import DocumentProcessor
from database.vector_ops import VectorOperations

@pytest.fixture
def sample_documents():
    """Sample teaching documents"""
    return [{
        'content': '''
        Effective classroom management strategies include:
        1. Setting clear expectations
        2. Establishing routines
        3. Using positive reinforcement
        4. Addressing disruptions promptly
        5. Creating an engaging learning environment
        ''',
        'source': 'Teaching Best Practices Guide',
        'category': 'Classroom Management',
        'topic': 'Behavior Management'
    }]

@pytest.fixture
async def initialized_pipeline():
    """Setup RAG pipeline with initialized components"""
    pipeline = RAGPipeline()
    await pipeline.initialize()
    return pipeline

@pytest.mark.asyncio
async def test_document_processing(sample_documents):
    """Test document processing and chunking"""
    processor = DocumentProcessor()
    processed_docs = processor.process_teaching_documents(sample_documents)
    
    assert len(processed_docs) > 0
    for doc in processed_docs:
        assert 'content' in doc
        assert 'embedding' in doc
        assert 'metadata' in doc
        assert len(doc['embedding']) == 384
        assert doc['metadata']['source'] == sample_documents[0]['source']
        assert doc['metadata']['category'] == sample_documents[0]['category']

@pytest.mark.asyncio
async def test_document_storage(initialized_pipeline, sample_documents):
    """Test storing processed documents"""
    # Process and store documents
    await initialized_pipeline.add_documents(sample_documents)
    
    # Verify storage
    vector_ops = VectorOperations()
    query = "classroom management strategies"
    query_embedding = initialized_pipeline.embedder.generate_embedding(query)
    
    results = await vector_ops.find_similar_documents(
        query_embedding=query_embedding,
        threshold=0.5,
        limit=5
    )
    
    assert len(results) > 0
    assert all('content' in doc for doc in results)
    assert all('similarity' in doc for doc in results)

@pytest.mark.asyncio
async def test_query_processing(initialized_pipeline, sample_documents):
    """Test complete query processing"""
    # First add some documents
    await initialized_pipeline.add_documents(sample_documents)
    
    # Test query
    query = "How should I handle classroom disruptions?"
    result = await initialized_pipeline.process_query(query)
    
    assert 'response' in result
    assert 'sources' in result
    assert len(result['sources']) > 0
    assert isinstance(result['response'], str)
    assert len(result['response']) > 0

@pytest.mark.asyncio
async def test_context_preparation(initialized_pipeline, sample_documents):
    """Test context preparation from retrieved documents"""
    # Add documents
    await initialized_pipeline.add_documents(sample_documents)
    
    # Get context for a query
    query = "classroom management"
    context = await initialized_pipeline.prepare_context(query)
    
    assert isinstance(context, str)
    assert len(context) > 0
    assert "classroom management" in context.lower()

@pytest.mark.asyncio
async def test_response_generation(initialized_pipeline):
    """Test LLM response generation"""
    query = "How to engage students?"
    context = "Effective engagement strategies include active learning and interactive discussions."
    
    response = await initialized_pipeline.generate_response(
        query=query,
        context=context
    )
    
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_error_handling(initialized_pipeline):
    """Test error handling in RAG pipeline"""
    # Test with empty query
    with pytest.raises(ValueError):
        await initialized_pipeline.process_query("")
    
    # Test with invalid document
    with pytest.raises(ValueError):
        await initialized_pipeline.add_documents([{'invalid': 'document'}])

@pytest.mark.asyncio
async def test_source_attribution(initialized_pipeline, sample_documents):
    """Test source attribution in responses"""
    # Add documents
    await initialized_pipeline.add_documents(sample_documents)
    
    # Process query
    query = "What are effective teaching strategies?"
    result = await initialized_pipeline.process_query(query)
    
    assert 'sources' in result
    for source in result['sources']:
        assert 'source' in source
        assert 'category' in source
        assert source['source'] == sample_documents[0]['source']

@pytest.mark.asyncio
async def test_performance_metrics(initialized_pipeline):
    """Test performance metrics collection"""
    query = "How to maintain classroom discipline?"
    
    with initialized_pipeline.monitor_performance():
        result = await initialized_pipeline.process_query(query)
    
    metrics = initialized_pipeline.get_performance_metrics()
    assert 'query_time' in metrics
    assert 'embedding_time' in metrics
    assert 'response_time' in metrics 