from database import get_db, StudentProfile, Scenario, Dialogue, create_tables
from crud import *

if __name__ == "__main__":
    print(create_student("bob", ["Shy"]))
    print(create_student("bob", ["Shy"]))
    print(create_student("jenny", ["Outgoing", "smart"]))
    print(create_student(1, ["Outgoing", "smart"]))
    print(create_student(2, "idk"))
    print(create_student(["cars", "wagon"], ["smart"]))