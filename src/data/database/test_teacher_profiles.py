from database import *
from crud import (
    create_teacher, get_teacher_by_id, get_teacher_by_name, get_all_teachers,
    update_teacher, delete_teacher_by_id, delete_teacher_by_name,
    get_teachers_by_teaching_method, get_teachers_by_area_for_growth,
    get_teachers_by_grade_level, print_teacher_profiles, print_student_profiles,
    print_scenarios, print_dialogues, print_active_files, print_inactive_files,
    clear_teacher_profiles
)

def test_teacher_crud_operations():
    print("\n=== Starting Teacher CRUD Operations Test ===")
    
    # Clear the teacher_profiles table before starting tests
    if clear_teacher_profiles():
        print("Successfully cleared teacher_profiles table")
    else:
        print("Failed to clear teacher_profiles table")
        return

    # Test 1: Create a teacher
    print("\nTest 1: Creating a teacher...")
    teacher1 = create_teacher(
        name="John Smith",
        grade_level=2,
        teaching_philosophy="Student-centered learning with emphasis on critical thinking",
        preferred_teaching_methods=["project-based", "inquiry-based"],
        behavior_management_philosophy="Positive reinforcement and clear expectations",
        areas_for_growth=["technology integration", "differentiated instruction"]
    )
    if teacher1:
        print("[+] Teacher 1 created successfully")
        print(f"  ID: {teacher1.id}")
        print(f"  Name: {teacher1.name}")
        print(f"  Grade Level: {teacher1.grade_level}")
    else:
        print("[-] Failed to create Teacher 1")
        return  # Stop testing if creation failed

    # Test 2: Create another teacher
    print("\nTest 2: Creating another teacher...")
    teacher2 = create_teacher(
        name="Jane Doe",
        grade_level=3,
        teaching_philosophy="Hands-on learning with focus on real-world applications",
        preferred_teaching_methods=["experiential", "cooperative learning"],
        behavior_management_philosophy="Building relationships and setting clear boundaries",
        areas_for_growth=["assessment strategies", "parent communication"]
    )
    if teacher2:
        print("[+] Teacher 2 created successfully")
        print(f"  ID: {teacher2.id}")
        print(f"  Name: {teacher2.name}")
        print(f"  Grade Level: {teacher2.grade_level}")
    else:
        print("[-] Failed to create Teacher 2")
        return

    # Test 3: Get teacher by ID
    print("\nTest 3: Getting teacher by ID...")
    retrieved_teacher = get_teacher_by_id(teacher1.id)
    if retrieved_teacher:
        print("[+] Successfully retrieved teacher by ID")
        print(f"  Name: {retrieved_teacher.name}")
        print(f"  Grade Level: {retrieved_teacher.grade_level}")
    else:
        print("[-] Failed to retrieve teacher by ID")

    # Test 4: Get teacher by name
    print("\nTest 4: Getting teacher by name...")
    retrieved_teacher = get_teacher_by_name("Jane Doe")
    if retrieved_teacher:
        print("[+] Successfully retrieved teacher by name")
        print(f"  ID: {retrieved_teacher.id}")
        print(f"  Grade Level: {retrieved_teacher.grade_level}")
    else:
        print("[-] Failed to retrieve teacher by name")

    # Test 5: Get all teachers
    print("\nTest 5: Getting all teachers...")
    all_teachers = get_all_teachers()
    if all_teachers:
        print("[+] Successfully retrieved all teachers")
        print(f"  Total teachers: {len(all_teachers)}")
        for teacher in all_teachers:
            print(f"  - {teacher.name} (Grade {teacher.grade_level})")
    else:
        print("[-] Failed to retrieve all teachers")

    # Test 6: Update teacher
    print("\nTest 6: Updating teacher...")
    update_success = update_teacher(
        teacher1.id,
        grade_level=4,
        teaching_philosophy="Updated philosophy focusing on personalized learning"
    )
    if update_success:
        print("[+] Successfully updated teacher")
        updated_teacher = get_teacher_by_id(teacher1.id)
        print(f"  New grade level: {updated_teacher.grade_level}")
        print(f"  New philosophy: {updated_teacher.teaching_philosophy}")
    else:
        print("[-] Failed to update teacher")

    # Test 7: Get teachers by teaching method
    print("\nTest 7: Getting teachers by teaching method...")
    project_based_teachers = get_teachers_by_teaching_method("project-based")
    if project_based_teachers:
        print("[+] Successfully retrieved teachers by teaching method")
        print(f"  Found {len(project_based_teachers)} teachers using project-based learning")
        for teacher in project_based_teachers:
            print(f"  - {teacher.name} (Grade {teacher.grade_level})")
    else:
        print("[-] Failed to retrieve teachers by teaching method")

    # Test 8: Get teachers by area for growth
    print("\nTest 8: Getting teachers by area for growth...")
    tech_teachers = get_teachers_by_area_for_growth("technology integration")
    if tech_teachers:
        print("[+] Successfully retrieved teachers by area for growth")
        print(f"  Found {len(tech_teachers)} teachers with technology integration as growth area")
        for teacher in tech_teachers:
            print(f"  - {teacher.name} (Grade {teacher.grade_level})")
    else:
        print("[-] Failed to retrieve teachers by area for growth")

    # Test 9: Get teachers by grade level
    print("\nTest 9: Getting teachers by grade level...")
    grade_3_teachers = get_teachers_by_grade_level(3)
    if grade_3_teachers:
        print("[+] Successfully retrieved teachers by grade level")
        print(f"  Found {len(grade_3_teachers)} teachers in grade 3")
        for teacher in grade_3_teachers:
            print(f"  - {teacher.name}")
    else:
        print("[-] Failed to retrieve teachers by grade level")

    # Test 10: Delete teacher by ID
    print("\nTest 10: Deleting teacher by ID...")
    if delete_teacher_by_id(teacher1.id):
        print("[+] Successfully deleted teacher by ID")
        deleted_teacher = get_teacher_by_id(teacher1.id)
        if not deleted_teacher:
            print("  [+] Verified teacher was deleted")
        else:
            print("  [-] Teacher still exists after deletion")
    else:
        print("[-] Failed to delete teacher by ID")

    # Test 11: Delete teacher by name
    print("\nTest 11: Deleting teacher by name...")
    if delete_teacher_by_name("Jane Doe"):
        print("[+] Successfully deleted teacher by name")
        deleted_teacher = get_teacher_by_name("Jane Doe")
        if not deleted_teacher:
            print("  [+] Verified teacher was deleted")
        else:
            print("  [-] Teacher still exists after deletion")
    else:
        print("[-] Failed to delete teacher by name")

    # Test 12: Print all teacher profiles
    print("\nTest 12: Printing all teacher profiles...")
    print_teacher_profiles()

    print("\n=== Teacher CRUD Operations Test Complete ===")

if __name__ == "__main__":
    # Generate tables first to ensure they exist with the correct schema
    generate_tables()
    test_teacher_crud_operations() 