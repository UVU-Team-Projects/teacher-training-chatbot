from typing import List, Dict, Any, Optional, Union
from sqlalchemy.exc import IntegrityError
import json
import os

from database import StudentProfileDB, TeacherProfile, get_db, Scenario, Dialogue, ActiveFile, InactiveFile, generate_tables, SessionLocal
from src.ai.student_profiles import StudentProfile, Mood, Interest, create_student_profile as create_custom_profile

def initialize_database():
    """
    Generates all database tables.
    This function should be called before populating the database with data.
    """
    try:
        generate_tables()
        print("Database tables generated successfully.")
        return True
    except Exception as e:
        print(f"Error generating database tables: {e}")
        return False

def populate_student_profiles() -> bool:
    """
    Populates the student_profiles table with example data.
    Returns True if successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Create example students directly in the database with template information
        maria = create_student_profile(
            name="Maria Rodriguez",
            grade_level=5,
            personality_traits=["quiet", "observant", "creative"],
            typical_moods=["focused", "happy"],
            behavioral_patterns={"classroom": "prefers independent work", "group": "listens more than speaks"},
            learning_style="visual",
            interests=["reading", "arts", "nature"],
            academic_strengths=["reading comprehension", "creative writing"],
            academic_challenges=["math", "public speaking"],
            support_strategies=["visual aids", "positive reinforcement", "flexible learning environment"],
            social_dynamics={"peers": "few close friends", "adults": "respectful but reserved"},
            template_name="quiet_observer"
        )
        
        jacob = create_student_profile(
            name="Jacob Smith",
            grade_level=5,
            personality_traits=["energetic", "curious", "hands-on"],
            typical_moods=["excited", "focused"],
            behavioral_patterns={"classroom": "needs movement breaks", "group": "active participant"},
            learning_style="kinesthetic",
            interests=["sports", "technology", "music"],
            academic_strengths=["hands-on activities", "visual learning"],
            academic_challenges=["sitting still", "completing tasks"],
            support_strategies=["movement breaks", "clear expectations", "positive reinforcement"],
            social_dynamics={"peers": "popular and outgoing", "adults": "friendly but needs boundaries"},
            template_name="active_learner"
        )
        
        sophia = create_student_profile(
            name="Sophia Chen",
            grade_level=5,
            personality_traits=["artistic", "observant", "sensitive"],
            typical_moods=["thoughtful", "anxious"],
            behavioral_patterns={"classroom": "needs reassurance", "group": "prefers one-on-one"},
            learning_style="visual",
            interests=["nature", "arts"],
            academic_strengths=["artistic expression", "observational skills"],
            academic_challenges=["reading comprehension", "math"],
            support_strategies=["small group instruction", "visual aids", "positive reinforcement"],
            social_dynamics={"peers": "selective in friendships", "adults": "seeks approval"},
            template_name="struggling_student"
        )
        
        if not maria or not jacob or not sophia:
            print("Failed to create one or more student profiles")
            return False
            
        return True
    except IntegrityError:
        db.rollback()
        print("Student profiles already exist in the database.")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error populating student profiles: {e}")
        return False

def print_student_profiles():
    """
    Prints all student profiles in the database.
    """
    db = next(get_db())
    students = db.query(StudentProfileDB).all()
    if not students:
        print("No student profiles found in the database.")
        return
    
    print(f"Found {len(students)} student profiles:")
    for student in students:
        print(f"\nID: {student.id}")
        print(f"Name: {student.name}")
        print(f"Grade Level: {student.grade_level if student.grade_level else 'Not specified'}")
        print(f"Template: {student.template_name if student.template_name else 'Custom'}")
        
        if student.personality_traits:
            print(f"Personality Traits: {', '.join(student.personality_traits)}")
        
        if student.typical_moods:
            print(f"Typical Moods: {', '.join(student.typical_moods)}")
        
        if student.behavioral_patterns:
            try:
                behavioral_patterns = json.loads(student.behavioral_patterns)
                print(f"Behavioral Patterns: {behavioral_patterns}")
            except json.JSONDecodeError:
                print(f"Behavioral Patterns: {student.behavioral_patterns}")
        
        if student.learning_style:
            print(f"Learning Style: {student.learning_style}")
        
        if student.interests:
            print(f"Interests: {', '.join(student.interests)}")
        
        if student.academic_strengths:
            print(f"Academic Strengths: {', '.join(student.academic_strengths)}")
        
        if student.academic_challenges:
            print(f"Academic Challenges: {', '.join(student.academic_challenges)}")
        
        if student.support_strategies:
            print(f"Support Strategies: {', '.join(student.support_strategies)}")
        
        if student.social_dynamics:
            try:
                social_dynamics = json.loads(student.social_dynamics)
                print(f"Social Dynamics: {social_dynamics}")
            except json.JSONDecodeError:
                print(f"Social Dynamics: {student.social_dynamics}")
        
        print("-" * 40)

def print_teacher_profiles():
    """
    Prints the contents of the teacher_profiles table.
    """
    db = next(get_db())
    teachers = db.query(TeacherProfile).all()
    print("\nteacher_profiles table contents:")
    for teacher in teachers:
        print(f"  ID: {teacher.id}")
        print(f"  Name: {teacher.name}")
        print(f"  Grade Level: {teacher.grade_level}")
        print(f"  Teaching Philosophy: {teacher.teaching_philosophy}")
        print(f"  Preferred Teaching Methods: {', '.join(teacher.preferred_teaching_methods) if teacher.preferred_teaching_methods else 'None'}")
        print(f"  Behavior Management Philosophy: {teacher.behavior_management_philosophy}")
        print(f"  Areas for Growth: {', '.join(teacher.areas_for_growth) if teacher.areas_for_growth else 'None'}")
        print("-" * 20)  # Separator between teachers

def print_scenarios():
    """
    Prints the contents of the scenarios table.
    """
    db = next(get_db())
    scenarios = db.query(Scenario).all()
    print("\nscenarios table contents:")
    for scenario in scenarios:
        print(f"  ID: {scenario.id}")
        print(f"  Title: {scenario.title}")
        print(f"  Description: {scenario.description}")
        print(f"  Instruction: {scenario.instruction[:100]}..." if scenario.instruction and len(scenario.instruction) > 100 else f"  Instruction: {scenario.instruction}")
        print("-" * 20)  # Separator between scenarios

def print_all_tables():
    """
    Prints the contents of all tables in the database.
    """
    print_student_profiles()
    print_teacher_profiles()
    print_scenarios()

def populate_scenarios():
    """
    Populates the scenarios table with predefined scenario data.
    """
    db = next(get_db())
    try:
        scenarios = [
            {
                "title": "First Day Jitters",
                "description": "A new student is feeling anxious on their first day.",
                "instruction": """You are role-playing as the selected student on their first day of school. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - It's the first day of a new school year
   - You're meeting your new teacher and classmates
   - You're in an unfamiliar environment

