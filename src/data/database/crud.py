from .database import StudentProfile, get_db, Scenario, Dialogue, ActiveFile, InactiveFile
from sqlalchemy.exc import IntegrityError
from typing import List, Union
import os

def print_table_contents(table_name: str):
    """
    Prints the contents of the specified table.

    Args:
        table_name (str): The name of the table to print.
    """
    db = next(get_db())

    if table_name == "student_profiles":
        students = db.query(StudentProfile).all()
        print("\nstudent_profiles table contents:")
        for student in students:
            print(f"  ID: {student.id}")
            print(f"  Name: {student.name}")
            print(f"  Traits: {', '.join(student.traits)}")
            print(f"  Strengths: {', '.join(student.strengths) if student.strengths else 'None'}")
            print(f"  Weaknesses: {', '.join(student.weaknesses) if student.weaknesses else 'None'}")
            print(f"  Motivations: {', '.join(student.motivations) if student.motivations else 'None'}")
            print(f"  Fears: {', '.join(student.fears) if student.fears else 'None'}")
            print(f"  Communication Style: {student.communication_style}")
            print(f"  Engagement Level: {student.engagement_level}")
            print("-" * 20)  # Separator between students
    elif table_name == "scenarios":
        scenarios = db.query(Scenario).all()
        print("\nscenarios table contents:")
        for scenario in scenarios:
            print(f"  ID: {scenario.id}")
            print(f"  Title: {scenario.title}")
            print(f"  Description: {scenario.description}")
            print("-" * 20)  # Separator between scenarios
    elif table_name == "dialogues":
        dialogues = db.query(Dialogue).all()
        print("\ndialogues table contents:")
        for dialogue in dialogues:
            print(f"  ID: {dialogue.id}")
            print(f"  Scenario ID: {dialogue.scenario_id}")
            print(f"  Student Name: {dialogue.student_name}")
            print(f"  Utterance: {dialogue.utterance}")
            print("-" * 20)  # Separator between dialogues
    elif table_name == "active_files":
        active_files = db.query(ActiveFile).all()
        print("\nactive_files table contents:")
        for file in active_files:
            print(f"ID: {file.id}, Name: {file.name}")  # Print only ID and name
    elif table_name == "inactive_files":
        inactive_files = db.query(InactiveFile).all()
        print("\ninactive_files table contents:")
        for file in inactive_files:
            print(f"ID: {file.id}, Name: {file.name}")  # Print only ID and name
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

def create_student(name: str, traits: list, strengths: list = None, weaknesses: list = None, motivations: list = None, fears: list = None, communication_style: str = None) -> StudentProfile:
    """
    Creates a new student profile in the database.

    Args:
        name (str): The name of the student.
        traits (list): A list of personality traits for the student.
        strengths (list, optional): A list of strengths for the student. Defaults to None.
        weaknesses (list, optional): A list of weaknesses for the student. Defaults to None.
        motivations (list, optional): A list of motivations for the student. Defaults to None.
        fears (list, optional): A list of fears for the student. Defaults to None.
        communication_style (str, optional): A description of the student's communication style. Defaults to None.

    Returns:
        StudentProfile: The created StudentProfile object, or None if creation failed.
    """
    db = next(get_db())
    try:
        student = StudentProfile(
            name=name,
            traits=traits,
            strengths=strengths,
            weaknesses=weaknesses,
            motivations=motivations,
            fears=fears,
            communication_style=communication_style
        )
        db.add(student)
        db.commit()
        db.refresh(student)  # Refresh to get the generated ID
        return student
    except IntegrityError:
        db.rollback()
        return None  # Or raise an exception, depending on your error handling strategy

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

def delete_student(student_id: int) -> bool:
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

def create_scenario(title: str, description: str) -> Scenario:
    """
    Creates a new scenario in the database.

    Args:
        title (str): The title of the scenario.
        description (str): The description of the scenario.

    Returns:
        Scenario: The created Scenario object, or None if creation failed.
    """
    db = next(get_db())
    try:
        scenario = Scenario(title=title, description=description)
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

    Returns:
        Scenario: The updated Scenario object, or None if the update failed.
    """
    db = next(get_db())
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario:
        for key, value in kwargs.items():
            setattr(scenario, key, value)
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

