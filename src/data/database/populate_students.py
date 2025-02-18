from database import StudentProfile, get_db  # Import from database.py
from sqlalchemy.exc import IntegrityError

# Add Maria Rodriguez (Example)
def add_maria_rodriguez():
    db = next(get_db())
    try:
        maria = StudentProfile(
            name="Maria Rodriguez",
            traits=["shy", "creative", "perfectionist", "sensitive"],
            strengths=["art", "reading comprehension", "empathy"],
            weaknesses=["public speaking", "math facts", "handling criticism"],
            motivations=["praise", "helping others", "learning new things"],
            fears=["failure", "being laughed at", "loud noises"],
            communication_style="quiet, thoughtful, sometimes hesitant. Uses a rich vocabulary but might struggle to express complex emotions verbally. Prefers writing or drawing to communicate feelings.",
            engagement_level=3
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
            traits=["energetic", "impulsive", "easily distracted", "fidgety", "enthusiastic"],
            strengths=["hands-on activities", "visual learning", "creative thinking"],
            weaknesses=["staying focused", "following multi-step instructions", "organization"],
            motivations=["positive reinforcement", "frequent breaks", "novelty"],
            fears=["being criticized", "feeling restricted", "failure"],
            communication_style="talks quickly, interrupts frequently, might have difficulty expressing thoughts in an organized way",
            engagement_level=0  # Starts with low engagement
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
            traits=["shy", "quiet", "observant", "anxious", "introverted"],
            strengths=["listening", "independent work", "detail-oriented tasks"],
            weaknesses=["group work", "public speaking", "asking for help"],
            motivations=["one-on-one interactions", "feeling safe and comfortable", "animals"],
            fears=["being called on in class", "making mistakes", "social situations"],
            communication_style="soft-spoken, hesitant, might avoid eye contact",
            engagement_level=1  # Starts with very low engagement
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
            traits=["kind", "gentle", "eager to please", "slow learner", "easily frustrated"],
            strengths=["visual learning", "hands-on activities", "repetitive tasks"],
            weaknesses=["abstract concepts", "reading comprehension", "processing information quickly"],
            motivations=["positive reinforcement", "clear expectations", "patience"],
            fears=["feeling overwhelmed", "being rushed", "negative feedback"],
            communication_style="simple sentences, might need extra time to process information, responds well to visual cues",
            engagement_level=2  # Starts with moderate engagement
        )
        db.add(david)
        db.commit()
        print("David added to the database.")
    except IntegrityError:
        db.rollback()
        print("David already exists in the database.")

# Add a user-created example
def add_user_student(name, traits, strengths=None, weaknesses=None, motivations=None, fears=None, communication_style=None, engagement_level=None):
    db = next(get_db())
    try:
        student = StudentProfile(
            name=name,
            traits=traits,
            strengths=strengths,
            weaknesses=weaknesses,
            motivations=motivations,
            fears=fears,
            communication_style=communication_style,
            engagement_level=engagement_level
        )
        db.add(student)
        db.commit()
        print(f"{name} added to the database.")
    except IntegrityError:
        db.rollback()
        print(f"{name} already exists in the database.")

if __name__ == "__main__":
    add_maria_rodriguez()
    add_user_student(name="Bob", traits=['outgoing', 'vocal', 'proud'])
    add_jacob_smith()
    add_sophia_chen()
    add_david_lee()
    