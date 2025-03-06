import pytest
import asyncio
from database.vector_ops import VectorOperations
from ai.embedding import EmbeddingGenerator

@pytest.fixture
async def vector_ops():
    """Setup vector operations"""
    ops = VectorOperations()
    await ops.initialize()
    return ops

@pytest.fixture
def sample_scenario():
    """Sample teaching scenario"""
    return {
        'name': 'Test Scenario',
        'description': 'Student repeatedly interrupts class discussion',
        'expected_response': 'Address the behavior privately with the student, establish clear expectations, and implement consistent consequences.'
    }

@pytest.mark.asyncio
async def test_store_scenario(vector_ops, sample_scenario):
    """Test storing scenario with embedding"""
    embedder = EmbeddingGenerator()
    embedding = embedder.generate_embedding(sample_scenario['expected_response'])
    
    scenario_id = await vector_ops.store_scenario(
        name=sample_scenario['name'],
        description=sample_scenario['description'],
        expected_response=sample_scenario['expected_response'],
        embedding=embedding
    )
    
    assert scenario_id is not None
    assert isinstance(scenario_id, int)
    return scenario_id

@pytest.mark.asyncio
async def test_find_similar_scenarios(vector_ops, sample_scenario):
    """Test finding similar scenarios"""
    # First store a scenario
    scenario_id = await test_store_scenario(vector_ops, sample_scenario)
    
    # Then search for similar scenarios
    query = "How to handle student interruptions?"
    query_embedding = EmbeddingGenerator().generate_embedding(query)
    
    results = await vector_ops.find_similar_scenarios(
        query_embedding=query_embedding,
        threshold=0.5,
        limit=5
    )
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert all('similarity' in r for r in results)
    assert all('id' in r for r in results)
    assert any(r['id'] == scenario_id for r in results)

@pytest.mark.asyncio
async def test_batch_store_scenarios(vector_ops):
    """Test storing multiple scenarios in batch"""
    embedder = EmbeddingGenerator()
    scenarios = [
        {
            'name': 'Scenario 1',
            'description': 'Student disruption',
            'expected_response': 'Address calmly',
            'embedding': embedder.generate_embedding('Address calmly')
        },
        {
            'name': 'Scenario 2',
            'description': 'Student engagement',
            'expected_response': 'Use interactive methods',
            'embedding': embedder.generate_embedding('Use interactive methods')
        }
    ]
    
    scenario_ids = await vector_ops.batch_store_scenarios(scenarios)
    assert len(scenario_ids) == len(scenarios)
    assert all(isinstance(id_, int) for id_ in scenario_ids)

@pytest.mark.asyncio
async def test_update_scenario(vector_ops, sample_scenario):
    """Test updating an existing scenario"""
    # First store a scenario
    scenario_id = await test_store_scenario(vector_ops, sample_scenario)
    
    # Update the scenario
    updated_response = "Updated response for the scenario"
    updated_embedding = EmbeddingGenerator().generate_embedding(updated_response)
    
    success = await vector_ops.update_scenario(
        scenario_id=scenario_id,
        expected_response=updated_response,
        embedding=updated_embedding
    )
    
    assert success
    
    # Verify update
    results = await vector_ops.find_similar_scenarios(
        query_embedding=updated_embedding,
        threshold=0.9,
        limit=1
    )
    assert len(results) == 1
    assert results[0]['id'] == scenario_id
    assert results[0]['expected_response'] == updated_response

@pytest.mark.asyncio
async def test_delete_scenario(vector_ops, sample_scenario):
    """Test deleting a scenario"""
    # First store a scenario
    scenario_id = await test_store_scenario(vector_ops, sample_scenario)
    
    # Delete the scenario
    success = await vector_ops.delete_scenario(scenario_id)
    assert success
    
    # Verify deletion
    query_embedding = EmbeddingGenerator().generate_embedding(sample_scenario['expected_response'])
    results = await vector_ops.find_similar_scenarios(
        query_embedding=query_embedding,
        threshold=0.9,
        limit=1
    )
    assert len(results) == 0

@pytest.mark.asyncio
async def test_error_handling(vector_ops):
    """Test error handling for invalid operations"""
    with pytest.raises(ValueError):
        await vector_ops.store_scenario(
            name="",  # Empty name should raise error
            description="Test",
            expected_response="Test",
            embedding=[0.0] * 384
        )
    
    with pytest.raises(ValueError):
        await vector_ops.find_similar_scenarios(
            query_embedding=[0.0] * 383,  # Wrong dimension
            threshold=0.5,
            limit=5
        ) 