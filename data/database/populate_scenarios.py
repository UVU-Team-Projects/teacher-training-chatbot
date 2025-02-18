from database import Scenario, get_db, Dialogue
from sqlalchemy.exc import IntegrityError

def add_first_day_jitters_scenario():
    db = next(get_db())
    existing_scenario = db.query(Scenario).filter(Scenario.title == "First Day Jitters").first()
    if not existing_scenario:
        try:
            scenario = Scenario(
                title="First Day Jitters",
                description="A new student is feeling anxious on their first day."
            )
            db.add(scenario)
            db.commit()
            print("First Day Jitters scenario added to the database.")
        except IntegrityError:
            db.rollback()
            print("First Day Jitters scenario already exists in the database.")
    else:
        print("First Day Jitters scenario already exists in the database.")

def add_math_session_scenario():
    db = next(get_db())
    existing_scenario = db.query(Scenario).filter(Scenario.title == "Individual Math Session").first()
    if not existing_scenario:
        try:
            scenario = Scenario(
                title="Individual Math Session",
                description="Working with a student on addition and subtraction fluency within 20."
            )
            db.add(scenario)
            db.commit()
            print("Individual Math Session scenario added to the database.")
        except IntegrityError:
            db.rollback()
            print("Individual Math Session scenario already exists in the database.")
    else:
        print("Individual Math Session scenario already exists in the database.")

def add_reading_session_scenario():
    db = next(get_db())
    existing_scenario = db.query(Scenario).filter(Scenario.title == "Individual Reading Session").first()
    if not existing_scenario:
        try:
            scenario = Scenario(
                title="Individual Reading Session",
                description="A student reads a Ramona and Beezus book."
            )
            db.add(scenario)
            db.commit()
            print("Individual Reading Session scenario added to the database.")
        except IntegrityError:
            db.rollback()
            print("Individual Reading Session scenario already exists in the database.")
    else:
        print("Individual Reading Session scenario already exists in the database.")

def add_science_session_scenario():
    db = next(get_db())
    existing_scenario = db.query(Scenario).filter(Scenario.title == "Individual Science Session").first()
    if not existing_scenario:
        try:
            scenario = Scenario(
                title="Individual Science Session",
                description="Teaching a student about living things needing water, air, and resources to survive in habitats."
            )
            db.add(scenario)
            db.commit()
            print("Individual Science Session scenario added to the database.")
        except IntegrityError:
            db.rollback()
            print("Individual Science Session scenario already exists in the database.")
    else:
        print("Individual Science Session scenario already exists in the database.")

if __name__ == "__main__":
    add_first_day_jitters_scenario()
    add_math_session_scenario()
    add_reading_session_scenario()
    add_science_session_scenario()