from database import Dialogue, get_db, Scenario
from sqlalchemy.exc import IntegrityError

def add_maria_dialogues():
    db = next(get_db())
    student_name = "Maria Rodriguez"

    # Get scenario IDs
    first_day_jitters_id = db.query(Scenario).filter(Scenario.title == "First Day Jitters").first().id
    math_session_id = db.query(Scenario).filter(Scenario.title == "Individual Math Session").first().id
    reading_session_id = db.query(Scenario).filter(Scenario.title == "Individual Reading Session").first().id
    science_session_id = db.query(Scenario).filter(Scenario.title == "Individual Science Session").first().id

    dialogues = [
        {"scenario_id": first_day_jitters_id, "utterance": "I... I don't know anyone here."},
        {"scenario_id": first_day_jitters_id, "utterance": "Will I be able to do the work? What if it's too hard?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I don't want to go to recess. It's too loud outside."},
        {"scenario_id": math_session_id, "utterance": "Seven plus five... umm... twelve?"},
        {"scenario_id": math_session_id, "utterance": "I like using the blocks to count, but I get confused with bigger numbers."},
        {"scenario_id": math_session_id, "utterance": "Can I draw a picture to help me solve the problem?"},
        {"scenario_id": reading_session_id, "utterance": "Ramona is so funny! I like how she makes mistakes, but it always works out in the end."},
        {"scenario_id": reading_session_id, "utterance": "I wish I had a sister like Beezus."},
        {"scenario_id": reading_session_id, "utterance": "I love reading! It's like watching a movie in my head."},
        {"scenario_id": science_session_id, "utterance": "Why do plants need sunlight? Do they eat it?"},
        {"scenario_id": science_session_id, "utterance": "I wonder if there are living things in outer space... Do they need water and air too?"},
        {"scenario_id": science_session_id, "utterance": "I want to be a scientist when I grow up and discover new animals!"}
    ]

    for dialogue in dialogues:
        try:
            # Check for duplicate dialogues
            existing_dialogue = db.query(Dialogue).filter(
                Dialogue.scenario_id == dialogue["scenario_id"],
                Dialogue.student_name == student_name,
                Dialogue.utterance == dialogue["utterance"]
            ).first()

            if not existing_dialogue:
                db_dialogue = Dialogue(
                    scenario_id=dialogue["scenario_id"],
                    student_name=student_name,
                    utterance=dialogue["utterance"]
                )
                db.add(db_dialogue)
                db.commit()
                print(f"Dialogue added for {student_name} in scenario {dialogue['scenario_id']}.")
            else:
                print(f"Dialogue for {student_name} in scenario {dialogue['scenario_id']} already exists.")
        except IntegrityError:
            db.rollback()
            print(f"Error adding dialogue for {student_name} in scenario {dialogue['scenario_id']}.")

def add_jacob_dialogues():
    db = next(get_db())
    student_name = "Jacob Smith"

    # Get scenario IDs (same as in add_maria_dialogues)
    first_day_jitters_id = db.query(Scenario).filter(Scenario.title == "First Day Jitters").first().id
    math_session_id = db.query(Scenario).filter(Scenario.title == "Individual Math Session").first().id
    reading_session_id = db.query(Scenario).filter(Scenario.title == "Individual Reading Session").first().id
    science_session_id = db.query(Scenario).filter(Scenario.title == "Individual Science Session").first().id

    dialogues = [
        {"scenario_id": first_day_jitters_id, "utterance": "Wow! This school is so big! Can we go explore?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I can't wait to meet my teacher! I hope they like dinosaurs."},
        {"scenario_id": first_day_jitters_id, "utterance": "Is it time for recess yet? I have so much energy!"},
        {"scenario_id": math_session_id, "utterance": "Seven plus five is... hmm... let me count... thirteen! No, wait... twelve!"},
        {"scenario_id": math_session_id, "utterance": "Can I use the number line? It's easier than counting on my fingers."},
        {"scenario_id": math_session_id, "utterance": "This is boring! Can we play a math game instead?"},
        {"scenario_id": reading_session_id, "utterance": "Ramona is so silly! I like when she makes mischief."},
        {"scenario_id": reading_session_id, "utterance": "I can't sit still for this long. Can I stand up and read?"},
        {"scenario_id": reading_session_id, "utterance": "This book has too many words! Can we read a comic book instead?"},
        {"scenario_id": science_session_id, "utterance": "Plants drink water with their roots, right? Like straws!"},
        {"scenario_id": science_session_id, "utterance": "Do you think aliens have habitats too? Maybe on Mars!"},
        {"scenario_id": science_session_id, "utterance": "I want to build a robot that can explore the ocean and find new creatures!"}
    ]
    for dialogue in dialogues:
        try:
            # Check for duplicate dialogues
            existing_dialogue = db.query(Dialogue).filter(
                Dialogue.scenario_id == dialogue["scenario_id"],
                Dialogue.student_name == student_name,
                Dialogue.utterance == dialogue["utterance"]
            ).first()

            if not existing_dialogue:
                db_dialogue = Dialogue(
                    scenario_id=dialogue["scenario_id"],
                    student_name=student_name,
                    utterance=dialogue["utterance"]
                )
                db.add(db_dialogue)
                db.commit()
                print(f"Dialogue added for {student_name} in scenario {dialogue['scenario_id']}.")
            else:
                print(f"Dialogue for {student_name} in scenario {dialogue['scenario_id']} already exists.")
        except IntegrityError:
            db.rollback()
            print(f"Error adding dialogue for {student_name} in scenario {dialogue['scenario_id']}.")

