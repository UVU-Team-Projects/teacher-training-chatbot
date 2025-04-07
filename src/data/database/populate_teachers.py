from database import get_db, StudentProfile, Scenario, Dialogue, ActiveFile, InactiveFile, TeacherProfile
from crud import *
from sqlalchemy.exc import IntegrityError

def add_jane_doe():
    db = next(get_db())
    try:
        teacher = TeacherProfile(
            name="Jane Doe",
            grade_level=2,
            teaching_philosophy="Hands-on learning with focus on real-world applications",
            preferred_teaching_methods=["experiential", "cooperative learning"],
            behavior_management_philosophy="Building relationships and setting clear boundaries",
            areas_for_growth=["assessment strategies", "parent communication"]
        )
        db.add(teacher)
        db.commit()
        print("Jane Doe added to the database.")
    except IntegrityError:
        db.rollback()
        print("Jane Doe already exists in the database.")

def add_john_smith():
    db = next(get_db())
    try:
        teacher = TeacherProfile(
            name="John Smith",
            grade_level=2,
            teaching_philosophy="Student-centered learning with emphasis on critical thinking",
            preferred_teaching_methods=["project-based", "inquiry-based"],
            behavior_management_philosophy="Positive reinforcement and clear expectations",
            areas_for_growth=["technology integration", "differentiated instruction"]
        )
        db.add(teacher)
        db.commit()
        print("John Smith added to the database.")
    except IntegrityError:
        db.rollback()
        print("John Smith already exists in the database.")

def add_sarah_johnson():
    db = next(get_db())
    try:
        teacher = TeacherProfile(
            name="Sarah Johnson",
            grade_level=2,
            teaching_philosophy="Inclusive education with focus on individual learning styles",
            preferred_teaching_methods=["differentiated instruction", "flipped classroom"],
            behavior_management_philosophy="Proactive approach with emphasis on social-emotional learning",
            areas_for_growth=["data-driven instruction", "classroom technology"]
        )
        db.add(teacher)
        db.commit()
        print("Sarah Johnson added to the database.")
    except IntegrityError:
        db.rollback()
        print("Sarah Johnson already exists in the database.")

if __name__ == "__main__":
    add_jane_doe()
    add_john_smith()
    add_sarah_johnson()



    
    

