import pytest
import asyncio
from ai.interaction_handler import InteractionHandler
from database.vector_ops import VectorOperations
from ai.embedding import EmbeddingGenerator

@pytest.fixture
async def setup_environment():
    """Setup test environment with sample data"""
    vector_ops = VectorOperations()
    await vector_ops.initialize()
    
    # Add sample scenarios
    scenarios = [
        {
            'name': 'Classroom Disruption',
            'description': 'Student repeatedly interrupts class discussion',
            'expected_response': 'Address the behavior privately, establish clear expectations, and implement consistent consequences.'
        },
        {
            'name': 'Student Engagement',
            'description': 'Students show low engagement in online learning',
            'expected_response': 'Implement interactive activities, use multimedia resources, and encourage active participation.'
        }
    ]
    
    embedder = EmbeddingGenerator()
    for scenario in scenarios:
        embedding = embedder.generate_embedding(scenario['expected_response'])
        await vector_ops.store_scenario(
            name=scenario['name'],
            description=scenario['description'],
            expected_response=scenario['expected_response'],
            embedding=embedding
        )
    
    return vector_ops

@pytest.mark.asyncio
async def test_complete_interaction(setup_environment):
    """Test complete interaction flow"""
    handler = InteractionHandler()
    query = "How to handle a disruptive student?"
    
    result = await handler.handle_interaction(query)
    
    # Check response structure
    assert 'response' in result
    assert 'feedback' in result
    assert 'similarity' in result
    assert 'improvements' in result
    
    # Check response content
    assert isinstance(result['response'], str)
    assert len(result['response']) > 0
    assert isinstance(result['similarity'], float)
    assert 0 <= result['similarity'] <= 1
    assert isinstance(result['improvements'], list)

@pytest.mark.asyncio
async def test_rag_with_fine_tuned_model():
    """Test RAG with fine-tuned model"""
    handler = InteractionHandler(model_path="./fine_tuned_model")
    
    # Test multiple queries
    queries = [
        "How to engage students in online learning?",
        "What are effective classroom management techniques?",
        "How to handle student conflicts?"
    ]
    
    for query in queries:
        result = await handler.handle_interaction(query)
        assert result['response'] is not None
        assert len(result['improvements']) > 0
        assert 0 <= result['similarity'] <= 1

@pytest.mark.asyncio
async def test_feedback_generation(setup_environment):
    """Test feedback generation for teacher responses"""
    handler = InteractionHandler()
    
    # Test scenario
    query = "How to maintain classroom discipline?"
    teacher_response = "I would immediately punish disruptive students."
    
    result = await handler.handle_interaction(
        query=query,
        teacher_response=teacher_response
    )
    
    # Check feedback
    assert result['feedback'] is not None
    assert result['similarity'] < 0.7  # Response should be flagged as needing improvement
    assert len(result['improvements']) > 0
    assert any('positive' in imp.lower() for imp in result['improvements'])

@pytest.mark.asyncio
async def test_concurrent_processing():
    """Test handling multiple concurrent interactions"""
    handler = InteractionHandler()
    
    # Multiple concurrent queries
    queries = [
        "How to engage students?",
        "How to handle disruptions?",
        "How to provide feedback?",
        "How to manage time effectively?"
    ]
    
    # Process queries concurrently
    tasks = [handler.handle_interaction(query) for query in queries]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(queries)
    assert all('response' in r for r in results)
    assert all('feedback' in r for r in results)

@pytest.mark.asyncio
async def test_error_recovery():
    """Test system recovery from errors"""
    handler = InteractionHandler()
    
    # Test with invalid input
    with pytest.raises(ValueError):
        await handler.handle_interaction("")
    
    # System should still work after error
    result = await handler.handle_interaction("How to engage students?")
    assert result['response'] is not None
    
    # Test with very long input
    long_query = "How to" + " very" * 1000 + " long query"
    result = await handler.handle_interaction(long_query)
    assert result['response'] is not None

@pytest.mark.asyncio
async def test_performance_requirements():
    """Test performance requirements"""
    handler = InteractionHandler()
    query = "How to improve student engagement?"
    
    # Measure response time
    import time
    start_time = time.time()
    result = await handler.handle_interaction(query)
    duration = time.time() - start_time
    
    # Response should be generated within 5 seconds
    assert duration < 5.0
    assert result['response'] is not None

@pytest.mark.asyncio
async def test_system_state_persistence(setup_environment):
    """Test system state persistence across interactions"""
    handler = InteractionHandler()
    
    # First interaction
    query1 = "How to handle classroom disruption?"
    result1 = await handler.handle_interaction(query1)
    
    # Second interaction referencing first
    query2 = "Can you elaborate on the previous response?"
    result2 = await handler.handle_interaction(query2)
    
    assert result2['response'] is not None
    assert result2['response'] != result1['response']
    
    # Check context awareness
    assert any(word in result2['response'].lower() 
              for word in ['previous', 'mentioned', 'discussed']) 