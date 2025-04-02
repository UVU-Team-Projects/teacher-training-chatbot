"""
Performance monitoring module using Prometheus metrics.

This module provides functionality to track and measure various performance metrics
in the teacher training chatbot application, including:
- Embedding generation time
- RAG query processing time
- Model inference time
- Query counts
- Error counts by type

The metrics are exposed via a Prometheus HTTP server for collection and visualization.
"""

from prometheus_client import start_http_server, Summary, Counter
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Define metrics
EMBEDDING_TIME = Summary('embedding_generation_seconds', 
                        'Time spent generating embeddings')

RAG_QUERY_TIME = Summary('rag_query_seconds',
                        'Time spent processing RAG queries')

MODEL_INFERENCE_TIME = Summary('model_inference_seconds',
                             'Time spent on model inference')

QUERY_COUNT = Counter('queries_total',
                     'Total number of queries processed')

ERROR_COUNT = Counter('errors_total',
                     'Total number of errors',
                     ['type'])

def start_monitoring(port: int = 8000):
    """Start the monitoring server"""
    try:
        start_http_server(port)
        logger.info(f"Monitoring server started on port {port}")
    except Exception as e:
        logger.error(f"Error starting monitoring: {str(e)}")
        raise 