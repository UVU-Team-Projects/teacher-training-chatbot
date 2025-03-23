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
            behavioral_patterns={
                "morning": "quiet and focused",
                "afternoon": "more talkative and social",
                "group_work": "observes more than participates",
                "independent_work": "highly focused",
                "transitions": "needs clear expectations"
            },
            learning_style="visual and kinesthetic",
            interests=["art", "reading", "nature"],
            academic_strengths=["reading comprehension", "creative writing"],
            academic_challenges=["math", "public speaking"],
            support_strategies=["visual aids", "positive reinforcement", "flexible learning environment"],
            social_dynamics={
                "peer_interactions": "shy and reserved",
                "teacher_interaction": "responds well to individual attention"
            }
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
            behavioral_patterns={
                "morning": "high energy and distractible",
                "afternoon": "restless and needs movement breaks",
                "group_work": "can be disruptive or off-task",
                "independent_work": "struggles to stay focused",
                "transitions": "needs extra time and support"
            },
            learning_style="kinesthetic and auditory",
            interests=["building", "sports", "music"],
            academic_strengths=["hands-on activities", "visual learning"],
            academic_challenges=["sitting still", "completing tasks"],
            support_strategies=["movement breaks", "clear expectations", "positive reinforcement"],
            social_dynamics={
                "peer_interactions": "friendly but impulsive",
                "teacher_interaction": "responds well to humor and positive feedback"
            }
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
            behavioral_patterns={
                "morning": "slow to warm up",
                "afternoon": "more relaxed and engaged",
                "group_work": "prefers to listen and observe",
                "independent_work": "thrives with clear instructions",
                "transitions": "can be challenging if unexpected"
            },
            learning_style="visual and read/write",
            interests=["animals", "nature", "drawing"],
            academic_strengths=["reading comprehension", "writing"],
            academic_challenges=["public speaking", "group projects"],
            support_strategies=["quiet workspaces", "predictable routines", "opportunities for self-expression"],
            social_dynamics={
                "peer_interactions": "limited but meaningful",
                "teacher_interaction": "needs gentle encouragement and positive reinforcement"
            }
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
            behavioral_patterns={
                "morning": "needs extra time and support",
                "afternoon": "may become tired and overwhelmed",
                "group_work": "enjoys collaborative activities with support",
                "independent_work": "needs frequent check-ins and encouragement",
                "transitions": "require clear visual cues and routines"
            },
            learning_style="visual and kinesthetic",
            interests=["music", "simple games", "hands-on activities"],
            academic_strengths=["visual learning", "repetitive tasks"],
            academic_challenges=["abstract concepts", "reading comprehension", "writing"],
            support_strategies=["visual aids", "positive reinforcement", "simplified instructions", "extra time"],
            social_dynamics={
                "peer_interactions": "friendly and inclusive",
                "teacher_interaction": "responds well to patience and positive guidance"
            }
        )
        db.add(david)
        db.commit()
        print("David added to the database.")
    except IntegrityError:
        db.rollback()
        print("David already exists in the database.")


def add_emma_wilson():  # Advanced learner who can be a know-it-all
    db = next(get_db())
    try:
        emma = StudentProfile(
            name="Emma Wilson",
            grade_level=2,
            personality_traits=["confident", "outspoken", "perfectionist", "competitive", "sometimes bossy"],
            typical_moods=["enthusiastic", "frustrated", "impatient"],
            behavioral_patterns={
                "morning": "eager to start and share knowledge",
                "afternoon": "may become bored with routine tasks",
                "group_work": "tends to take charge",
                "independent_work": "completes quickly and seeks more",
                "transitions": "efficient but may rush others"
            },
            learning_style="auditory and read/write",
            interests=["science", "math", "reading", "debate"],
            academic_strengths=["advanced reading", "problem-solving", "verbal expression"],
            academic_challenges=["patience with others", "accepting different viewpoints"],
            support_strategies=["enrichment activities", "leadership opportunities", "guidance in social interactions"],
            social_dynamics={
                "peer_interactions": "can be dominant",
                "teacher_interaction": "responds well to being challenged intellectually"
            }
        )
        db.add(emma)
        db.commit()
        print("Emma added to the database.")
    except IntegrityError:
        db.rollback()
        print("Emma already exists in the database.")


def add_lucas_parker():  # ADHD with strong math skills
    db = next(get_db())
    try:
        lucas = StudentProfile(
            name="Lucas Parker",
            grade_level=2,
            personality_traits=["energetic", "mathematically gifted", "impulsive", "creative", "easily distracted"],
            typical_moods=["excited", "focused", "frustrated"],
            behavioral_patterns={
                "morning": "needs movement to focus",
                "afternoon": "more settled after physical activity",
                "group_work": "excels in hands-on math activities",
                "independent_work": "needs frequent breaks",
                "transitions": "benefits from clear countdowns"
            },
            learning_style="kinesthetic and visual",
            interests=["math games", "building", "puzzles", "sports"],
            academic_strengths=["mathematical reasoning", "pattern recognition", "spatial awareness"],
            academic_challenges=["reading comprehension", "sustained attention"],
            support_strategies=["movement breaks", "math-based transitions", "visual schedules"],
            social_dynamics={
                "peer_interactions": "friendly but can be overwhelming",
                "teacher_interaction": "responds well to math-based praise"
            }
        )
        db.add(lucas)
        db.commit()
        print("Lucas added to the database.")
    except IntegrityError:
        db.rollback()
        print("Lucas already exists in the database.")


