"""
Test script for student profile CRUD operations.
This script tests creating, retrieving, updating, and deleting student profiles,
including conversion between database profiles and custom profiles.
"""

import json
from src.ai.student_profiles import StudentProfile, Interest, Mood, create_student_profile as create_custom_profile
from database import get_db
from crud import (
    clear_student_profiles, 
    create_student_profile,
    create_student_profile_from_object,
    get_student_by_id,
    get_student_by_name,
    get_all_students,
    get_custom_student_by_id,
    update_student,
    delete_student_by_id,
    delete_student_by_name,
    print_student_profiles
)

def test_student_profiles():
    """Run all student profile tests."""
    print("\n=========== STUDENT PROFILE TESTS ===========\n")
    
    # Start with a clean database
    print("Clearing student profiles table...")
    clear_student_profiles()
    print("Table cleared.")
    
    # Test 1: Create student profiles with direct parameters
    print("\n===== TEST 1: Create student profiles with direct parameters =====\n")
    
    print("Creating Maria Rodriguez...")
    maria = create_student_profile(
        name="Maria Rodriguez",
        grade_level=5,
        personality_traits=["quiet", "observant", "creative"],
        typical_moods=["focused", "happy"],  # Using valid values from Mood enum
        behavioral_patterns={"classroom": "prefers independent work", "group": "listens more than speaks"},
        learning_style="visual",
        interests=["reading", "arts", "nature"],  # Using valid values from Interest enum
        academic_strengths=["reading comprehension", "creative writing"],
        academic_challenges=["math", "public speaking"],
        support_strategies=["visual aids", "positive reinforcement", "flexible learning environment"],
        social_dynamics={"peers": "few close friends", "adults": "respectful but reserved"},
        template_name=""
    )
    
    print(f"Created Maria with ID: {maria.id}")
    
    # Test 2: Create student profile from StudentProfile object
    print("\n===== TEST 2: Create student profile from StudentProfile object =====\n")
    
    print("Creating a StudentProfile object for Jacob Smith...")
    jacob_custom = StudentProfile(
        name="Jacob Smith",
        grade_level=5,
        personality_traits=["energetic", "curious", "hands-on"],
        typical_moods=[Mood.EXCITED, Mood.FOCUSED],
        behavioral_patterns={"classroom": "needs movement breaks", "group": "active participant"},
        learning_style="kinesthetic",
        interests=[Interest.SPORTS, Interest.TECHNOLOGY, Interest.MUSIC],
        academic_strengths=["hands-on activities", "visual learning"],
        academic_challenges=["sitting still", "completing tasks"],
        support_strategies=["movement breaks", "clear expectations", "positive reinforcement"],
        social_dynamics={"peers": "popular and outgoing", "adults": "friendly but needs boundaries"}
    )
    
    print("Converting and storing Jacob's StudentProfile in the database...")
    jacob_db = create_student_profile_from_object(jacob_custom)
    print(f"Created Jacob with ID: {jacob_db.id}")
    
    # Test 3: Create student with template using teammate's create_student_profile
    print("\n===== TEST 3: Create student with template using create_custom_profile =====\n")
    
    print("Creating a StudentProfile from template for Sophia Chen...")
    sophia_custom = create_custom_profile(
        template_name="struggling_student",
        name="Sophia Chen",
        grade_level=5,
        interests=[Interest.NATURE, Interest.ARTS],
        academic_strengths=["artistic expression", "observational skills"],
        academic_challenges=["reading comprehension", "math"],
        support_strategies=["small group instruction", "visual aids", "positive reinforcement"]
    )
    
    print("Converting and storing Sophia's StudentProfile in the database...")
    sophia_db = create_student_profile_from_object(sophia_custom)
    print(f"Created Sophia with ID: {sophia_db.id}")
    
    # Test 4: Get all student profiles
    print("\n===== TEST 4: Get all student profiles =====\n")
    
    students = get_all_students()
    print(f"Retrieved {len(students)} student profiles")
    print_student_profiles()
    
    # Test 5: Get student profile by ID
    print("\n===== TEST 5: Get student profile by ID =====\n")
    
    maria_retrieved = get_student_by_id(maria.id)
    print(f"Retrieved Maria by ID: {maria_retrieved.name}, template: {maria_retrieved.template_name}")
    
    # Test 6: Get student profile by name
    print("\n===== TEST 6: Get student profile by name =====\n")
    
    jacob_retrieved = get_student_by_name("Jacob Smith")
    print(f"Retrieved Jacob by name: ID {jacob_retrieved.id}")
    
    # Test 7: Get student as StudentProfile
    print("\n===== TEST 7: Get student as StudentProfile =====\n")
    
    maria_custom = get_custom_student_by_id(maria.id)
    print(f"Retrieved Maria as StudentProfile: {maria_custom.name}")
    
    # Check the exact type
    from src.ai.student_profiles import StudentProfile as OriginalStudentProfile
    print(f"Type check: {type(maria_custom) is OriginalStudentProfile}")
    print(f"Type name: {type(maria_custom).__name__}")
    
    # Print interests and moods safely
    if hasattr(maria_custom, 'interests') and maria_custom.interests:
        interests = [interest.value for interest in maria_custom.interests]
        print(f"Maria's interests: {interests}")
    else:
        print("Maria's interests not available")
        
    if hasattr(maria_custom, 'typical_moods') and maria_custom.typical_moods:
        moods = [mood.value for mood in maria_custom.typical_moods]
        print(f"Maria's typical moods: {moods}")
    else:
        print("Maria's typical moods not available")
    
    # Test 8: Update student profile
    print("\n===== TEST 8: Update student profile =====\n")
    
    print("Updating Maria's grade level to 6...")
    update_student(maria.id, grade_level=6)
    
    maria_updated = get_student_by_id(maria.id)
    print(f"Maria's grade level is now: {maria_updated.grade_level}")
    
    # Test 9: More complex update with JSON fields
    print("\n===== TEST 9: More complex update with JSON fields =====\n")
    
    new_social_dynamics = {"peers": "becoming more outgoing", "adults": "respectful and engaging"}
    social_dynamics_json = json.dumps(new_social_dynamics)
    
    print("Updating Maria's social dynamics...")
    update_student(maria.id, social_dynamics=social_dynamics_json)
    
    maria_updated = get_student_by_id(maria.id)
    social_dynamics = json.loads(maria_updated.social_dynamics)
    print(f"Maria's updated social dynamics: {social_dynamics}")
    
    # Test 10: Delete student by ID
    print("\n===== TEST 10: Delete student by ID =====\n")
    
    print(f"Deleting student with ID {maria.id} (Maria)...")
    delete_student_by_id(maria.id)
    
    # Verify deletion
    remaining_students = get_all_students()
    print(f"Remaining students: {len(remaining_students)}")
    
    # Test 11: Delete student by name
    print("\n===== TEST 11: Delete student by name =====\n")
    
    print("Deleting student with name 'Jacob Smith'...")
    delete_student_by_name("Jacob Smith")
    
    # Verify deletion
    remaining_students = get_all_students()
    print(f"Remaining students: {len(remaining_students)}")
    print_student_profiles()
    
    # Clean up
    print("\n===== Cleaning up =====\n")
    clear_student_profiles()
    print("All student profiles cleared.")
    
    print("\n=========== ALL TESTS COMPLETED ===========\n")

if __name__ == "__main__":
    test_student_profiles() 