from database import StudentProfile, get_db  # Import from database.py
from sqlalchemy.exc import IntegrityError

# Add Maria Rodriguez (Example)
def add_maria_rodriguez():
    db = next(get_db())
    try:
        maria = StudentProfile(
            name="Maria Rodriguez",
            grade_level=2,
            personality_traits=["shy", "creative", "perfectionist", "sensitive"],
            typical_moods=["focused", "daydreamer", "anxious"],
            behavioral_patterns='{"morning": "quiet and focused", "afternoon": "more talkative and social", "group_work": "observes more than participates", "independent_work": "highly focused", "transitions": "needs clear expectations"}',
            learning_style="visual and kinesthetic",
            interests=["art", "reading", "nature"],
            academic_strengths=["reading comprehension", "creative writing"],
            academic_challenges=["math", "public speaking"],
            support_strategies=["visual aids", "positive reinforcement", "flexible learning environment"],
            social_dynamics='{"peer_interactions": "shy and reserved", "teacher_interaction": "responds well to individual attention"}'
        )
        db.add(maria)
        db.commit()
        print("Maria added to the database.")
    except IntegrityError:
        db.rollback()
        print("Maria already exists in the database.")


def add_jacob_smith():  # Student with ADHD
    db = next(get_db())
    try:
        jacob = StudentProfile(
            name="Jacob Smith",
            grade_level=2,
            personality_traits=["energetic", "impulsive", "easily distracted", "fidgety", "enthusiastic"],
            typical_moods=["excited", "restless", "frustrated"],
            behavioral_patterns='{"morning": "high energy and distractible", "afternoon": "restless and needs movement breaks", "group_work": "can be disruptive or off-task", "independent_work": "struggles to stay focused", "transitions": "needs extra time and support"}',
            learning_style="kinesthetic and auditory",
            interests=["building", "sports", "music"],
            academic_strengths=["hands-on activities", "visual learning"],
            academic_challenges=["sitting still", "completing tasks"],
            support_strategies=["movement breaks", "clear expectations", "positive reinforcement"],
            social_dynamics='{"peer_interactions": "friendly but impulsive", "teacher_interaction": "responds well to humor and positive feedback"}'
        )
        db.add(jacob)
        db.commit()
        print("Jacob added to the database.")
    except IntegrityError:
        db.rollback()
        print("Jacob already exists in the database.")


def add_sophia_chen():  # Shy and hard to engage
    db = next(get_db())
    try:
        sophia = StudentProfile(
            name="Sophia Chen",
            grade_level=2,
            personality_traits=["shy", "quiet", "observant", "anxious", "introverted"],
            typical_moods=["calm", "withdrawn", "worried"],
            behavioral_patterns='{"morning": "slow to warm up", "afternoon": "more relaxed and engaged", "group_work": "prefers to listen and observe", "independent_work": "thrives with clear instructions", "transitions": "can be challenging if unexpected"}',
            learning_style="visual and read/write",
            interests=["animals", "nature", "drawing"],
            academic_strengths=["reading comprehension", "writing"],
            academic_challenges=["public speaking", "group projects"],
            support_strategies=["quiet workspaces", "predictable routines", "opportunities for self-expression"],
            social_dynamics='{"peer_interactions": "limited but meaningful", "teacher_interaction": "needs gentle encouragement and positive reinforcement"}'
        )
        db.add(sophia)
        db.commit()
        print("Sophia added to the database.")
    except IntegrityError:
        db.rollback()
        print("Sophia already exists in the database.")


def add_david_lee():  # Mild mental disability
    db = next(get_db())
    try:
        david = StudentProfile(
            name="David Lee",
            grade_level=2,
            personality_traits=["kind", "gentle", "eager to please", "slow learner", "easily frustrated"],
            typical_moods=["happy", "confused", "upset"],
            behavioral_patterns='{"morning": "needs extra time and support", "afternoon": "may become tired and overwhelmed", "group_work": "enjoys collaborative activities with support", "independent_work": "needs frequent check-ins and encouragement", "transitions": "require clear visual cues and routines"}',
            learning_style="visual and kinesthetic",
            interests=["music", "simple games", "hands-on activities"],
            academic_strengths=["visual learning", "repetitive tasks"],
            academic_challenges=["abstract concepts", "reading comprehension", "writing"],
            support_strategies=["visual aids", "positive reinforcement", "simplified instructions", "extra time"],
            social_dynamics='{"peer_interactions": "friendly and inclusive", "teacher_interaction": "responds well to patience and positive guidance"}'
        )
        db.add(david)
        db.commit()
        print("David added to the database.")
    except IntegrityError:
        db.rollback()
        print("David already exists in the database.")


if __name__ == "__main__":
    add_maria_rodriguez()
    add_jacob_smith()
    add_sophia_chen()
    add_david_lee()
    