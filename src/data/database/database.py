from sqlalchemy import create_engine, Column, Integer, String, ARRAY, Text, MetaData, inspect, ForeignKey, LargeBinary, text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import OperationalError

# Database Configuration
DATABASE_URL = "postgresql://teacher_chatbot_user:team4ai@localhost/teacher_chatbot_database"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


        # initial_state = {
        #     "messages": [HumanMessage(content=query)],
        #     "context": "",
        #     "student_profile": {
        #         "name": student.name,
        #         "grade_level": student.grade_level,
        #         "personality_traits": student.personality_traits,
        #         "typical_moods": student.typical_moods,
        #         "behavioral_patterns": student.behavioral_patterns,
        #         "learning_style": student.learning_style,
        #         "interests": student.interests,
        #         "academic_strengths": student.academic_strengths,
        #         "academic_challenges": student.academic_challenges,
        #         "support_strategies": student.support_strategies,
        #         "social_dynamics": student.social_dynamics
        #     }
        # }

#         {{
#     "name": "Sarah",
#     "grade_level": 2,
#     "personality_traits": ["bright", "anxious", "hesitant"],
#     "learning_style": "visual",
#     "interests": ["science", "nature", "math"],
#     "typical_moods": ["focused", "tired", "distracted"],
#     "behavioral_patterns": {{
#         "morning": "focused and attentive",
#         "afternoon": "becomes tired and distracted",
#         "during_group_work": "works well in small groups",
#         "during_independent_work": "can maintain focus but may need support",
#         "transitions": "handles smoothly with structure"
#     }},
#     "academic_strengths": ["math", "science experiments"],
#     "academic_challenges": ["writing long passages", "speaking in large groups"],
#     "social_dynamics": {{
#         "peer_interactions": "comfortable in small groups",
#         "group_work": "participates well in small settings",
#         "teacher_interaction": "may need encouragement to speak up"
#     }},
#     "support_strategies": ["visual aids", "positive reinforcement", "small group settings"]
# }}

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = (UniqueConstraint('name'),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grade_level = Column(Integer)
    personality_traits = Column(ARRAY(String), nullable=True)
    typical_moods = Column(ARRAY(String), nullable=True)
    behavioral_patterns = Column(JSON, nullable=True)
    learning_style = Column(String, nullable=True)
    interests = Column(ARRAY(String), nullable=True)
    academic_strengths = Column(ARRAY(String), nullable=True)
    academic_challenges = Column(ARRAY(String), nullable=True)
    support_strategies = Column(ARRAY(String), nullable=True)
    social_dynamics = Column(JSON, nullable=True)

class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grade_level = Column(Integer)
    teaching_philosophy = Column(Text)
    preferred_teaching_methods = Column(ARRAY(String), nullable=True)
    behavior_management_philosophy = Column(Text, nullable=True)
    areas_for_growth = Column(ARRAY(String), nullable=True)

class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (UniqueConstraint('title'),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    instruction = Column(Text, nullable=True)  # AI instruction/prompt for role-playing the scenario
    # The instruction field will contain structured guidance for the AI, including:
    # - Role-playing context
    # - Emotional state and background
    # - Key points to emphasize
    # - How to respond to teacher interactions
    # - Any specific triggers or sensitive topics to handle carefully

    dialogues = relationship("Dialogue", back_populates="scenario")

class Dialogue(Base):
    __tablename__ = "dialogues"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    student_name = Column(String, ForeignKey("student_profiles.name"))
    utterance = Column(Text)

    scenario = relationship("Scenario", back_populates="dialogues")
    student = relationship("StudentProfile", back_populates="dialogues")

StudentProfile.dialogues = relationship("Dialogue", back_populates="student")

class ActiveFile(Base):
    __tablename__ = "active_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)  # Store the file content as binary data

class InactiveFile(Base):
    __tablename__ = "inactive_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)  # Store the file content as binary data

def generate_tables():
    """
    Generates or updates all database tables based on the SQLAlchemy models.
    This function checks if tables exist and creates/updates them as needed.
    """
    inspector = inspect(engine)
    tables_to_check = ["student_profiles", "teacher_profiles", "scenarios", "dialogues", "active_files", "inactive_files"]
    
    for table_name in tables_to_check:
        table_exists = inspector.has_table(table_name)
        if table_exists:
            # Get the actual table columns from the database
            table_columns = [c["name"] for c in inspector.get_columns(table_name)]
            # Get the model columns from our SQLAlchemy model
            model_columns = [c.name for c in Base.metadata.tables[table_name].columns]

            # Sort the lists before comparing
            table_columns.sort()
            model_columns.sort()

            # Only drop and recreate if there's an actual difference in columns
            if table_columns != model_columns:
                print(f"Schema mismatch detected for {table_name}:")
                print(f"  Database columns: {table_columns}")
                print(f"  Model columns: {model_columns}")
                
                # Drop the table using a raw SQL statement
                try:
                    with engine.begin() as conn:  # This automatically handles transaction commit
                        # First, drop any foreign key constraints
                        conn.execute(text(f"ALTER TABLE IF EXISTS {table_name} DROP CONSTRAINT IF EXISTS {table_name}_pkey CASCADE;"))
                        # Then drop the table
                        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                    print(f"{table_name} table dropped due to schema changes.")

                    # Recreate the table with the new schema
                    Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[table_name]])
                    print(f"{table_name} table created with new schema.")
                except OperationalError as e:
                    print(f"Error dropping or creating {table_name} table: {str(e)}")
            else:
                print(f"{table_name} table exists with correct schema.")
        else:
            # Create the table if it doesn't exist
            try:
                Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[table_name]])
                print(f"{table_name} table created.")
            except OperationalError as e:
                print(f"Error creating {table_name} table: {str(e)}")

# Create a Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Only run table generation if this file is run directly
    generate_tables()