2. Character Integration:
   - Stay true to the student's personality traits (e.g., if outgoing, show enthusiasm despite nerves)
   - Maintain the student's typical behavioral patterns
   - Reflect their learning style in how they process new information
   - Show their social dynamics in interactions
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate first-day emotions while staying true to character
   - Express concerns that align with the student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance scenario emotions with student's typical demeanor
   - Show vulnerability or confidence based on student profile
   - Express concerns about academic and social aspects
   - React to teacher reassurance in character-appropriate ways

5. Key Behaviors:
   - Adapt communication style to student's personality
   - Show interest in activities based on student's interests
   - Express concerns matching student's typical patterns
   - Demonstrate coping strategies from student's profile
   - Process instructions according to learning style

6. Sensitive Topics:
   - Handle separation anxiety based on student's profile
   - Address academic concerns matching student's challenges
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a first-day scenario, your primary goal is to stay true to the student's profile. Adapt the scenario's emotional elements to fit the student's personality, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Individual Math Session",
                "description": "A student is working one-on-one with their teacher on math concepts.",
                "instruction": """You are role-playing as the selected student during an individual math session. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're working one-on-one with your teacher
   - The focus is on addition and subtraction within 20
   - You're in a quiet, focused environment

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their learning style in problem-solving
   - Show their academic strengths and challenges
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate math session emotions while staying true to character
   - Express understanding or confusion based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance math confidence with student's typical demeanor
   - Show enthusiasm or anxiety based on student profile
   - Express mathematical thinking in character-appropriate ways
   - React to teacher guidance according to student's learning style

5. Key Behaviors:
   - Adapt problem-solving approach to student's learning style
   - Show engagement based on student's interests
   - Express mathematical understanding or confusion
   - Demonstrate use of support strategies when needed
   - Process teacher feedback according to learning style

6. Sensitive Topics:
   - Handle math anxiety based on student's profile
   - Address learning challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a math session, your primary goal is to stay true to the student's profile. Adapt the mathematical elements to fit the student's personality and learning style, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Individual Reading Session",
                "description": "A student is reading with their teacher in a one-on-one setting.",
                "instruction": """You are role-playing as the selected student during an individual reading session. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're reading one-on-one with your teacher
   - The focus is on reading comprehension and fluency
   - You're in a quiet, focused environment

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their learning style in reading
   - Show their academic strengths and challenges
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate reading session emotions while staying true to character
   - Express understanding or confusion based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance reading confidence with student's typical demeanor
   - Show enthusiasm or anxiety based on student profile
   - Express comprehension in character-appropriate ways
   - React to teacher guidance according to student's learning style

5. Key Behaviors:
   - Adapt reading approach to student's learning style
   - Show engagement based on student's interests
   - Express understanding or confusion
   - Demonstrate use of support strategies when needed
   - Process teacher feedback according to learning style

6. Sensitive Topics:
   - Handle reading anxiety based on student's profile
   - Address learning challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a reading session, your primary goal is to stay true to the student's profile. Adapt the reading elements to fit the student's personality and learning style, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Individual Science Session",
                "description": "A student is working on science concepts with their teacher.",
                "instruction": """You are role-playing as the selected student during an individual science session. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're working on science concepts with your teacher
   - The focus is on understanding basic scientific principles
   - You're in a quiet, focused environment

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their learning style in scientific thinking
   - Show their academic strengths and challenges
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate science session emotions while staying true to character
   - Express understanding or confusion based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance scientific curiosity with student's typical demeanor
   - Show enthusiasm or anxiety based on student profile
   - Express scientific thinking in character-appropriate ways
   - React to teacher guidance according to student's learning style

5. Key Behaviors:
   - Adapt scientific thinking to student's learning style
   - Show engagement based on student's interests
   - Express understanding or confusion
   - Demonstrate use of support strategies when needed
   - Process teacher feedback according to learning style

6. Sensitive Topics:
   - Handle science anxiety based on student's profile
   - Address learning challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a science session, your primary goal is to stay true to the student's profile. Adapt the scientific elements to fit the student's personality and learning style, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Peer Conflict",
                "description": "A student is experiencing a conflict with a classmate.",
                "instruction": """You are role-playing as the selected student during a peer conflict situation. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're experiencing a conflict with a classmate
   - The situation requires emotional regulation and problem-solving
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their social dynamics
   - Show their emotional regulation patterns
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate conflict resolution emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance emotional expression with student's typical demeanor
   - Show appropriate conflict resolution strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's social dynamics

5. Key Behaviors:
   - Adapt conflict resolution to student's personality
   - Show emotional regulation based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to social dynamics

6. Sensitive Topics:
   - Handle emotional responses based on student's profile
   - Address social challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a conflict situation, your primary goal is to stay true to the student's profile. Adapt the conflict resolution elements to fit the student's personality and social dynamics, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Transition Difficulty",
                "description": "A student is having trouble transitioning between activities.",
                "instruction": """You are role-playing as the selected student during a transition difficulty. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're having trouble transitioning between activities
   - The situation requires flexibility and adaptability
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their transition patterns
   - Show their emotional regulation
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate transition emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance transition flexibility with student's typical demeanor
   - Show appropriate transition strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's transition patterns

5. Key Behaviors:
   - Adapt transition strategies to student's personality
   - Show emotional regulation based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to transition patterns

6. Sensitive Topics:
   - Handle emotional responses based on student's profile
   - Address transition challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a transition situation, your primary goal is to stay true to the student's profile. Adapt the transition elements to fit the student's personality and behavioral patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Group Work Challenge",
                "description": "A student is struggling with group work activities.",
                "instruction": """You are role-playing as the selected student during a group work challenge. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're participating in a group work activity
   - The situation requires collaboration and communication
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their social dynamics
   - Show their group work patterns
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate group work emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance group participation with student's typical demeanor
   - Show appropriate collaboration strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's social dynamics

