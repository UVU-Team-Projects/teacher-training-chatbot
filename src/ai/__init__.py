try:
    from .simple_rag import SimpleRAG
    from .profile_builder import StudentProfileBuilder
    from .rag_pipeline import RAG, create_pipeline, chat_with_student
    from .student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
except ImportError:
    from src.ai.simple_rag import SimpleRAG
    from src.ai.profile_builder import StudentProfileBuilder
    from src.ai.rag_pipeline import RAG, create_pipeline, chat_with_student
    from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile

__all__ = [
    'SimpleRAG',
    'StudentProfileBuilder',
    'RAG',
    'create_pipeline',
    'chat_with_student',
    'create_student_profile',
    'Interest',
    'STUDENT_TEMPLATES',
    'StudentProfile',
]
