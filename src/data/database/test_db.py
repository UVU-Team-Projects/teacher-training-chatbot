from database import get_db, StudentProfile, Scenario, Dialogue, ActiveFile, InactiveFile, TeacherProfile
from crud import *

if __name__ == "__main__":
    print_table_contents("student_profiles")
    # print_table_contents("scenarios")
    # print_table_contents("dialogues")
    # print_table_contents("active_files")
    # print_table_contents("inactive_files")
    print_table_contents("teacher_profiles")
    print(populate_teacher_profiles())
    print_table_contents("teacher_profiles")

    
    