5. Key Behaviors:
   - Adapt group work strategies to student's personality
   - Show social interaction based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to social dynamics

6. Sensitive Topics:
   - Handle social responses based on student's profile
   - Address group work challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a group work situation, your primary goal is to stay true to the student's profile. Adapt the group work elements to fit the student's personality and social dynamics, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Test Anxiety",
                "description": "A student is experiencing anxiety before a test.",
                "instruction": """You are role-playing as the selected student experiencing test anxiety. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're preparing for a test
   - The situation requires emotional regulation and coping strategies
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their anxiety patterns
   - Show their coping strategies
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate test anxiety emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance anxiety management with student's typical demeanor
   - Show appropriate coping strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's anxiety patterns

5. Key Behaviors:
   - Adapt anxiety management to student's personality
   - Show emotional regulation based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to anxiety patterns

6. Sensitive Topics:
   - Handle emotional responses based on student's profile
   - Address anxiety challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is an anxiety situation, your primary goal is to stay true to the student's profile. Adapt the anxiety management elements to fit the student's personality and emotional patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Attention Difficulty",
                "description": "A student is having trouble maintaining attention during class.",
                "instruction": """You are role-playing as the selected student experiencing attention difficulties. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're having trouble maintaining attention
   - The situation requires focus and self-regulation
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their attention patterns
   - Show their self-regulation strategies
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate attention difficulty emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance attention management with student's typical demeanor
   - Show appropriate self-regulation strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's attention patterns

5. Key Behaviors:
   - Adapt attention management to student's personality
   - Show self-regulation based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to attention patterns

6. Sensitive Topics:
   - Handle behavioral responses based on student's profile
   - Address attention challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is an attention difficulty situation, your primary goal is to stay true to the student's profile. Adapt the attention management elements to fit the student's personality and behavioral patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Social Inclusion",
                "description": "A student is having trouble being included in social activities.",
                "instruction": """You are role-playing as the selected student experiencing social inclusion challenges. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're having trouble being included in social activities
   - The situation requires social skills and self-advocacy
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their social dynamics
   - Show their self-advocacy skills
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate social inclusion emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance social inclusion with student's typical demeanor
   - Show appropriate self-advocacy strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's social dynamics

5. Key Behaviors:
   - Adapt social inclusion strategies to student's personality
   - Show self-advocacy based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to social dynamics

6. Sensitive Topics:
   - Handle social responses based on student's profile
   - Address inclusion challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a social inclusion situation, your primary goal is to stay true to the student's profile. Adapt the social inclusion elements to fit the student's personality and social dynamics, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Homework Struggle",
                "description": "A student is having trouble completing homework assignments.",
                "instruction": """You are role-playing as the selected student experiencing homework struggles. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're having trouble completing homework
   - The situation requires organization and time management
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their homework patterns
   - Show their organization skills
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate homework struggle emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance homework management with student's typical demeanor
   - Show appropriate organization strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's homework patterns

5. Key Behaviors:
   - Adapt homework management to student's personality
   - Show organization based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to homework patterns

6. Sensitive Topics:
   - Handle academic responses based on student's profile
   - Address homework challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a homework struggle situation, your primary goal is to stay true to the student's profile. Adapt the homework management elements to fit the student's personality and academic patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Emotional Outburst",
                "description": "A student is experiencing an emotional outburst in class.",
                "instruction": """You are role-playing as the selected student experiencing an emotional outburst. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're experiencing an emotional outburst
   - The situation requires emotional regulation and coping strategies
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their emotional patterns
   - Show their coping strategies
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate emotional outburst emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance emotional regulation with student's typical demeanor
   - Show appropriate coping strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's emotional patterns

5. Key Behaviors:
   - Adapt emotional regulation to student's personality
   - Show coping strategies based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to emotional patterns

6. Sensitive Topics:
   - Handle emotional responses based on student's profile
   - Address outburst challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is an emotional outburst situation, your primary goal is to stay true to the student's profile. Adapt the emotional regulation elements to fit the student's personality and emotional patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Learning Frustration",
                "description": "A student is becoming frustrated with a learning task.",
                "instruction": """You are role-playing as the selected student experiencing learning frustration. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You're becoming frustrated with a learning task
   - The situation requires perseverance and problem-solving
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their learning patterns
   - Show their problem-solving strategies
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate learning frustration emotions while staying true to character
   - Express feelings based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance frustration management with student's typical demeanor
   - Show appropriate problem-solving strategies
   - Express feelings in character-appropriate ways
   - React to teacher guidance according to student's learning patterns

5. Key Behaviors:
   - Adapt frustration management to student's personality
   - Show problem-solving based on student's profile
   - Express feelings appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to learning patterns

6. Sensitive Topics:
   - Handle academic responses based on student's profile
   - Address frustration challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a learning frustration situation, your primary goal is to stay true to the student's profile. Adapt the frustration management elements to fit the student's personality and learning patterns, rather than letting the scenario override the student's core characteristics."""
            },
            {
                "title": "Self-Advocacy",
                "description": "A student needs to advocate for their learning needs.",
                "instruction": """You are role-playing as the selected student learning to self-advocate. Your responses should primarily reflect the student's profile characteristics while incorporating these scenario-specific elements:

1. Context:
   - You need to advocate for your learning needs
   - The situation requires communication and self-awareness
   - You're in a classroom setting

2. Character Integration:
   - Stay true to the student's personality traits
   - Maintain their typical behavioral patterns
   - Reflect their communication style
   - Show their self-awareness
   - Use their support strategies when needed

3. Scenario-Specific Elements:
   - Show appropriate self-advocacy emotions while staying true to character
   - Express needs based on student's profile
   - Demonstrate behaviors that blend scenario needs with student traits
   - Use language and responses appropriate for the student's personality

4. Response Guidelines:
   - Keep responses age-appropriate (2nd grade level)
   - Balance self-advocacy with student's typical demeanor
   - Show appropriate communication strategies
   - Express needs in character-appropriate ways
   - React to teacher guidance according to student's communication style

5. Key Behaviors:
   - Adapt self-advocacy to student's personality
   - Show communication based on student's profile
   - Express needs appropriately
   - Demonstrate use of support strategies when needed
   - Process teacher guidance according to communication style

6. Sensitive Topics:
   - Handle communication responses based on student's profile
   - Address self-advocacy challenges appropriately
   - Be mindful of student-specific triggers
   - Maintain appropriate boundaries
   - Use student's support strategies when needed

Remember: While this is a self-advocacy situation, your primary goal is to stay true to the student's profile. Adapt the self-advocacy elements to fit the student's personality and communication style, rather than letting the scenario override the student's core characteristics."""
            }
        ]

        for scenario_data in scenarios:
            scenario = Scenario(**scenario_data)
            db.add(scenario)

        db.commit()
        print("Scenarios populated successfully.")
        return True
    except IntegrityError:
        db.rollback()
        print("Some scenarios already exist in the database.")
        return False
    except Exception as e:
        db.rollback()
        print(f"Error populating scenarios: {e}")
        return False

