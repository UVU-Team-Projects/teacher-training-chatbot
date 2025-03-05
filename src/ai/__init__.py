try:
    from .simple_rag import SimpleRAG
    from .profile_builder import StudentProfileBuilder
    from .MultiAgent_pipeline import RAG, create_pipeline, create_multi_agent_pipeline
    from .student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from .scenario_generator import ScenarioGenerator
    from .embedding import EmbeddingGenerator
except ImportError:
    from src.ai.simple_rag import SimpleRAG
    from src.ai.profile_builder import StudentProfileBuilder
    from src.ai.MultiAgent_pipeline import RAG, create_pipeline, create_multi_agent_pipeline
    from src.ai.student_profiles import create_student_profile, Interest, STUDENT_TEMPLATES, StudentProfile
    from src.ai.scenario_generator import ScenarioGenerator
    from src.ai.embedding import EmbeddingGenerator


__all__ = [
    'SimpleRAG',
    'StudentProfileBuilder',
    'RAG',
    'create_pipeline',
    'create_multi_agent_pipeline',
    'create_student_profile',
    'Interest',
    'STUDENT_TEMPLATES',
    'StudentProfile',
    'ScenarioGenerator',
    'EmbeddingGenerator'
]
