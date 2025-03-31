# Classroom Management Knowledge Base

This feature adds a knowledge base retrieval capability specifically focused on classroom management strategies and techniques to help teachers respond effectively to different classroom situations.

## Features

1. **Active Knowledge Base Retrieval**: Teachers can request classroom management advice during conversations by using trigger phrases like "classroom management", "what should I do", or "help me with".

2. **Automatic Suggestion**: The system automatically identifies challenging student responses and suggests that the teacher ask for classroom management assistance.

3. **End-of-Conversation Evaluation with KB Context**: When the conversation ends, the evaluation process uses relevant classroom management best practices to assess the teacher's responses.

## How It Works

### 1. Building the Knowledge Base

The system uses a vector database to store and retrieve relevant classroom management content:

```python
# Load and index classroom management content
from src.ai.embedding import EmbeddingGenerator

embedder = EmbeddingGenerator()
embedder.construct_classroom_management_db()
```

### 2. Getting Help During Conversations

Teachers can get classroom management assistance in two ways:

- **Explicit Request**: Include phrases like "classroom management", "what should I do", or "help me with this" in your response to the student.

- **Suggested by System**: When the system detects a challenging student response, it will suggest that you might want to ask for classroom management help.

### 3. Result Integration

The knowledge base insights are presented in a structured format:

```
CLASSROOM MANAGEMENT INSIGHTS:
Query: handling student defiance

1. Key insight: Set clear expectations and consequences
2. Practical strategy: Use a calm, private discussion approach
3. Implementation: Acknowledge the student's feelings while maintaining expectations
```

## Available Knowledge Sources

The knowledge base includes content from several classroom management resources:

1. "Classroom Management That Works: Research-Based Strategies for Every Teacher"
2. "Effective Classroom Management: A Teacher's Guide"
3. "A Teacher's Guide to Successful Classroom Management and Differentiated Instruction"
4. "The Classroom Teacher's Behavior Management Toolbox"

## Example Usage

Example dialog with the system:

```
Student: I'm not doing this assignment. It's stupid and boring.

Tip: This may be a challenging classroom situation. Ask for classroom management help by including 'classroom management' or 'what should I do' in your response.

Teacher: What classroom management strategies would help me address this student resistance?

CLASSROOM MANAGEMENT INSIGHTS:
Query: addressing student resistance to assignments

1. Key insight: Student resistance often stems from feeling overwhelmed or seeing no purpose
2. Practical strategy: Connect the assignment to student interests and provide clear value
3. Implementation: Begin with validation, offer choices within the assignment structure, and break the task into smaller components

Teacher: I understand this assignment might seem boring at first. What part do you find most difficult? I can help break it down into smaller steps, or we could find a way to connect it to something you're interested in. What would make it more engaging for you?
```

## Development

To extend or customize the classroom management knowledge base:

1. Add new resources to the `data/books/` directory (PDFs are preferred)
2. Add markdown files with classroom management content to `data/collection/markdown_files/`
3. Run the `construct_classroom_management_db()` method to rebuild the vector database