def populate_active_files():
    """
    Populates the active_files table with markdown files from the data/markdown_files directory.
    """
    db = next(get_db())
    try:
        # Define the root directory of your project
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

        # Construct the path to the markdown files
        markdown_files_dir = os.path.join(project_root, "data", "markdown_files")

        print(f"Searching for markdown files in: {markdown_files_dir}")

        # Check if directory exists
        if not os.path.exists(markdown_files_dir):
            print(f"Error: Directory not found: {markdown_files_dir}")
            return False

        # Get list of markdown files
        markdown_files = [f for f in os.listdir(markdown_files_dir) if f.endswith('.md')]

        if not markdown_files:
            print("No markdown files found in the directory.")
            return False

        print(f"Found {len(markdown_files)} markdown files.")

        # Add each file to the database
        for filename in markdown_files:
            filepath = os.path.join(markdown_files_dir, filename)
            try:
                with open(filepath, "rb") as f:
                    file_content = f.read()

                # Try to create the file in the database
                result = create_active_file(name=filename, file_content=file_content)
                if result:
                    print(f"Successfully added {filename} to the database.")
                else:
                    print(f"Failed to add {filename} to the database.")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

        db.commit()
        print("Active files populated successfully.")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error populating active files: {e}")
        return False

def populate_teacher_profiles():
    """
    Populates the teacher_profiles table with predefined teacher data.
    """
    db = next(get_db())
    try:
        # Jane Doe
        jane = TeacherProfile(
            name="Jane Doe",
            grade_level=2,
            teaching_philosophy="Hands-on learning with focus on real-world applications",
            preferred_teaching_methods=["experiential", "cooperative learning"],
            behavior_management_philosophy="Building relationships and setting clear boundaries",
            areas_for_growth=["assessment strategies", "parent communication"]
        )
        db.add(jane)

        # John Smith
        john = TeacherProfile(
            name="John Smith",
            grade_level=2,
            teaching_philosophy="Student-centered learning with emphasis on critical thinking",
            preferred_teaching_methods=["project-based", "inquiry-based"],
            behavior_management_philosophy="Positive reinforcement and clear expectations",
            areas_for_growth=["technology integration", "differentiated instruction"]
        )
        db.add(john)

        # Sarah Johnson
        sarah = TeacherProfile(
            name="Sarah Johnson",
            grade_level=2,
            teaching_philosophy="Inclusive education with focus on individual learning styles",
            preferred_teaching_methods=["differentiated instruction", "flipped classroom"],
            behavior_management_philosophy="Proactive approach with emphasis on social-emotional learning",
            areas_for_growth=["data-driven instruction", "classroom technology"]
        )
        db.add(sarah)

        db.commit()
        print("Teacher profiles populated successfully.")
        return True
    except IntegrityError:
        db.rollback()
        print("Some teacher profiles already exist in the database.")
        return False
    except Exception as e:
        db.rollback()
        print(f"Error populating teacher profiles: {e}")
        return False

def populate_all_tables() -> bool:
    """
    Populates all tables in the database with example data.
    This function should be called after initialize_database().
    
    Returns:
        bool: True if all tables were populated successfully, False otherwise.
    """
    print("Starting database population...")
    
    success = True
    success &= populate_student_profiles()
    success &= populate_scenarios()
    success &= populate_active_files()
    success &= populate_teacher_profiles()
    
    if success:
        print("All tables populated successfully.")
    else:
        print("Some tables may not have been populated correctly.")
    
    return success

# Student CRUD Functions

def get_student_by_id(id: int) -> StudentProfileDB:
    """
    Retrieves a student profile from the database by their id.
    
    Args:
        id (int): Id of the student to retrieve.
        
    Returns:
        StudentProfileDB: The StudentProfileDB object if found, None otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfileDB).filter(StudentProfileDB.id == id).first()
    return student

def get_student_by_name(name: str) -> StudentProfileDB:
    """
    Retrieves a student profile from the database by their name.
    
    Args:
        name (str): The name of the student to retrieve.
        
    Returns:
        StudentProfileDB: The StudentProfileDB object if found, None otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfileDB).filter(StudentProfileDB.name == name).first()
    return student

def get_student_object_by_id(id: int) -> StudentProfile:
    """
    Retrieves a student profile from the database and converts it to a StudentProfile object.
    
    Args:
        id (int): ID of the student to retrieve
        
    Returns:
        StudentProfile: The student profile as a StudentProfile object
    """
    db = next(get_db())
    try:
        db_student = db.query(StudentProfileDB).filter(StudentProfileDB.id == id).first()
        if not db_student:
            return None
            
        # Convert to student profile object
        return db_to_student_object(db_student)
    except Exception as e:
        print(f"Error retrieving student profile object: {e}")
        return None

def get_student_object_by_name(name: str) -> StudentProfile:
    """
    Retrieves a student profile from the database and converts it to a StudentProfile object.
    
    Args:
        name (str): name of the student to retrieve
        
    Returns:
        StudentProfile: The student profile as a StudentProfile object
    """
    db = next(get_db())
    try:
        db_student = db.query(StudentProfileDB).filter(StudentProfileDB.name == name).first()
        if not db_student:
            return None
            
        # Convert to student profile object
        return db_to_student_object(db_student)
    except Exception as e:
        print(f"Error retrieving student profile object: {e}")
        return None

