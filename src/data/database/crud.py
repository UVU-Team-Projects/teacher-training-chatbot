from database import StudentProfile, get_db, Scenario, Dialogue, ActiveFile, InactiveFile, TeacherProfile
from sqlalchemy.exc import IntegrityError
from typing import List, Union, Optional
import os
import json

    # id = Column(Integer, primary_key=True, index=True)
    # name = Column(String, index=True)
    # grade_level = Column(Integer)
    # personality_traits = Column(ARRAY(String), nullable=True)
    # typical_moods = Column(ARRAY(String), nullable=True)
    # behavioral_patterns = Column(String, nullable=True)
    # learning_style = Column(String, nullable=True)
    # interests = Column(ARRAY(String), nullable=True)
    # academic_strengths = Column(ARRAY(String), nullable=True)
    # academic_challenges = Column(ARRAY(String), nullable=True)
    # support_strategies = Column(ARRAY(String), nullable=True)
    # social_dynamics = Column(String, nullable=True)

def print_student_profiles():
    """
    Prints the contents of the student_profiles table.
    """
    db = next(get_db())
    students = db.query(StudentProfile).all()
    print("\nstudent_profiles table contents:")
    for student in students:
        print(f"  ID: {student.id}")
        print(f"  Name: {student.name}")
        print(f"  Grade Level: {student.grade_level}")
        print(f"  Personality Traits: {', '.join(student.personality_traits) if student.personality_traits else 'None'}")
        print(f"  Typical Moods: {', '.join(student.typical_moods) if student.typical_moods else 'None'}")
        # Format behavioral patterns as a clean JSON string
        if student.behavioral_patterns:
            if isinstance(student.behavioral_patterns, str):
                print(f"  Behavioral Patterns: {student.behavioral_patterns}")
            else:
                print(f"  Behavioral Patterns: {json.dumps(student.behavioral_patterns)}")
        else:
            print("  Behavioral Patterns: None")
        print(f"  Learning Style: {student.learning_style}")
        print(f"  Interests: {', '.join(student.interests) if student.interests else 'None'}")
        print(f"  Academic Strengths: {', '.join(student.academic_strengths) if student.academic_strengths else 'None'}")
        print(f"  Academic Challenges: {', '.join(student.academic_challenges) if student.academic_challenges else 'None'}")
        print(f"  Support Strategies: {', '.join(student.support_strategies) if student.support_strategies else 'None'}")
        # Format social dynamics as a clean JSON string
        if student.social_dynamics:
            if isinstance(student.social_dynamics, str):
                print(f"  Social Dynamics: {student.social_dynamics}")
            else:
                print(f"  Social Dynamics: {json.dumps(student.social_dynamics)}")
        else:
            print("  Social Dynamics: None")
        print("-" * 20)  # Separator between students

