from sqlalchemy import create_engine, Column, Integer, String, ARRAY, Text, MetaData, inspect, ForeignKey, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import OperationalError

# Database Configuration
DATABASE_URL = "postgresql://teacher_chatbot_user:Bing_Bong19@localhost/teacher_chatbot_database"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = (UniqueConstraint('name'),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    traits = Column(ARRAY(String))
    strengths = Column(ARRAY(String), nullable=True)
    weaknesses = Column(ARRAY(String), nullable=True)
    motivations = Column(ARRAY(String), nullable=True)
    fears = Column(ARRAY(String), nullable=True)
    communication_style = Column(Text, nullable=True)
    engagement_level = Column(Integer, nullable=True)

class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (UniqueConstraint('title'),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)

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


# Check if the table exists and if its schema matches the model
inspector = inspect(engine)
for table_name in ["student_profiles", "scenarios", "dialogues", "active_files", "inactive_files"]:
    table_exists = inspector.has_table(table_name)
    if table_exists:
        table_columns = [c["name"] for c in inspector.get_columns(table_name)]
        model_columns = [c.name for c in Base.metadata.tables[table_name].columns]
        if table_columns!= model_columns:
            # Drop the table if the schema doesn't match
            try:
                Base.metadata.tables[table_name].drop(engine)
                print(f"{table_name} table dropped due to schema changes.")
            except OperationalError:
                print(f"Error dropping {table_name} table.")
    else:
        # Create the table if it doesn't exist
        metadata.create_all(bind=engine)
        print(f"{table_name} table created.")

# Create a Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()