def db_to_student_object(db_student: StudentProfileDB) -> StudentProfile:
    """
    Converts a database student profile to a StudentProfile object.
    
    Args:
        db_student (StudentProfileDB): The database student profile to convert
        
    Returns:
        StudentProfile: The StudentProfile object
    """
    try:
        # Convert JSON strings back to dictionaries
        behavioral_patterns = json.loads(db_student.behavioral_patterns) if db_student.behavioral_patterns else {}
        social_dynamics = json.loads(db_student.social_dynamics) if db_student.social_dynamics else {}
        
        # Convert string interests to Interest enums, validating against available values
        interests = []
        if db_student.interests:
            for interest_str in db_student.interests:
                # Try to find a matching enum value
                try:
                    interests.append(Interest(interest_str))
                except ValueError:
                    # If no exact match, find the closest match
                    for interest_enum in Interest:
                        if interest_str.lower() == interest_enum.value.lower():
                            interests.append(interest_enum)
                            break
        
        # Convert string moods to Mood enums, with fallback mapping
        moods = []
        mood_mapping = {
            "calm": Mood.HAPPY,
            "focused": Mood.FOCUSED,
            "enthusiastic": Mood.EXCITED,
            "restless": Mood.DISTRACTED,
            "thoughtful": Mood.FOCUSED,
            "anxious": Mood.ANXIOUS
        }
        
        if db_student.typical_moods:
            for mood_str in db_student.typical_moods:
                try:
                    # Try direct match
                    moods.append(Mood(mood_str))
                except ValueError:
                    # Try mapping
                    if mood_str.lower() in mood_mapping:
                        moods.append(mood_mapping[mood_str.lower()])
                    else:
                        # Default to FOCUSED if no match
                        moods.append(Mood.FOCUSED)
        
        # Use teammate's create_student_profile function
        if db_student.template_name:
            # If we have a template, use it
            return create_custom_profile(
                template_name=db_student.template_name,
                name=db_student.name,
                grade_level=db_student.grade_level,
                interests=interests,
                academic_strengths=db_student.academic_strengths,
                academic_challenges=db_student.academic_challenges,
                support_strategies=db_student.support_strategies
            )
        else:
            # Create from scratch if no template
            student_object = StudentProfile(
                name=db_student.name,
                grade_level=db_student.grade_level,
                personality_traits=db_student.personality_traits,
                typical_moods=moods,
                behavioral_patterns=behavioral_patterns,
                learning_style=db_student.learning_style,
                interests=interests,
                academic_strengths=db_student.academic_strengths,
                academic_challenges=db_student.academic_challenges,
                support_strategies=db_student.support_strategies,
                social_dynamics=social_dynamics
            )
            return student_object
    except Exception as e:
        print(f"Error converting DB student to StudentProfile object: {e}")
        return None

