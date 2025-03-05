"""
Teacher Training Chatbot
A system for simulating student interactions for teacher training.
"""

__version__ = "0.1.0"

# Core components
try:
    from .ai.embedding import EmbeddingGenerator
    from .ai.rag_pipeline import RAG, create_pipeline, chat_with_student
    from .ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from .ai.profile_builder import StudentProfileBuilder
    from .ai.simple_rag import LlamaRAG
    from .app import load_css
except ImportError:
    from src.ai.embedding import EmbeddingGenerator
    from src.ai.rag_pipeline import RAG, create_pipeline, chat_with_student
    from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from src.ai.profile_builder import StudentProfileBuilder
    from src.ai.simple_rag import LlamaRAG
    from src.app import load_css

# Version information
__all__ = [
    'EmbeddingGenerator',
    'RAG',
    'create_pipeline',
    'chat_with_student',
    'create_student_profile',
    'Interest',
    'STUDENT_TEMPLATES',
    'StudentProfile',
    'LlamaRAG',
    'load_css',
    'StudentProfileBuilder',
]
