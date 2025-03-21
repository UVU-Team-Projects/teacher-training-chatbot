from database import *
from crud import (
    create_teacher, get_teacher_by_id, get_teacher_by_name, get_all_teachers,
    update_teacher, delete_teacher_by_id, delete_teacher_by_name,
    get_teachers_by_teaching_method, get_teachers_by_area_for_growth,
    print_teacher_profiles, print_student_profiles, print_scenarios,
    print_dialogues, print_active_files, print_inactive_files,
    clear_teacher_profiles
)

def test_teacher_profiles():
    print("\n=== Starting Teacher Profile Tests ===\n")
    
    # Generate tables to ensure they exist
    generate_tables()
    
    # Clear the teacher_profiles table before starting tests
    if clear_teacher_profiles():
        print("Successfully cleared teacher_profiles table")
    else:
        print("Failed to clear teacher_profiles table")
        return
    
    # Test 1: Create two teachers
   
    print("Test 1: Creating two teachers...")
    teacher1 = create_teacher(
        name="John Smith",
        teaching_philosophy="I believe in student-centered learning and fostering critical thinking skills.",
        preferred_teaching_methods=["Project-Based Learning", "Inquiry-Based Learning", "Group Work"],
        behavior_management_philosophy="Positive reinforcement and clear expectations are key to maintaining a productive classroom.",
        areas_for_growth=["Technology Integration", "Differentiation"]
    )
    
    if teacher1 is None:
        print("Error: Failed to create teacher1")

    print("deleting ", delete_teacher_by_id(teacher1.id))
    

    
    teacher2 = create_teacher(
        name="Sarah Johnson",
        teaching_philosophy="I focus on building strong relationships with students and creating an inclusive learning environment.",
        preferred_teaching_methods=["Direct Instruction", "Small Group Work", "Hands-on Activities"],
        behavior_management_philosophy="Consistent routines and clear communication help create a positive learning environment.",
        areas_for_growth=["Assessment Strategies", "Classroom Management"]
    )
    
    if teacher2 is None:
        print("Error: Failed to create teacher2")

    
    
    print("\nAfter creating teachers:")
    print_teacher_profiles()
    
    # Test 2: Get teachers by ID
    print("\nTest 2: Getting teachers by ID...")
    retrieved_teacher1 = get_teacher_by_id(teacher1.id)
    retrieved_teacher2 = get_teacher_by_id(teacher2.id)
    
    if retrieved_teacher1:
        print(f"Retrieved teacher 1: {retrieved_teacher1.name}")
    else:
        print("Error: Failed to retrieve teacher 1 by ID")
    
    if retrieved_teacher2:
        print(f"Retrieved teacher 2: {retrieved_teacher2.name}")
    else:
        print("Error: Failed to retrieve teacher 2 by ID")
    
    # Test 3: Get teachers by name
    print("\nTest 3: Getting teachers by name...")
    retrieved_teacher1_by_name = get_teacher_by_name("John Smith")
    retrieved_teacher2_by_name = get_teacher_by_name("Sarah Johnson")
    
    if retrieved_teacher1_by_name:
        print(f"Retrieved teacher 1 by name: {retrieved_teacher1_by_name.name}")
    else:
        print("Error: Failed to retrieve teacher 1 by name")
    
    if retrieved_teacher2_by_name:
        print(f"Retrieved teacher 2 by name: {retrieved_teacher2_by_name.name}")
    else:
        print("Error: Failed to retrieve teacher 2 by name")
    
    # Test 4: Get all teachers
    print("\nTest 4: Getting all teachers...")
    all_teachers = get_all_teachers()
    print(f"Total number of teachers: {len(all_teachers)}")
    
    # Test 5: Update teachers
    print("\nTest 5: Updating teachers...")
    updated_teacher1 = update_teacher(
        teacher1.id,
        teaching_philosophy="Updated philosophy focusing on student engagement and active learning.",
        preferred_teaching_methods=["Project-Based Learning", "Inquiry-Based Learning", "Group Work", "Technology Integration"]
    )
    
    if updated_teacher1:
        print("\nAfter updating teacher 1:")
        print_teacher_profiles()
    else:
        print("Error: Failed to update teacher 1")
    
    # Test 6: Get teachers by teaching method
    print("\nTest 6: Getting teachers by teaching method...")
    project_based_teachers = get_teachers_by_teaching_method("Project-Based Learning")
    print(f"Teachers using Project-Based Learning: {len(project_based_teachers)}")
    
    # Test 7: Get teachers by area for growth
    print("\nTest 7: Getting teachers by area for growth...")
    tech_integration_teachers = get_teachers_by_area_for_growth("Technology Integration")
    print(f"Teachers with Technology Integration as an area for growth: {len(tech_integration_teachers)}")
    
    # Test 8: Delete teachers
    print("\nTest 8: Deleting teachers...")
    if delete_teacher_by_id(teacher1.id):
        print("Successfully deleted teacher 1 by ID")
    else:
        print("Error: Failed to delete teacher 1 by ID")
        
    if delete_teacher_by_name("Sarah Johnson"):
        print("Successfully deleted teacher 2 by name")
    else:
        print("Error: Failed to delete teacher 2 by name")
    
    print("\nAfter deleting teachers:")
    print_teacher_profiles()
    
    # Test 9: Print all tables
    print("\nTest 9: Printing all tables...")
    print("\n=== Student Profiles ===")
    print_student_profiles()
    print("\n=== Scenarios ===")
    print_scenarios()
    print("\n=== Dialogues ===")
    print_dialogues()
    print("\n=== Active Files ===")
    print_active_files()
    print("\n=== Inactive Files ===")
    print_inactive_files()
    
    print("\n=== Teacher Profile Tests Completed ===\n")

if __name__ == "__main__":
    test_teacher_profiles() 