def print_teacher_profiles():
    """
    Prints all teacher profiles in a formatted table.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).all()
        if not teachers:
            print("\nNo teacher profiles found.")
            return

        print("\n=== Teacher Profiles ===")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Grade Level':<12} {'Teaching Philosophy':<40}")
        print("-" * 80)

        for teacher in teachers:
            # Truncate teaching philosophy if too long
            philosophy = teacher.teaching_philosophy[:37] + "..." if len(teacher.teaching_philosophy) > 40 else teacher.teaching_philosophy
            print(f"{teacher.id:<5} {teacher.name:<20} {teacher.grade_level:<12} {philosophy:<40}")

        print("-" * 80)
        print(f"Total Teachers: {len(teachers)}")
        print("-" * 80)

        # Print detailed information for each teacher
        print("\nDetailed Teacher Information:")
        print("=" * 80)
        for teacher in teachers:
            print(f"\nTeacher: {teacher.name} (ID: {teacher.id})")
            print(f"Grade Level: {teacher.grade_level}")
            print(f"Teaching Philosophy: {teacher.teaching_philosophy}")
            if teacher.preferred_teaching_methods:
                print(f"Preferred Teaching Methods: {', '.join(teacher.preferred_teaching_methods)}")
            if teacher.behavior_management_philosophy:
                print(f"Behavior Management Philosophy: {teacher.behavior_management_philosophy}")
            if teacher.areas_for_growth:
                print(f"Areas for Growth: {', '.join(teacher.areas_for_growth)}")
            print("-" * 40)

    except Exception as e:
        print(f"Error printing teacher profiles: {e}")
        return

def print_scenarios():
    """
    Prints the contents of the scenarios table.
    """
    db = next(get_db())
    scenarios = db.query(Scenario).all()
    print("\nscenarios table contents:")
    for scenario in scenarios:
        print(f"  ID: {scenario.id}")
        print(f"  Title: {scenario.title}")
        print(f"  Description: {scenario.description}")
        print(f"  Instruction: {scenario.instruction}")
        print("-" * 20)  # Separator between scenarios

def print_dialogues():
    """
    Prints the contents of the dialogues table.
    """
    db = next(get_db())
    dialogues = db.query(Dialogue).all()
    print("\ndialogues table contents:")
    for dialogue in dialogues:
        print(f"  ID: {dialogue.id}")
        print(f"  Scenario ID: {dialogue.scenario_id}")
        print(f"  Student Name: {dialogue.student_name}")
        print(f"  Utterance: {dialogue.utterance}")
        print("-" * 20)  # Separator between dialogues

def print_active_files():
    """
    Prints the contents of the active_files table.
    """
    db = next(get_db())
    active_files = db.query(ActiveFile).all()
    print("\nactive_files table contents:")
    for file in active_files:
        print(f"ID: {file.id}, Name: {file.name}")  # Print only ID and name

def print_inactive_files():
    """
    Prints the contents of the inactive_files table.
    """
    db = next(get_db())
    inactive_files = db.query(InactiveFile).all()
    print("\ninactive_files table contents:")
    for file in inactive_files:
        print(f"ID: {file.id}, Name: {file.name}")  # Print only ID and name

def print_table_contents(table_name: str):
    """
    Prints the contents of the specified table.

    Args:
        table_name (str): The name of the table to print.
    """
    if table_name == "student_profiles":
        print_student_profiles()
    elif table_name == "teacher_profiles":
        print_teacher_profiles()
    elif table_name == "scenarios":
        print_scenarios()
    elif table_name == "dialogues":
        print_dialogues()
    elif table_name == "active_files":
        print_active_files()
    elif table_name == "inactive_files":
        print_inactive_files()
    else:
        print(f"\nInvalid table name: {table_name}")

# Student CRUD Functions

def get_student_by_id(id: int) -> StudentProfile:
    """
    Retrieves a student profile from the database by their id.

    Args:
        id (int): Id of the student to retrieve.

    Returns:
        StudentProfile: The StudentProfile object if found, None otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    return student


def get_student_by_name(name: str) -> StudentProfile:
    """
    Retrieves a student profile from the database by their name.

    Args:
        name (str): The name of the student to retrieve.

    Returns:
        StudentProfile: The StudentProfile object if found, None otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfile).filter(StudentProfile.name == name).first()
    return student

def get_all_students() -> List[StudentProfile]:
    """
    Retrieves all student profiles from the database.

    Returns:
        list: A list of StudentProfile objects.
    """
    db = next(get_db())
    students = db.query(StudentProfile).all()
    return students

def create_student(
    name: str, 
    grade_level: int, 
    personality_traits: list = None, 
    typical_moods: list = None, 
    behavioral_patterns: dict = None, 
    learning_style: str = None, 
    interests: list = None, 
    academic_strengths: list = None, 
    academic_challenges: list = None, 
    support_strategies: list = None, 
    social_dynamics: dict = None
) -> StudentProfile:
    """
    Creates a new student profile in the database.

    Args:
        name (str): The name of the student.
        grade_level (int): The grade level of the student.
        personality_traits (list, optional): A list of personality traits. Defaults to None.
        typical_moods (list, optional): A list of typical moods. Defaults to None.
        behavioral_patterns (dict, optional): A dictionary of behavioral patterns. Defaults to None.
        learning_style (str, optional): The student's learning style. Defaults to None.
        interests (list, optional): A list of interests. Defaults to None.
        academic_strengths (list, optional): A list of academic strengths. Defaults to None.
        academic_challenges (list, optional): A list of academic challenges. Defaults to None.
        support_strategies (list, optional): A list of support strategies. Defaults to None.
        social_dynamics (dict, optional): A dictionary of social dynamics. Defaults to None.

    Returns:
        StudentProfile: The created StudentProfile object, or None if creation failed.
    """
    db = next(get_db())
    try:
        student = StudentProfile(
            name=name,
            grade_level=grade_level,
            personality_traits=personality_traits,
            typical_moods=typical_moods,
            behavioral_patterns=behavioral_patterns,
            learning_style=learning_style,
            interests=interests,
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            support_strategies=support_strategies,
            social_dynamics=social_dynamics
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except IntegrityError:
        db.rollback()
        return None

def update_student(student_id: int, **kwargs) -> StudentProfile:
    """
    Updates an existing student profile in the database.

    Args:
        student_id (int): The ID of the student to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.

    Returns:
        StudentProfile: The updated StudentProfile object, or None if the update failed.
    """
    db = next(get_db())
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if student:
        for key, value in kwargs.items():
            setattr(student, key, value)
        db.commit()
        return student
    return None

def delete_student_by_id(student_id: int) -> bool:
    """
    Deletes a student profile from the database.

    Args:
        student_id (int): The ID of the student to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

