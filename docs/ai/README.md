# AI Developer Guide

## Overview
Guide for implementing and maintaining the AI components of UTAH-TTA.

## Key Resources
- [Development Guidelines](development_guidelines.md)
- [Model Training Protocols](training_protocols.md)
- [Performance Metrics](performance_metrics.md)

## Implementation Guides
1. RAG Pipeline Setup
2. Model Fine-tuning
3. Response Generation
4. Performance Monitoring

[Additional content...]

# AI Integration Documentation

## Overview

The AI component of the Teacher Training Chatbot uses Llama models for natural language processing and sentence transformers for semantic similarity calculations.

## Components

### 1. Language Model Integration

#### Llama Model Setup
```python
from llama_cpp import Llama

# Initialize Llama model
llm = Llama(
    model_path="models/llama-2-7b-chat.gguf",  # Path to your GGUF model file
    n_ctx=2048,            # Context window
    n_threads=4,           # Number of CPU threads to use
    n_gpu_layers=0         # Number of layers to offload to GPU (if available)
)

def get_completion(prompt):
    response = llm(
        prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["</s>"],     # Llama's end of sequence token
        echo=False
    )
    return response['choices'][0]['text']
```

#### Prompt Engineering
```python
def generate_student_query(scenario, personality, tone):
    prompt = f"""<s>[INST]You are simulating an elementary school student.
    Scenario: {scenario}
    Personality: {personality}
    Emotional Tone: {tone}
    Generate a realistic question as the student.[/INST]"""
    return get_completion(prompt)
```

### 2. Semantic Similarity

#### Sentence Transformer Setup
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(text1, text2):
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(embedding1, embedding2)[0][0])
```

### 3. Response Generation

#### Student Query Generation
```python
def generate_student_query(scenario, personality, tone):
    prompt = f"""<s>[INST]Generate a student question with these characteristics:
    - Scenario: {scenario}
    - Student Personality: {personality}
    - Emotional Tone: {tone}
    
    Respond with just the question, no additional text.[/INST]"""
    return get_completion(prompt)
```

#### Response Evaluation
```python
def evaluate_response(teacher_response, expected_response):
    similarity = calculate_similarity(teacher_response, expected_response)
    feedback = generate_feedback(similarity, teacher_response, expected_response)
    return similarity, feedback
```

## Implementation Guidelines

### 1. Model Setup

#### Model Download
```bash
# Download Llama model in GGUF format
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O models/llama-2-7b-chat.gguf
```

#### Environment Setup
```bash
# Install required packages
pip install llama-cpp-python
pip install sentence-transformers
```

### 2. Error Handling

```python
def safe_completion(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return get_completion(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embedding(text):
    return model.encode(text, convert_to_tensor=True)
```

## Best Practices

### 1. Prompt Engineering for Llama

- Use Llama's instruction format: `<s>[INST]...[/INST]`
- Keep instructions clear and concise
- Include relevant context
- Handle edge cases
- Validate outputs

### 2. Model Selection

- Llama 2 7B for general responses
- Sentence transformers for embeddings
- Consider hardware requirements
- Monitor memory usage

### 3. Performance Optimization

- Use quantized models (GGUF format)
- Batch processing when possible
- Response caching
- Embedding precomputation
- GPU acceleration when available

## Security Considerations

### 1. Input Validation

```python
def sanitize_input(text):
    # Remove potentially harmful content
    return clean_text(text)
```

### 2. Output Filtering

```python
def filter_response(response):
    # Ensure response meets guidelines
    return validate_content(response)
```

### 3. Model Security

- Secure model file storage
- Regular model updates
- Access control
- Input/output monitoring

## Monitoring and Logging

### 1. Performance Metrics

```python
def log_completion_metrics(start_time, end_time, tokens):
    duration = end_time - start_time
    log_metric("completion_duration", duration)
    log_metric("tokens_used", tokens)
```

### 2. Error Tracking

```python
def log_ai_error(error, context):
    logger.error(f"AI Error: {error}", extra={
        "context": context,
        "timestamp": datetime.utcnow()
    })
```

## Testing

### 1. Unit Tests

```python
def test_response_generation():
    response = generate_student_query(
        scenario="Math problem",
        personality="Curious",
        tone="Confused"
    )
    assert len(response) > 0
```

### 2. Integration Tests

```python
def test_end_to_end_interaction():
    query = generate_student_query(scenario)
    response = get_teacher_response(query)
    similarity = evaluate_response(response)
    assert similarity > 0.5
```

## Model Management

### 1. Environment Setup

```bash
export MODEL_PATH="models/llama-2-7b-chat.gguf"
export MODEL_CACHE_DIR="/path/to/cache"
```

### 2. Model Loading

```python
def load_models():
    global llm, embedding_model
    llm = Llama(model_path=os.getenv('MODEL_PATH'))
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

## Troubleshooting

### Common Issues

1. Memory Management
   - Monitor RAM usage
   - Use appropriate model size
   - Implement proper cleanup

2. Performance Issues
   - Use quantized models
   - Enable GPU acceleration
   - Optimize batch size

3. Response Quality
   - Adjust temperature
   - Refine prompts
   - Implement better validation

### Solutions

1. Memory Issues
   - Use smaller models
   - Implement garbage collection
   - Monitor memory usage

2. Speed Issues
   - Enable GPU layers
   - Use caching
   - Optimize context window 