"""
Teacher Training Chatbot
A system for simulating student interactions for teacher training.
"""

__version__ = "0.1.0"

# Core components
try:
    from .ai.embedding import EmbeddingGenerator
    from .ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from .ai.profile_builder import StudentProfileBuilder
except ImportError:
    from src.ai.embedding import EmbeddingGenerator
    from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from src.ai.profile_builder import StudentProfileBuilder

# Version information
__all__ = [
    'EmbeddingGenerator',
    'create_student_profile',
    'Interest',
    'STUDENT_TEMPLATES',
    'StudentProfile',
    'StudentProfileBuilder',
]