def delete_student_by_name(student_name: str) -> bool:
    """
    Deletes a student profile from the database.

    Args:
        student_name (str): The name of the student to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfile).filter(StudentProfile.name == student_name).first()
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

def clear_student_profiles() -> bool:
    """
    Clears all records from the student_profiles table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(StudentProfile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing student profiles: {e}")
        return False

# Scenario CRUD Functions

def get_scenario_by_title(title: str) -> Scenario:
    """
    Retrieves a scenario from the database by its title.

    Args:
        title (str): The title of the scenario to retrieve.

    Returns:
        Scenario: The Scenario object if found, None otherwise.
    """
    db = next(get_db())
    scenario = db.query(Scenario).filter(Scenario.title == title).first()
    return scenario

def get_all_scenarios() -> List[Scenario]:
    """
    Retrieves all scenarios from the database.

    Returns:
        list: A list of Scenario objects.
    """
    db = next(get_db())
    scenarios = db.query(Scenario).all()
    return scenarios

def create_scenario(title: str, description: str, instruction: str = None) -> Scenario:
    """
    Creates a new scenario in the database.

    Args:
        title (str): The title of the scenario.
        description (str): The description of the scenario.
        instruction (str, optional): The AI instruction/prompt for role-playing the scenario.

    Returns:
        Scenario: The created Scenario object, or None if creation failed.
    """
    db = next(get_db())
    try:
        scenario = Scenario(title=title, description=description, instruction=instruction)
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario
    except Exception as e:
        db.rollback()
        print(f"Error creating scenario: {e}")
        return None

def update_scenario(scenario_id: int, **kwargs) -> Scenario:
    """
    Updates an existing scenario in the database.

    Args:
        scenario_id (int): The ID of the scenario to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.
                 Can include: title, description, instruction.

    Returns:
        Scenario: The updated Scenario object, or None if the update failed.
    """
    db = next(get_db())
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario:
        valid_fields = {'title', 'description', 'instruction'}
        for key, value in kwargs.items():
            if key in valid_fields:
                setattr(scenario, key, value)
            else:
                print(f"Warning: Invalid field '{key}' for scenario update")
        db.commit()
        return scenario
    return None

def delete_scenario(scenario_id: int) -> bool:
    """
    Deletes a scenario from the database.

    Args:
        scenario_id (int): The ID of the scenario to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if scenario:
            db.delete(scenario)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting scenario: {e}")
        return False

def clear_scenarios() -> bool:
    """
    Clears all records from the scenarios table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(Scenario).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing scenarios: {e}")
        return False

# Dialogue CRUD functions

def get_dialogue_by_id(dialogue_id: int) -> Dialogue:
    """
    Retrieves a dialogue from the database by its ID.

    Args:
        dialogue_id (int): The ID of the dialogue to retrieve.

    Returns:
        Dialogue: The Dialogue object if found, None otherwise.
    """
    db = next(get_db())
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    return dialogue

def get_dialogues_by_scenario(scenario_id: int) -> List[Dialogue]:
    """
    Retrieves all dialogues for a given scenario ID.

    Args:
        scenario_id (int): The ID of the scenario.

    Returns:
        list: A list of Dialogue objects associated with the scenario.
    """
    db = next(get_db())
    dialogues = db.query(Dialogue).filter(Dialogue.scenario_id == scenario_id).all()
    return dialogues

def create_dialogue(scenario_id: int, student_name: str, utterance: str) -> Dialogue:
    """
    Creates a new dialogue in the database.

    Args:
        scenario_id (int): The ID of the scenario this dialogue belongs to.
        student_name (str): The name of the student speaking.
        utterance (str): The actual dialogue utterance.

    Returns:
        Dialogue: The created Dialogue object, or None if creation failed.
    """
    db = next(get_db())
    try:
        dialogue = Dialogue(scenario_id=scenario_id, student_name=student_name, utterance=utterance)
        db.add(dialogue)
        db.commit()
        db.refresh(dialogue)
        return dialogue
    except Exception as e:
        db.rollback()
        print(f"Error creating dialogue: {e}")
        return None

def update_dialogue(dialogue_id: int, **kwargs) -> Dialogue:
    """
    Updates an existing dialogue in the database.

    Args:
        dialogue_id (int): The ID of the dialogue to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.

    Returns:
        Dialogue: The updated Dialogue object, or None if the update failed.
    """
    db = next(get_db())
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if dialogue:
        for key, value in kwargs.items():
            setattr(dialogue, key, value)
        db.commit()
        return dialogue
    return None

def delete_dialogue(dialogue_id: int) -> bool:
    """
    Deletes a dialogue from the database.

    Args:
        dialogue_id (int): The ID of the dialogue to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
        if dialogue:
            db.delete(dialogue)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting dialogue: {e}")
        return False
    
def get_dialogues_by_student_and_scenario(student_name: str, scenario_title: str) -> List[Dialogue]:
    """
    Retrieves dialogues for a specific student in a specific scenario.

    Args:
        student_name (str): The name of the student.
        scenario_title (str): The title of the scenario.

    Returns:
        list: A list of Dialogue objects matching the criteria.
    """
    db = next(get_db())
    dialogues = db.query(Dialogue).join(Scenario).filter(
        Dialogue.student_name == student_name,
        Scenario.title == scenario_title
    ).all()
    return dialogues

def clear_dialogues() -> bool:
    """
    Clears all records from the dialogues table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(Dialogue).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing dialogues: {e}")
        return False

# Active and Inactive Tables CRUD functions

def create_active_file(name: str, file_content: bytes) -> ActiveFile:
    """
    Creates a new active file entry in the database.

    Args:
        name (str): The name of the file.
        file_content (bytes): The content of the file as bytes.

    Returns:
        The created ActiveFile object, or None if creation failed.
    """
    db = next(get_db())
    try:
        active_file = ActiveFile(name=name, file_content=file_content)
        db.add(active_file)
        db.commit()
        print(f"File added to database: {name}")
        db.refresh(active_file)
        return active_file
    except Exception as e:
        db.rollback()
        print(f"Error creating active file: {e}")
        return None

def get_active_file_by_id(active_file_id: int) -> ActiveFile:
    """
    Retrieves an active file from the database by its ID.

    Args:
        active_file_id (int): The ID of the active file.

    Returns:
        The ActiveFile object if found, None otherwise.
    """
    db = next(get_db())
    active_file = db.query(ActiveFile).filter(ActiveFile.id == active_file_id).first()
    return active_file

def get_inactive_file_by_id(inactive_file_id: int) -> InactiveFile:
    """
    Retrieves an inactive file from the database by its ID.

    Args:
        inactive_file_id (int): The ID of the inactive file.

    Returns:
        The InactiveFile object if found, None otherwise.
    """
    db = next(get_db())
    inactive_file = db.query(InactiveFile).filter(InactiveFile.id == inactive_file_id).first()
    return inactive_file

def get_active_file_by_name(active_file_name: str) -> ActiveFile:
    """
    Retrieves an active file from the database by its name.

    Args:
        active_file_name (str): The name of the active file.

    Returns:
        The ActiveFile object if found, None otherwise.
    """
    db = next(get_db())
    active_file = db.query(ActiveFile).filter(ActiveFile.name == active_file_name).first()
    return active_file

def get_inactive_file_by_name(inactive_file_name: str) -> InactiveFile:
    """
    Retrieves an inactive file from the database by its name.

    Args:
        inactive_file_name (str): The name of the inactive file.

    Returns:
        The InactiveFile object if found, None otherwise.
    """
    db = next(get_db())
    inactive_file = db.query(InactiveFile).filter(InactiveFile.name == inactive_file_name).first()
    return inactive_file

def add_markdown_files():
    """
    Adds markdown files from the data/markdown_files directory to the active_files table.
    """
    db = next(get_db())

    # Define the root directory of your project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # Construct the path to the markdown files
    markdown_files_dir = os.path.join(project_root, "data", "markdown_files")

    print(f"Searching for markdown files in: {markdown_files_dir}")  # Debug print statement

    for filename in os.listdir(markdown_files_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(markdown_files_dir, filename)

            with open(filepath, "rb") as f:
                file_content = f.read()

            name = filename

            create_active_file(name=name, file_content=file_content)

def move_file_to_inactive_by_id(file_id: int) -> bool:
    """
    Moves a file from the active_files table to the inactive_files table.

    Args:
        file_id (int): The ID of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the active file
        active_file = db.query(ActiveFile).filter(ActiveFile.id == file_id).first()
        if not active_file:
            print(f"Active file with ID {file_id} not found.")
            return False

        # Create an inactive file with the same data
        inactive_file = InactiveFile(
            name=active_file.name,
            file_content=active_file.file_content
        )
        db.add(inactive_file)

        # Delete the active file
        db.delete(active_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to inactive: {e}")
        return False


def move_file_to_active_by_id(file_id: int) -> bool:
    """
    Moves a file from the inactive_files table to the active_files table.

    Args:
        file_id (int): The ID of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the inactive file
        inactive_file = db.query(InactiveFile).filter(InactiveFile.id == file_id).first()
        if not inactive_file:
            print(f"Inactive file with ID {file_id} not found.")
            return False

        # Create an active file with the same data
        active_file = ActiveFile(
            name=inactive_file.name,
            file_content=inactive_file.file_content
        )
        db.add(active_file)

        # Delete the inactive file
        db.delete(inactive_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to active: {e}")
        return False

def move_file_to_inactive_by_name(name: str) -> bool:
    """
    Moves a file from the active_files table to the inactive_files table by its name.

    Args:
        name (str): The name of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the active file by name
        active_file = db.query(ActiveFile).filter(ActiveFile.name == name).first()
        if not active_file:
            print(f"Active file with name {name} not found.")
            return False

        # Create an inactive file with the same data
        inactive_file = InactiveFile(
            name=active_file.name,
            file_content=active_file.file_content
        )
        db.add(inactive_file)

        # Delete the active file
        db.delete(active_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to inactive: {e}")
        return False


def move_file_to_active_by_name(name: str) -> bool:
    """
    Moves a file from the inactive_files table to the active_files table by its name.

    Args:
        name (str): The name of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the inactive file by name
        inactive_file = db.query(InactiveFile).filter(InactiveFile.name == name).first()
        if not inactive_file:
            print(f"Inactive file with name {name} not found.")
            return False

        # Create an active file with the same data
        active_file = ActiveFile(
            name=inactive_file.name,
            file_content=inactive_file.file_content
        )
        db.add(active_file)

        # Delete the inactive file
        db.delete(inactive_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to active: {e}")
        return False

def clear_active_files() -> bool:
    """
    Clears all records from the active_files table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(ActiveFile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing active files: {e}")
        return False

def clear_inactive_files() -> bool:
    """
    Clears all records from the inactive_files table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(InactiveFile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing inactive files: {e}")
        return False

# Teacher CRUD Functions

def get_teacher_by_id(teacher_id: int) -> TeacherProfile:
    """
    Retrieves a teacher profile from the database by their id.

    Args:
        teacher_id (int): Id of the teacher to retrieve.

    Returns:
        TeacherProfile: The TeacherProfile object if found, None otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
        return teacher
    except Exception as e:
        print(f"Error retrieving teacher by ID: {e}")
        return None

def get_teacher_by_name(name: str) -> TeacherProfile:
    """
    Retrieves a teacher profile from the database by their name.

    Args:
        name (str): The name of the teacher to retrieve.

    Returns:
        TeacherProfile: The TeacherProfile object if found, None otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.name == name).first()
        return teacher
    except Exception as e:
        print(f"Error retrieving teacher by name: {e}")
        return None

def get_all_teachers() -> List[TeacherProfile]:
    """
    Retrieves all teacher profiles from the database.

    Returns:
        list: A list of TeacherProfile objects.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving all teachers: {e}")
        return []

def create_teacher(
    name: str,
    grade_level: int,
    teaching_philosophy: str,
    preferred_teaching_methods: List[str] = None,
    behavior_management_philosophy: str = None,
    areas_for_growth: List[str] = None
) -> Optional[TeacherProfile]:
    """
    Creates a new teacher profile in the database.

    Args:
        name (str): The name of the teacher
        grade_level (int): The grade level the teacher teaches
        teaching_philosophy (str): The teacher's teaching philosophy
        preferred_teaching_methods (List[str], optional): List of preferred teaching methods
        behavior_management_philosophy (str, optional): The teacher's behavior management philosophy
        areas_for_growth (List[str], optional): List of areas for growth

    Returns:
        Optional[TeacherProfile]: The created teacher profile or None if creation fails
    """
    db = next(get_db())
    try:
        teacher = TeacherProfile(
            name=name,
            grade_level=grade_level,
            teaching_philosophy=teaching_philosophy,
            preferred_teaching_methods=preferred_teaching_methods,
            behavior_management_philosophy=behavior_management_philosophy,
            areas_for_growth=areas_for_growth
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        return teacher
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating teacher: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"Unexpected error creating teacher: {e}")
        return None

def update_teacher(teacher_id: int, **kwargs) -> bool:
    """
    Updates a teacher's profile in the database.

    Args:
        teacher_id (int): The ID of the teacher to update
        **kwargs: Fields to update (name, grade_level, teaching_philosophy, etc.)

    Returns:
        bool: True if update was successful, False otherwise
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter_by(id=teacher_id).first()
        if not teacher:
            print(f"Teacher with ID {teacher_id} not found")
            return False

        for key, value in kwargs.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)
            else:
                print(f"Invalid field: {key}")
                return False

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating teacher: {e}")
        return False

def delete_teacher_by_id(teacher_id: int) -> bool:
    """
    Deletes a teacher profile from the database by ID.

    Args:
        teacher_id (int): The ID of the teacher to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
        if teacher:
            db.delete(teacher)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting teacher by ID: {e}")
        return False

def delete_teacher_by_name(name: str) -> bool:
    """
    Deletes a teacher profile from the database by name.

    Args:
        name (str): The name of the teacher to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.name == name).first()
        if teacher:
            db.delete(teacher)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting teacher by name: {e}")
        return False

def get_teachers_by_teaching_method(method: str) -> List[TeacherProfile]:
    """
    Retrieves all teachers who use a specific teaching method.

    Args:
        method (str): The teaching method to search for.

    Returns:
        list: A list of TeacherProfile objects that use the specified teaching method.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter(TeacherProfile.preferred_teaching_methods.contains([method])).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by teaching method: {e}")
        return []

def get_teachers_by_area_for_growth(area: str) -> List[TeacherProfile]:
    """
    Retrieves all teachers who have a specific area for growth.

    Args:
        area (str): The area for growth to search for.

    Returns:
        list: A list of TeacherProfile objects that have the specified area for growth.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter(TeacherProfile.areas_for_growth.contains([area])).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by area for growth: {e}")
        return []

def get_teachers_by_grade_level(grade_level: int) -> List[TeacherProfile]:
    """
    Retrieves all teachers teaching at a specific grade level.

    Args:
        grade_level (int): The grade level to filter by

    Returns:
        List[TeacherProfile]: List of teachers at the specified grade level
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter_by(grade_level=grade_level).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by grade level: {e}")
        return []

def clear_teacher_profiles() -> bool:
    """
    Clears all records from the teacher_profiles table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(TeacherProfile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing teacher profiles: {e}")
        return False

# Table Management Functions

def clear_all_tables() -> bool:
    """
    Clears all records from all tables in the database.
    Tables are cleared in a specific order to handle foreign key constraints.

    Returns:
        bool: True if all tables were cleared successfully, False otherwise.
    """
    try:
        # Clear tables in order of dependencies
        clear_dialogues()  # Clear first due to foreign key constraints
        clear_scenarios()
        clear_student_profiles()
        clear_teacher_profiles()
        clear_active_files()
        clear_inactive_files()
        return True
    except Exception as e:
        print(f"Error clearing all tables: {e}")
        return False

