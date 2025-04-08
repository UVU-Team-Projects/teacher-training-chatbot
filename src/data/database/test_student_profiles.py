"""
Test script for student profile CRUD operations.
This script tests creating, retrieving, updating, and deleting StudentProfile objects.
"""

from src.data.database.crud import (
    initialize_database, 
    create_student_profile_from_object,
    get_student_object_by_id,
    get_student_object_by_name,
    delete_student_by_id
)
from src.ai.student_profiles import StudentProfile, Mood, Interest

def main():
    # Initialize the database
    print("Initializing database...")
    initialize_database()
    
    # Create a test student profile
    print("\nCreating test student profile...")
    test_student = StudentProfile(
        name="Test Student",
        grade_level=5,
        personality_traits=["curious", "energetic"],
        typical_moods=[Mood.HAPPY, Mood.FOCUSED],
        behavioral_patterns={"classroom": "active", "independent": "focused"},
        learning_style="kinesthetic",
        interests=[Interest.SPORTS, Interest.ARTS],
        academic_strengths=["math", "science"],
        academic_challenges=["reading"],
        support_strategies=["visual aids", "breaks"],
        social_dynamics={"peers": "friendly", "adults": "respectful"}
    )
    
    # Store the student in the database
    db_student = create_student_profile_from_object(test_student)
    if db_student:
        print(f"Created student profile with ID: {db_student.id}")
        student_id = db_student.id
    else:
        print("Failed to create student profile")
        return
    
    # Retrieve the student by ID
    print("\nRetrieving student by ID...")
    retrieved_student = get_student_object_by_id(student_id)
    if retrieved_student:
        print(f"Retrieved student: {retrieved_student.name}")
        print(f"Grade Level: {retrieved_student.grade_level}")
        print(f"Personality Traits: {retrieved_student.personality_traits}")
        print(f"Typical Moods: {[mood.name for mood in retrieved_student.typical_moods]}")
        print(f"Interests: {[interest.name for interest in retrieved_student.interests]}")
    else:
        print("Failed to retrieve student by ID")
    
    # Retrieve the student by name
    print("\nRetrieving student by name...")
    name_retrieved_student = get_student_object_by_name("Test Student")
    if name_retrieved_student:
        print(f"Retrieved student by name: {name_retrieved_student.name}")
    else:
        print("Failed to retrieve student by name")
    
    # Delete the student
    print("\nDeleting student...")
    if delete_student_by_id(student_id):
        print("Student deleted successfully")
    else:
        print("Failed to delete student")
    
    # Verify deletion
    deleted_check = get_student_object_by_id(student_id)
    if deleted_check is None:
        print("Verified student was deleted")
    else:
        print("Student was not deleted")

if __name__ == "__main__":
    main() 