def add_ava_martinez():  # English Language Learner
    db = next(get_db())
    try:
        ava = StudentProfile(
            name="Ava Martinez",
            grade_level=2,
            personality_traits=["resilient", "hardworking", "shy", "determined", "observant"],
            typical_moods=["focused", "anxious", "proud"],
            behavioral_patterns={
                "morning": "quiet and observant",
                "afternoon": "more comfortable with routines",
                "group_work": "prefers working with bilingual peers",
                "independent_work": "thrives with visual instructions",
                "transitions": "follows visual cues well"
            },
            learning_style="visual and kinesthetic",
            interests=["art", "music", "hands-on activities"],
            academic_strengths=["mathematical concepts", "visual learning", "determination"],
            academic_challenges=["English language comprehension", "verbal expression"],
            support_strategies=["visual aids", "bilingual support", "peer buddies", "gesture-based communication"],
            social_dynamics={
                "peer_interactions": "gradually increasing",
                "teacher_interaction": "responds well to visual and non-verbal communication"
            }
        )
        db.add(ava)
        db.commit()
        print("Ava added to the database.")
    except IntegrityError:
        db.rollback()
        print("Ava already exists in the database.")


def add_noah_thompson():  # Social butterfly who needs structure
    db = next(get_db())
    try:
        noah = StudentProfile(
            name="Noah Thompson",
            grade_level=2,
            personality_traits=["outgoing", "charismatic", "easily distracted", "creative", "sensitive"],
            typical_moods=["cheerful", "excited", "overwhelmed"],
            behavioral_patterns={
                "morning": "very social and energetic",
                "afternoon": "needs quiet time to recharge",
                "group_work": "natural leader but needs guidance",
                "independent_work": "struggles without clear structure",
                "transitions": "needs clear expectations"
            },
            learning_style="auditory and social",
            interests=["drama", "music", "group activities", "storytelling"],
            academic_strengths=["verbal expression", "creativity", "leadership"],
            academic_challenges=["focusing on tasks", "following directions"],
            support_strategies=["structured routines", "movement breaks", "social learning opportunities"],
            social_dynamics={
                "peer_interactions": "very strong",
                "teacher_interaction": "responds well to positive reinforcement and clear boundaries"
            }
        )
        db.add(noah)
        db.commit()
        print("Noah added to the database.")
    except IntegrityError:
        db.rollback()
        print("Noah already exists in the database.")


def add_olivia_brown():  # Perfectionist who needs encouragement
    db = next(get_db())
    try:
        olivia = StudentProfile(
            name="Olivia Brown",
            grade_level=2,
            personality_traits=["perfectionist", "organized", "anxious", "hardworking", "self-critical"],
            typical_moods=["focused", "worried", "frustrated"],
            behavioral_patterns={
                "morning": "prepared and organized",
                "afternoon": "may become anxious about mistakes",
                "group_work": "prefers to work alone",
                "independent_work": "very thorough but may need time limits",
                "transitions": "needs advance notice"
            },
            learning_style="visual and read/write",
            interests=["reading", "writing", "art", "organization"],
            academic_strengths=["attention to detail", "organization", "following directions"],
            academic_challenges=["handling mistakes", "time management"],
            support_strategies=["positive reinforcement", "mistake normalization", "time management tools"],
            social_dynamics={
                "peer_interactions": "selective",
                "teacher_interaction": "responds well to specific praise and reassurance"
            }
        )
        db.add(olivia)
        db.commit()
        print("Olivia added to the database.")
    except IntegrityError:
        db.rollback()
        print("Olivia already exists in the database.")


def add_liam_zhang():  # Gifted but socially reserved
    db = next(get_db())
    try:
        liam = StudentProfile(
            name="Liam Zhang",
            grade_level=2,
            personality_traits=["intelligent", "quiet", "analytical", "perfectionist", "reserved"],
            typical_moods=["focused", "thoughtful", "anxious"],
            behavioral_patterns={
                "morning": "quiet and observant",
                "afternoon": "more engaged in preferred subjects",
                "group_work": "prefers individual work",
                "independent_work": "highly focused",
                "transitions": "needs processing time"
            },
            learning_style="visual and logical",
            interests=["science", "math", "chess", "puzzles"],
            academic_strengths=["problem-solving", "analytical thinking", "advanced concepts"],
            academic_challenges=["social interactions", "expressing emotions"],
            support_strategies=["advanced materials", "quiet workspace", "social skills support"],
            social_dynamics={
                "peer_interactions": "limited but meaningful",
                "teacher_interaction": "responds well to intellectual challenges"
            }
        )
        db.add(liam)
        db.commit()
        print("Liam added to the database.")
    except IntegrityError:
        db.rollback()
        print("Liam already exists in the database.")


if __name__ == "__main__":
    add_maria_rodriguez()
    add_jacob_smith()
    add_sophia_chen()
    add_david_lee()
    add_emma_wilson()
    add_lucas_parker()
    add_ava_martinez()
    add_noah_thompson()
    add_olivia_brown()
    add_liam_zhang()
    