def add_sophia_dialogues():
    db = next(get_db())
    student_name = "Sophia Chen"

    # Get scenario IDs (same as in add_maria_dialogues)
    first_day_jitters_id = db.query(Scenario).filter(Scenario.title == "First Day Jitters").first().id
    math_session_id = db.query(Scenario).filter(Scenario.title == "Individual Math Session").first().id
    reading_session_id = db.query(Scenario).filter(Scenario.title == "Individual Reading Session").first().id
    science_session_id = db.query(Scenario).filter(Scenario.title == "Individual Science Session").first().id

    dialogues = [
        {"scenario_id": first_day_jitters_id, "utterance": "Um... excuse me... is it okay if I sit here?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I don't understand the instructions. Can you repeat them?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I'm not sure... I don't want to say the wrong answer."},
        {"scenario_id": math_session_id, "utterance": "Seven plus five... I think it's twelve... but I'm not sure."},
        {"scenario_id": math_session_id, "utterance": "Can I have some more time to think about it?"},
        {"scenario_id": math_session_id, "utterance": "I don't like talking in front of the class. Can I show you my answer on paper?"},
        {"scenario_id": reading_session_id, "utterance": "I like Ramona. She's quiet like me."},
        {"scenario_id": reading_session_id, "utterance": "I don't really like reading out loud. Can I read it silently to myself?"},
        {"scenario_id": reading_session_id, "utterance": "I like books about animals. Do you have any more like this one?"},
        {"scenario_id": science_session_id, "utterance": "Why do animals need to live in different habitats?"},
        {"scenario_id": science_session_id, "utterance": "I saw a documentary about the rainforest. It was amazing!"},
        {"scenario_id": science_session_id, "utterance": "I want to have a pet cat someday. They're my favorite animal."}
    ]
    for dialogue in dialogues:
        try:
            # Check for duplicate dialogues
            existing_dialogue = db.query(Dialogue).filter(
                Dialogue.scenario_id == dialogue["scenario_id"],
                Dialogue.student_name == student_name,
                Dialogue.utterance == dialogue["utterance"]
            ).first()

            if not existing_dialogue:
                db_dialogue = Dialogue(
                    scenario_id=dialogue["scenario_id"],
                    student_name=student_name,
                    utterance=dialogue["utterance"]
                )
                db.add(db_dialogue)
                db.commit()
                print(f"Dialogue added for {student_name} in scenario {dialogue['scenario_id']}.")
            else:
                print(f"Dialogue for {student_name} in scenario {dialogue['scenario_id']} already exists.")
        except IntegrityError:
            db.rollback()
            print(f"Error adding dialogue for {student_name} in scenario {dialogue['scenario_id']}.")

def add_david_dialogues():
    db = next(get_db())
    student_name = "David Lee"

    # Get scenario IDs (same as in add_maria_dialogues)
    first_day_jitters_id = db.query(Scenario).filter(Scenario.title == "First Day Jitters").first().id
    math_session_id = db.query(Scenario).filter(Scenario.title == "Individual Math Session").first().id
    reading_session_id = db.query(Scenario).filter(Scenario.title == "Individual Reading Session").first().id
    science_session_id = db.query(Scenario).filter(Scenario.title == "Individual Science Session").first().id

    dialogues = [
        {"scenario_id": first_day_jitters_id, "utterance": "Hi... Is this my classroom?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I brought my favorite book. Can I show you?"},
        {"scenario_id": first_day_jitters_id, "utterance": "I'm a little nervous, but I'm excited to be here."},
        {"scenario_id": math_session_id, "utterance": "Seven plus five... hmm... can you count with me?"},
        {"scenario_id": math_session_id, "utterance": "I like the pictures. They help me understand."},
        {"scenario_id": math_session_id, "utterance": "This is hard. Can we take a break?"},
        {"scenario_id": reading_session_id, "utterance": "Ramona is funny. I like her."},
        {"scenario_id": reading_session_id, "utterance": "Can you help me with this word? I don't know it."},
        {"scenario_id": reading_session_id, "utterance": "I like reading with you. It's fun."},
        {"scenario_id": science_session_id, "utterance": "What's a habitat? Is it like a house?"},
        {"scenario_id": science_session_id, "utterance": "I like animals. My dog needs water and food every day."},
        {"scenario_id": science_session_id, "utterance": "This is interesting! Can we learn more about plants next time?"}
    ]
    for dialogue in dialogues:
        try:
            # Check for duplicate dialogues
            existing_dialogue = db.query(Dialogue).filter(
                Dialogue.scenario_id == dialogue["scenario_id"],
                Dialogue.student_name == student_name,
                Dialogue.utterance == dialogue["utterance"]
            ).first()

            if not existing_dialogue:
                db_dialogue = Dialogue(
                    scenario_id=dialogue["scenario_id"],
                    student_name=student_name,
                    utterance=dialogue["utterance"]
                )
                db.add(db_dialogue)
                db.commit()
                print(f"Dialogue added for {student_name} in scenario {dialogue['scenario_id']}.")
            else:
                print(f"Dialogue for {student_name} in scenario {dialogue['scenario_id']} already exists.")
        except IntegrityError:
            db.rollback()
            print(f"Error adding dialogue for {student_name} in scenario {dialogue['scenario_id']}.")

if __name__ == "__main__":
    add_maria_dialogues()
    add_jacob_dialogues()
    add_sophia_dialogues()
    add_david_dialogues()