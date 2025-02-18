from database import StudentProfile, get_db, Scenario, Dialogue
from sqlalchemy.exc import IntegrityError
from typing import List

# Student CRUD Functions
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


