# Component Testing Guide

## Prerequisites Setup

### 1. Environment Setup
```bash
# Create and activate conda environment
conda create -n teacher-bot python=3.9
conda activate teacher-bot

# Install core dependencies
conda install -c conda-forge pytorch transformers sentence-transformers pandas numpy pytest pytest-asyncio

# Install database dependencies
conda install -c conda-forge postgresql psycopg2 asyncpg

# Install monitoring dependencies
conda install -c conda-forge prometheus_client
```

## Testing Individual Components

### 1. Test Embedding Generation
```python
# tests/test_embedding.py
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

# Run tests
# pytest tests/test_embedding.py -v
```

### 2. Test Vector Storage
```python
# tests/test_vector_storage.py
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

@pytest.mark.asyncio
async def test_store_scenario(vector_ops):
    """Test storing scenario with embedding"""
    embedder = EmbeddingGenerator()
    scenario = {
        'name': 'Test Scenario',
        'description': 'Test description',
        'expected_response': 'Test response'
    }
    embedding = embedder.generate_embedding(scenario['expected_response'])
    
    scenario_id = await vector_ops.store_scenario(
        name=scenario['name'],
        description=scenario['description'],
        expected_response=scenario['expected_response'],
        embedding=embedding
    )
    
    assert scenario_id is not None
    assert isinstance(scenario_id, int)

@pytest.mark.asyncio
async def test_find_similar_scenarios(vector_ops):
    """Test finding similar scenarios"""
    query = "classroom management"
    query_embedding = EmbeddingGenerator().generate_embedding(query)
    
    results = await vector_ops.find_similar_scenarios(
        query_embedding=query_embedding,
        threshold=0.5,
        limit=5
    )
    
    assert isinstance(results, list)
    assert all('similarity' in r for r in results)

# Run tests
# pytest tests/test_vector_storage.py -v
```

### 3. Test RAG Pipeline
```python
# tests/test_rag_pipeline.py
import pytest
from ai.rag_pipeline import RAGPipeline
from ai.document_processor import DocumentProcessor

@pytest.fixture
def sample_documents():
    """Sample teaching documents"""
    return [{
        'content': 'Effective classroom management strategies include...',
        'source': 'Teaching Guide',
        'category': 'Classroom Management',
        'topic': 'Discipline'
    }]

@pytest.mark.asyncio
async def test_document_processing(sample_documents):
    """Test document processing"""
    processor = DocumentProcessor()
    processed_docs = processor.process_teaching_documents(sample_documents)
    
    assert len(processed_docs) > 0
    assert all('embedding' in doc for doc in processed_docs)
    assert all('metadata' in doc for doc in processed_docs)

@pytest.mark.asyncio
async def test_rag_query():
    """Test RAG query processing"""
    pipeline = RAGPipeline()
    query = "How to handle disruptive students?"
    
    result = await pipeline.process_query(query)
    
    assert 'response' in result
    assert 'sources' in result
    assert len(result['sources']) > 0

# Run tests
# pytest tests/test_rag_pipeline.py -v
```

### 4. Test Fine-tuning Pipeline
```python
# tests/test_fine_tuning.py
import pytest
from ai.dataset_preparation import DatasetPreparator
from ai.fine_tuning import ModelFineTuner
from ai.model_evaluation import ModelEvaluator

@pytest.fixture
def sample_scenarios():
    """Sample teaching scenarios"""
    return [{
        'name': 'Classroom Disruption',
        'description': 'Student interrupting lesson',
        'expected_response': 'Address behavior calmly...',
        'category': 'classroom_management'
    }]

def test_dataset_preparation(sample_scenarios):
    """Test dataset preparation"""
    preparator = DatasetPreparator()
    df = preparator.prepare_training_data(sample_scenarios)
    
    assert 'instruction' in df.columns
    assert 'response' in df.columns
    assert len(df) == len(sample_scenarios)
    assert preparator.validate_dataset(df)

@pytest.mark.slow
def test_model_fine_tuning():
    """Test model fine-tuning (small scale)"""
    fine_tuner = ModelFineTuner()
    fine_tuner.prepare_model()
    
    # Create small test dataset
    train_data = create_test_dataset()
    val_data = create_test_dataset()
    
    # Run training for 1 epoch
    fine_tuner.train(
        train_dataset=train_data,
        validation_dataset=val_data,
        output_dir="./test_model",
        num_epochs=1
    )
    
    assert os.path.exists("./test_model/pytorch_model.bin")

# Run tests
# pytest tests/test_fine_tuning.py -v
```

## Integration Testing

### 1. Test Complete Pipeline
```python
# tests/test_integration.py
import pytest
from ai.interaction_handler import InteractionHandler

@pytest.mark.asyncio
async def test_complete_interaction():
    """Test complete interaction flow"""
    handler = InteractionHandler()
    query = "How to handle a disruptive student?"
    
    result = await handler.handle_interaction(query)
    
    assert 'response' in result
    assert 'feedback' in result
    assert 'similarity' in result
    assert 'improvements' in result

@pytest.mark.asyncio
async def test_rag_with_fine_tuned_model():
    """Test RAG with fine-tuned model"""
    # Load fine-tuned model
    handler = InteractionHandler(model_path="./fine_tuned_model")
    
    # Test queries
    queries = [
        "How to engage students in online learning?",
        "What are effective classroom management techniques?",
        "How to handle student conflicts?"
    ]
    
    for query in queries:
        result = await handler.handle_interaction(query)
        assert result['response'] is not None
        assert len(result['improvements']) > 0

# Run integration tests
# pytest tests/test_integration.py -v
```

## Running Components in Development

### 1. Start Vector Database
```bash
# Start PostgreSQL with pgvector
docker run -d \
    --name vector-db \
    -e POSTGRES_PASSWORD=your_password \
    -e POSTGRES_DB=teacher_bot \
    -p 5432:5432 \
    ankane/pgvector
```

### 2. Initialize Database Schema
```bash
# Run database initialization script
python scripts/init_database.py
```

### 3. Start RAG Pipeline
```bash
# Run RAG service
python scripts/run_rag_service.py
```

### 4. Run Fine-tuning (Optional)
```bash
# Run fine-tuning pipeline
python scripts/run_fine_tuning.py \
    --train_data data/scenarios.json \
    --output_dir models/fine_tuned \
    --num_epochs 3
```

## Monitoring and Debugging

### 1. Monitor Performance
```python
# monitoring/performance_monitor.py
from prometheus_client import start_http_server, Summary, Counter

# Start metrics server
start_http_server(8000)

# Monitor component performance
EMBEDDING_TIME = Summary('embedding_generation_seconds', 
                        'Time spent generating embeddings')
RAG_QUERY_TIME = Summary('rag_query_seconds',
                        'Time spent processing RAG queries')
MODEL_INFERENCE_TIME = Summary('model_inference_seconds',
                             'Time spent on model inference')

# Access metrics at http://localhost:8000/metrics
```

### 2. Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python scripts/run_rag_service.py --debug

# View detailed logs
tail -f logs/debug.log
```

## Best Practices

1. **Component Testing**:
   - Test each component in isolation
   - Use appropriate fixtures and mocks
   - Test edge cases and error conditions
   - Monitor memory usage during tests

2. **Integration Testing**:
   - Start with simple integration tests
   - Gradually add more complex scenarios
   - Test error handling and recovery
   - Monitor system resources

3. **Performance Testing**:
   - Test with realistic data volumes
   - Monitor response times
   - Check memory usage
   - Test concurrent operations

4. **Debugging Tips**:
   - Use detailed logging
   - Monitor system metrics
   - Check component interactions
   - Validate data flow 