def create_student_profile(
    name: str,
    grade_level: int = None,
    personality_traits: list = None,
    typical_moods: list = None,
    behavioral_patterns: dict = None,
    learning_style: str = None,
    interests: list = None,
    academic_strengths: list = None,
    academic_challenges: list = None,
    support_strategies: list = None,
    social_dynamics: dict = None,
    template_name: str = None
) -> StudentProfileDB:
    """
    Creates a new student profile in the database.
    
    Args:
        name (str): The student's name
        grade_level (int, optional): The student's grade level
        personality_traits (list, optional): List of personality traits
        typical_moods (list, optional): List of typical moods
        behavioral_patterns (dict, optional): Dictionary of behavioral patterns
        learning_style (str, optional): The student's learning style
        interests (list, optional): List of interests
        academic_strengths (list, optional): List of academic strengths
        academic_challenges (list, optional): List of academic challenges
        support_strategies (list, optional): List of support strategies
        social_dynamics (dict, optional): Dictionary of social dynamics
        template_name (str, optional): Name of the template used to create this profile
        
    Returns:
        StudentProfileDB: The created database student profile
    """
    db = next(get_db())
    try:
        # Convert dictionaries to JSON strings for storage
        behavioral_patterns_json = json.dumps(behavioral_patterns) if behavioral_patterns else None
        social_dynamics_json = json.dumps(social_dynamics) if social_dynamics else None
        
        # Create the database student profile
        student = StudentProfileDB(
            name=name,
            grade_level=grade_level,
            personality_traits=personality_traits,
            typical_moods=typical_moods,
            behavioral_patterns=behavioral_patterns_json,
            learning_style=learning_style,
            interests=interests,
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            support_strategies=support_strategies,
            social_dynamics=social_dynamics_json,
            template_name=template_name
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
        db.rollback()
        print(f"Error creating student profile: {e}")
        return None

def create_student_profile_from_object(student_profile: StudentProfile) -> StudentProfileDB:
    """
    Creates a database student profile from a StudentProfile object.
    
    Args:
        student_profile (StudentProfile): The StudentProfile object to store
        
    Returns:
        StudentProfileDB: The created database student profile
    """
    try:
        # Convert Interest enums to string values
        interests = [interest.value for interest in student_profile.interests] if student_profile.interests else []
        
        # Convert Mood enums to string values
        moods = [mood.value for mood in student_profile.typical_moods] if student_profile.typical_moods else []
        
        # Attempt to get template_name
        template_name = getattr(student_profile, 'template_name', None)
        
        return create_student_profile(
            name=student_profile.name,
            grade_level=student_profile.grade_level,
            personality_traits=student_profile.personality_traits,
            typical_moods=moods,
            behavioral_patterns=student_profile.behavioral_patterns,
            learning_style=student_profile.learning_style,
            interests=interests,
            academic_strengths=student_profile.academic_strengths,
            academic_challenges=student_profile.academic_challenges,
            support_strategies=student_profile.support_strategies,
            social_dynamics=student_profile.social_dynamics,
            template_name=template_name
        )
    except Exception as e:
        print(f"Error creating student profile from object: {e}")
        return None

def get_all_students() -> List[StudentProfileDB]:
    """
    Retrieves all student profiles from the database.

    Returns:
        list: A list of StudentProfileDB objects.
    """
    db = next(get_db())
    students = db.query(StudentProfileDB).all()
    return students

def create_student(
    name: str, 
    grade_level: int, 
    personality_traits: list = None, 
    typical_moods: list = None, 
    behavioral_patterns: dict = None, 
    learning_style: str = None, 
    interests: list = None, 
    academic_strengths: list = None, 
    academic_challenges: list = None, 
    support_strategies: list = None, 
    social_dynamics: dict = None
) -> StudentProfileDB:
    """
    Creates a new student profile in the database.

    Args:
        name (str): The name of the student.
        grade_level (int): The grade level of the student.
        personality_traits (list, optional): A list of personality traits. Defaults to None.
        typical_moods (list, optional): A list of typical moods. Defaults to None.
        behavioral_patterns (dict, optional): A dictionary of behavioral patterns. Defaults to None.
        learning_style (str, optional): The student's learning style. Defaults to None.
        interests (list, optional): A list of interests. Defaults to None.
        academic_strengths (list, optional): A list of academic strengths. Defaults to None.
        academic_challenges (list, optional): A list of academic challenges. Defaults to None.
        support_strategies (list, optional): A list of support strategies. Defaults to None.
        social_dynamics (dict, optional): A dictionary of social dynamics. Defaults to None.

    Returns:
        StudentProfileDB: The created StudentProfileDB object, or None if creation failed.
    """
    db = next(get_db())
    try:
        # Convert dictionaries to JSON strings for storage
        behavioral_patterns_json = json.dumps(behavioral_patterns) if behavioral_patterns else None
        social_dynamics_json = json.dumps(social_dynamics) if social_dynamics else None
        
        student = StudentProfileDB(
            name=name,
            grade_level=grade_level,
            personality_traits=personality_traits,
            typical_moods=typical_moods,
            behavioral_patterns=behavioral_patterns_json,
            learning_style=learning_style,
            interests=interests,
            academic_strengths=academic_strengths,
            academic_challenges=academic_challenges,
            support_strategies=support_strategies,
            social_dynamics=social_dynamics_json
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except IntegrityError:
        db.rollback()
        return None

def update_student(student_id: int, **kwargs) -> StudentProfileDB:
    """
    Updates an existing student profile in the database.

    Args:
        student_id (int): The ID of the student to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.

    Returns:
        StudentProfileDB: The updated StudentProfileDB object, or None if the update failed.
    """
    db = next(get_db())
    student = db.query(StudentProfileDB).filter(StudentProfileDB.id == student_id).first()
    if student:
        for key, value in kwargs.items():
            setattr(student, key, value)
        db.commit()
        return student
    return None

def delete_student_by_id(student_id: int) -> bool:
    """
    Deletes a student profile from the database.

    Args:
        student_id (int): The ID of the student to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfileDB).filter(StudentProfileDB.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

def delete_student_by_name(student_name: str) -> bool:
    """
    Deletes a student profile from the database.

    Args:
        student_name (str): The name of the student to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    student = db.query(StudentProfileDB).filter(StudentProfileDB.name == student_name).first()
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

def clear_student_profiles() -> bool:
    """
    Clears all records from the student_profiles table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(StudentProfileDB).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing student profiles: {e}")
        return False

# Scenario CRUD Functions

def get_scenario_by_title(title: str) -> Scenario:
    """
    Retrieves a scenario from the database by its title.

    Args:
        title (str): The title of the scenario to retrieve.

    Returns:
        Scenario: The Scenario object if found, None otherwise.
    """
    db = next(get_db())
    scenario = db.query(Scenario).filter(Scenario.title == title).first()
    return scenario

def get_all_scenarios() -> List[Scenario]:
    """
    Retrieves all scenarios from the database.

    Returns:
        list: A list of Scenario objects.
    """
    db = next(get_db())
    scenarios = db.query(Scenario).all()
    return scenarios

def create_scenario(title: str, description: str, instruction: str = None) -> Scenario:
    """
    Creates a new scenario in the database.

    Args:
        title (str): The title of the scenario.
        description (str): The description of the scenario.
        instruction (str, optional): The AI instruction/prompt for role-playing the scenario.

    Returns:
        Scenario: The created Scenario object, or None if creation failed.
    """
    db = next(get_db())
    try:
        scenario = Scenario(title=title, description=description, instruction=instruction)
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario
    except Exception as e:
        db.rollback()
        print(f"Error creating scenario: {e}")
        return None

def update_scenario(scenario_id: int, **kwargs) -> Scenario:
    """
    Updates an existing scenario in the database.

    Args:
        scenario_id (int): The ID of the scenario to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.
                 Can include: title, description, instruction.

    Returns:
        Scenario: The updated Scenario object, or None if the update failed.
    """
    db = next(get_db())
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario:
        valid_fields = {'title', 'description', 'instruction'}
        for key, value in kwargs.items():
            if key in valid_fields:
                setattr(scenario, key, value)
            else:
                print(f"Warning: Invalid field '{key}' for scenario update")
        db.commit()
        return scenario
    return None

def delete_scenario(scenario_id: int) -> bool:
    """
    Deletes a scenario from the database.

    Args:
        scenario_id (int): The ID of the scenario to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if scenario:
            db.delete(scenario)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting scenario: {e}")
        return False

def clear_scenarios() -> bool:
    """
    Clears all records from the scenarios table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(Scenario).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing scenarios: {e}")
        return False

# Dialogue CRUD functions

def get_dialogue_by_id(dialogue_id: int) -> Dialogue:
    """
    Retrieves a dialogue from the database by its ID.

    Args:
        dialogue_id (int): The ID of the dialogue to retrieve.

    Returns:
        Dialogue: The Dialogue object if found, None otherwise.
    """
    db = next(get_db())
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    return dialogue

def get_dialogues_by_scenario(scenario_id: int) -> List[Dialogue]:
    """
    Retrieves all dialogues for a given scenario ID.

    Args:
        scenario_id (int): The ID of the scenario.

    Returns:
        list: A list of Dialogue objects associated with the scenario.
    """
    db = next(get_db())
    dialogues = db.query(Dialogue).filter(Dialogue.scenario_id == scenario_id).all()
    return dialogues

def create_dialogue(scenario_id: int, student_name: str, utterance: str) -> Dialogue:
    """
    Creates a new dialogue in the database.

    Args:
        scenario_id (int): The ID of the scenario this dialogue belongs to.
        student_name (str): The name of the student speaking.
        utterance (str): The actual dialogue utterance.

    Returns:
        Dialogue: The created Dialogue object, or None if creation failed.
    """
    db = next(get_db())
    try:
        dialogue = Dialogue(scenario_id=scenario_id, student_name=student_name, utterance=utterance)
        db.add(dialogue)
        db.commit()
        db.refresh(dialogue)
        return dialogue
    except Exception as e:
        db.rollback()
        print(f"Error creating dialogue: {e}")
        return None

def update_dialogue(dialogue_id: int, **kwargs) -> Dialogue:
    """
    Updates an existing dialogue in the database.

    Args:
        dialogue_id (int): The ID of the dialogue to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.

    Returns:
        Dialogue: The updated Dialogue object, or None if the update failed.
    """
    db = next(get_db())
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if dialogue:
        for key, value in kwargs.items():
            setattr(dialogue, key, value)
        db.commit()
        return dialogue
    return None

def delete_dialogue(dialogue_id: int) -> bool:
    """
    Deletes a dialogue from the database.

    Args:
        dialogue_id (int): The ID of the dialogue to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
        if dialogue:
            db.delete(dialogue)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting dialogue: {e}")
        return False
    
def get_dialogues_by_student_and_scenario(student_name: str, scenario_title: str) -> List[Dialogue]:
    """
    Retrieves dialogues for a specific student in a specific scenario.

    Args:
        student_name (str): The name of the student.
        scenario_title (str): The title of the scenario.

    Returns:
        list: A list of Dialogue objects matching the criteria.
    """
    db = next(get_db())
    dialogues = db.query(Dialogue).join(Scenario).filter(
        Dialogue.student_name == student_name,
        Scenario.title == scenario_title
    ).all()
    return dialogues

def clear_dialogues() -> bool:
    """
    Clears all records from the dialogues table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(Dialogue).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing dialogues: {e}")
        return False

# Active and Inactive Tables CRUD functions

def create_active_file(name: str, file_content: bytes) -> ActiveFile:
    """
    Creates a new active file entry in the database.

    Args:
        name (str): The name of the file.
        file_content (bytes): The content of the file as bytes.

    Returns:
        The created ActiveFile object, or None if creation failed.
    """
    db = next(get_db())
    try:
        active_file = ActiveFile(name=name, file_content=file_content)
        db.add(active_file)
        db.commit()
        print(f"File added to database: {name}")
        db.refresh(active_file)
        return active_file
    except Exception as e:
        db.rollback()
        print(f"Error creating active file: {e}")
        return None

def get_active_file_by_id(active_file_id: int) -> ActiveFile:
    """
    Retrieves an active file from the database by its ID.

    Args:
        active_file_id (int): The ID of the active file.

    Returns:
        The ActiveFile object if found, None otherwise.
    """
    db = next(get_db())
    active_file = db.query(ActiveFile).filter(ActiveFile.id == active_file_id).first()
    return active_file

def get_inactive_file_by_id(inactive_file_id: int) -> InactiveFile:
    """
    Retrieves an inactive file from the database by its ID.

    Args:
        inactive_file_id (int): The ID of the inactive file.

    Returns:
        The InactiveFile object if found, None otherwise.
    """
    db = next(get_db())
    inactive_file = db.query(InactiveFile).filter(InactiveFile.id == inactive_file_id).first()
    return inactive_file

def get_active_file_by_name(active_file_name: str) -> ActiveFile:
    """
    Retrieves an active file from the database by its name.

    Args:
        active_file_name (str): The name of the active file.

    Returns:
        The ActiveFile object if found, None otherwise.
    """
    db = next(get_db())
    active_file = db.query(ActiveFile).filter(ActiveFile.name == active_file_name).first()
    return active_file

def get_inactive_file_by_name(inactive_file_name: str) -> InactiveFile:
    """
    Retrieves an inactive file from the database by its name.

    Args:
        inactive_file_name (str): The name of the inactive file.

    Returns:
        The InactiveFile object if found, None otherwise.
    """
    db = next(get_db())
    inactive_file = db.query(InactiveFile).filter(InactiveFile.name == inactive_file_name).first()
    return inactive_file

def add_markdown_files():
    """
    Adds markdown files from the data/markdown_files directory to the active_files table.
    """
    db = next(get_db())

    # Define the root directory of your project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # Construct the path to the markdown files
    markdown_files_dir = os.path.join(project_root, "data", "markdown_files")

    print(f"Searching for markdown files in: {markdown_files_dir}")  # Debug print statement

    for filename in os.listdir(markdown_files_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(markdown_files_dir, filename)

            with open(filepath, "rb") as f:
                file_content = f.read()

            name = filename

            create_active_file(name=name, file_content=file_content)

def move_file_to_inactive_by_id(file_id: int) -> bool:
    """
    Moves a file from the active_files table to the inactive_files table.

    Args:
        file_id (int): The ID of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the active file
        active_file = db.query(ActiveFile).filter(ActiveFile.id == file_id).first()
        if not active_file:
            print(f"Active file with ID {file_id} not found.")
            return False

        # Create an inactive file with the same data
        inactive_file = InactiveFile(
            name=active_file.name,
            file_content=active_file.file_content
        )
        db.add(inactive_file)

        # Delete the active file
        db.delete(active_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to inactive: {e}")
        return False


def move_file_to_active_by_id(file_id: int) -> bool:
    """
    Moves a file from the inactive_files table to the active_files table.

    Args:
        file_id (int): The ID of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the inactive file
        inactive_file = db.query(InactiveFile).filter(InactiveFile.id == file_id).first()
        if not inactive_file:
            print(f"Inactive file with ID {file_id} not found.")
            return False

        # Create an active file with the same data
        active_file = ActiveFile(
            name=inactive_file.name,
            file_content=inactive_file.file_content
        )
        db.add(active_file)

        # Delete the inactive file
        db.delete(inactive_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to active: {e}")
        return False

def move_file_to_inactive_by_name(name: str) -> bool:
    """
    Moves a file from the active_files table to the inactive_files table by its name.

    Args:
        name (str): The name of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the active file by name
        active_file = db.query(ActiveFile).filter(ActiveFile.name == name).first()
        if not active_file:
            print(f"Active file with name {name} not found.")
            return False

        # Create an inactive file with the same data
        inactive_file = InactiveFile(
            name=active_file.name,
            file_content=active_file.file_content
        )
        db.add(inactive_file)

        # Delete the active file
        db.delete(active_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to inactive: {e}")
        return False


def move_file_to_active_by_name(name: str) -> bool:
    """
    Moves a file from the inactive_files table to the active_files table by its name.

    Args:
        name (str): The name of the file to move.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    db = next(get_db())
    try:
        # Get the inactive file by name
        inactive_file = db.query(InactiveFile).filter(InactiveFile.name == name).first()
        if not inactive_file:
            print(f"Inactive file with name {name} not found.")
            return False

        # Create an active file with the same data
        active_file = ActiveFile(
            name=inactive_file.name,
            file_content=inactive_file.file_content
        )
        db.add(active_file)

        # Delete the inactive file
        db.delete(inactive_file)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error moving file to active: {e}")
        return False

def clear_active_files() -> bool:
    """
    Clears all records from the active_files table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(ActiveFile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing active files: {e}")
        return False

def clear_inactive_files() -> bool:
    """
    Clears all records from the inactive_files table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(InactiveFile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing inactive files: {e}")
        return False

# Teacher CRUD Functions

def get_teacher_by_id(teacher_id: int) -> TeacherProfile:
    """
    Retrieves a teacher profile from the database by their id.

    Args:
        teacher_id (int): Id of the teacher to retrieve.

    Returns:
        TeacherProfile: The TeacherProfile object if found, None otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
        return teacher
    except Exception as e:
        print(f"Error retrieving teacher by ID: {e}")
        return None

def get_teacher_by_name(name: str) -> TeacherProfile:
    """
    Retrieves a teacher profile from the database by their name.

    Args:
        name (str): The name of the teacher to retrieve.

    Returns:
        TeacherProfile: The TeacherProfile object if found, None otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.name == name).first()
        return teacher
    except Exception as e:
        print(f"Error retrieving teacher by name: {e}")
        return None

def get_all_teachers() -> List[TeacherProfile]:
    """
    Retrieves all teacher profiles from the database.

    Returns:
        list: A list of TeacherProfile objects.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving all teachers: {e}")
        return []

def create_teacher(
    name: str,
    grade_level: int,
    teaching_philosophy: str,
    preferred_teaching_methods: List[str] = None,
    behavior_management_philosophy: str = None,
    areas_for_growth: List[str] = None
) -> Optional[TeacherProfile]:
    """
    Creates a new teacher profile in the database.

    Args:
        name (str): The name of the teacher
        grade_level (int): The grade level the teacher teaches
        teaching_philosophy (str): The teacher's teaching philosophy
        preferred_teaching_methods (List[str], optional): List of preferred teaching methods
        behavior_management_philosophy (str, optional): The teacher's behavior management philosophy
        areas_for_growth (List[str], optional): List of areas for growth

    Returns:
        Optional[TeacherProfile]: The created teacher profile or None if creation fails
    """
    db = next(get_db())
    try:
        teacher = TeacherProfile(
            name=name,
            grade_level=grade_level,
            teaching_philosophy=teaching_philosophy,
            preferred_teaching_methods=preferred_teaching_methods,
            behavior_management_philosophy=behavior_management_philosophy,
            areas_for_growth=areas_for_growth
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        return teacher
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating teacher: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"Unexpected error creating teacher: {e}")
        return None

def update_teacher(teacher_id: int, **kwargs) -> bool:
    """
    Updates a teacher's profile in the database.

    Args:
        teacher_id (int): The ID of the teacher to update
        **kwargs: Fields to update (name, grade_level, teaching_philosophy, etc.)

    Returns:
        bool: True if update was successful, False otherwise
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter_by(id=teacher_id).first()
        if not teacher:
            print(f"Teacher with ID {teacher_id} not found")
            return False

        for key, value in kwargs.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)
            else:
                print(f"Invalid field: {key}")
                return False

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating teacher: {e}")
        return False

def delete_teacher_by_id(teacher_id: int) -> bool:
    """
    Deletes a teacher profile from the database by ID.

    Args:
        teacher_id (int): The ID of the teacher to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
        if teacher:
            db.delete(teacher)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting teacher by ID: {e}")
        return False

def delete_teacher_by_name(name: str) -> bool:
    """
    Deletes a teacher profile from the database by name.

    Args:
        name (str): The name of the teacher to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    db = next(get_db())
    try:
        teacher = db.query(TeacherProfile).filter(TeacherProfile.name == name).first()
        if teacher:
            db.delete(teacher)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting teacher by name: {e}")
        return False

def get_teachers_by_teaching_method(method: str) -> List[TeacherProfile]:
    """
    Retrieves all teachers who use a specific teaching method.

    Args:
        method (str): The teaching method to search for.

    Returns:
        list: A list of TeacherProfile objects that use the specified teaching method.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter(TeacherProfile.preferred_teaching_methods.contains([method])).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by teaching method: {e}")
        return []

def get_teachers_by_area_for_growth(area: str) -> List[TeacherProfile]:
    """
    Retrieves all teachers who have a specific area for growth.

    Args:
        area (str): The area for growth to search for.

    Returns:
        list: A list of TeacherProfile objects that have the specified area for growth.
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter(TeacherProfile.areas_for_growth.contains([area])).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by area for growth: {e}")
        return []

def get_teachers_by_grade_level(grade_level: int) -> List[TeacherProfile]:
    """
    Retrieves all teachers teaching at a specific grade level.

    Args:
        grade_level (int): The grade level to filter by

    Returns:
        List[TeacherProfile]: List of teachers at the specified grade level
    """
    db = next(get_db())
    try:
        teachers = db.query(TeacherProfile).filter_by(grade_level=grade_level).all()
        return teachers
    except Exception as e:
        print(f"Error retrieving teachers by grade level: {e}")
        return []

def clear_teacher_profiles() -> bool:
    """
    Clears all records from the teacher_profiles table.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    db = next(get_db())
    try:
        db.query(TeacherProfile).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing teacher profiles: {e}")
        return False

# Table Management Functions

def clear_all_tables() -> bool:
    """
    Clears all records from all tables in the database.
    Tables are cleared in a specific order to handle foreign key constraints.

    Returns:
        bool: True if all tables were cleared successfully, False otherwise.
    """
    try:
        # Clear tables in order of dependencies
        clear_dialogues()  # Clear first due to foreign key constraints
        clear_scenarios()
        clear_student_profiles()
        clear_teacher_profiles()
        clear_active_files()
        clear_inactive_files()
        return True
    except Exception as e:
        print(f"Error clearing all tables: {e}")
        return False

