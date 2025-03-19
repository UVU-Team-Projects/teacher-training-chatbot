# Utah Elementary Teacher Training Assistant (UTAH-TTA)
## Second Grade Focus

A specialized LLM-powered educational chatbot designed for training elementary school teachers in Utah, with a specific focus on second-grade education. The system simulates authentic classroom scenarios to help teachers develop effective teaching strategies aligned with Utah's second-grade curriculum standards.

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Data Collection Focus](#-data-collection-focus)
- [Knowledge Base Structure](#knowledge-base-structure)
- [Repository Structure](#-repository-structure)
- [Team Roles](#-for-each-role)
- [Educational Content Specialist](#-educational-content-specialist)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Documentation](#-documentation)
- [Maintenance](#-maintenance)
- [Deployment](#-deployment)
## 🎯 Project Overview

UTAH-TTA Second Grade Edition provides:
- Second-grade specific classroom scenarios
- Alignment with Utah Core Standards for 2nd Grade
- Research-based teaching strategies for 7-8 year olds
- Age-appropriate classroom management techniques
- Progressive learning paths for second-grade teachers

## 📚 Data Collection Focus

## Knowledge Base Structure

Our data collection is organized into three main categories:

### 1. Second Grade Core Content (data/second_grade/)
- **Utah Core Standards**
  - Second Grade Math Standards
    - Numbers and Operations
    - Basic Algebra Concepts
    - Measurement and Data
    - Geometry
  - Second Grade Language Arts
    - Reading Comprehension
    - Writing Skills
    - Phonics and Word Recognition
    - Speaking and Listening
  - Second Grade Science
    - Earth and Space Systems
    - Physical Science
    - Life Science
    - Engineering Design

- **Teaching Methodologies**
  - Second Grade Teaching Strategies
  - Hands-on Learning Approaches
  - Inquiry-based Teaching
  - Collaborative Learning Strategies
  - Visual and Kinesthetic Methods
  - Age-Appropriate Assessment Methods
  - Differentiated Instruction for 7-8 Year Olds

### 2. Teacher-Student Interactions (data/interactions/)
- **Classroom Dialogues**
  - Second Grade Communication Patterns
  - Real-world examples
  - Best practice demonstrations
  - Common challenges
- **Behavior Management**
  - Age-Appropriate Management Techniques
  - Positive reinforcement examples
  - Conflict resolution scenarios
  - Group dynamics management

### 3. Teaching Scenarios (data/scenarios/)
- **Subject-Specific**
  - Second Grade Math Lessons
    - Addition and Subtraction with Regrouping
    - Introduction to Multiplication
    - Basic Fractions
  - Reading and Writing Activities
    - Reading Comprehension Strategies
    - Writing Complete Sentences
    - Basic Paragraph Structure
  - Science Experiments
    - Simple Machines
    - States of Matter
    - Plant Life Cycles
- **Classroom Management**
  - Transition periods
  - Group activities
  - Special events
- **Special Situations**
  - Learning difficulties
  - Behavioral challenges
  - Parent communication

## 📁 Repository Structure

```
teacher-training-chatbot/
├── src/                              # Source code
│   ├── ai/                           # AI/ML components
│   │   ├── embedding.py              # Embedding generation
│   │   ├── rag_pipeline.py           # RAG implementation
│   │   ├── llm_config.py            # LLM configuration
│   │   └── evaluation.py            # Response evaluation
│   │
│   ├── database/                     # Database components
│   │   ├── models.py                # Database models
│   │   ├── vector_ops.py            # Vector operations
│   │   └── connection.py            # Database connection
│   │
│   ├── frontend/                     # Frontend components
│   │   ├── static/                  # Static assets
│   │   ├── templates/               # HTML templates
│   │   └── routes.py                # Frontend routes
│   │
│   └── api/                         # API endpoints
│       ├── routes.py                # API routes
│       └── middleware.py            # API middleware
│
├── data/                            # Data directory
│   ├── second_grade/                # Second grade content
│   │   ├── utah_core_standards/    # Utah 2nd grade standards
│   │   │   ├── mathematics/        # Math standards and objectives
│   │   │   ├── english_language_arts/ # ELA standards
│   │   │   ├── science/           # Science standards
│   │   │   └── social_studies/    # Social studies standards
│   │   │
│   │   ├── teaching_methods/       # Teaching methodologies
│   │   │   ├── stem_integration/  # STEM teaching approaches
│   │   │   ├── literacy_development/ # Reading/writing methods
│   │   │   └── differentiation/   # Learning adaptations
│   │   │
│   │   └── assessment_methods/     # Age-appropriate assessments
│   │
│   ├── interactions/             # Teacher-student interactions
│   │   ├── classroom_management/ # Management scenarios
│   │   │   ├── positive_reinforcement/ # Positive behavior examples
│   │   │   ├── conflict_resolution/ # Conflict handling
│   │   │   └── transitions/     # Activity transitions
│   │   │
│   │   ├── instructional_dialogs/ # Teaching conversations
│   │   │   ├── math_discussions/ # Math teaching dialogs
│   │   │   ├── reading_groups/   # Reading group interactions
│   │   │   └── science_experiments/ # Science lesson dialogs
│   │   │
│   │   └── support_strategies/  # Learning support
│   │       ├── struggling_learners/ # Support for challenges
│   │       ├── advanced_learners/ # Enrichment interactions
│   │       └── esl_support/     # Language support
│   │
│   └── scenarios/               # Teaching scenarios
│       ├── core_subjects/      # Subject-specific
│       │   ├── mathematics/    # Math teaching scenarios
│       │   ├── reading_writing/ # Literacy scenarios
│       │   ├── science/       # Science experiments
│       │   └── social_studies/ # Social studies activities
│       │
│       ├── classroom_situations/ # Management scenarios
│       │   ├── daily_routines/ # Regular procedures
│       │   ├── special_events/ # Special activities
│       │   └── challenges/    # Difficult situations
│       │
│       └── special_cases/     # Specific situations
│           ├── learning_support/ # Learning difficulties
│           ├── behavioral_support/ # Behavior management
│           └── parent_communication/ # Parent interactions
│
├── docs/                            # Documentation
│   ├── roles/                       # Role-specific guides
│   ├── scenarios/                   # Scenario documentation
│   ├── technical/                   # Technical documentation
│   └── meetings/                    # Meeting notes
│
├── tests/                           # Test files
├── scripts/                         # Utility scripts
└── config/                          # Configuration files
```

## �� For Each Role

### Project Manager
- **Primary Guide**: [`docs/project-management/README.md`](docs/project-management/README.md)
- **Key Responsibilities**:
  - Oversee project lifecycle from initiation to completion
  - Develop and maintain project plan, schedule, and budget
  - Coordinate team collaboration and communication
  - Manage project risks and issues
  - Facilitate Agile/Scrum ceremonies
  - Ensure deliverables meet objectives
  - Foster team cohesion and resolve conflicts
- **Key Resources**:
  - [Project Timeline](docs/project_pipeline.md)
  - [Meeting Notes](docs/meetings/)
  - [Sprint Planning](docs/sprints/README.md)
  - [Resource Allocation](docs/resources/README.md)
  - [Risk Management Plan](docs/project-management/risk_management.md)
  - [Team Communication Guidelines](docs/project-management/communication.md)

### Product Owner
- **Primary Guide**: [`docs/product/README.md`](docs/product/README.md)
- **Key Responsibilities**:
  - Define and prioritize product backlog
  - Communicate product vision and goals
  - Gather and analyze user requirements
  - Coordinate with Dr. Ruggles for content validation
  - Ensure alignment with Utah Core Standards
  - Make decisions on features and functionality
  - Balance stakeholder expectations
  - Guide product development direction
- **Key Resources**:
  - [Expert Meeting Notes](docs/meetings/expert_reviews/)
  - [Teaching Scenarios](data/scenarios/core_subjects/)
  - [Content Validation Process](docs/validation/README.md)
  - [Educational Milestones](docs/milestones.md)
  - [Product Backlog](docs/product/backlog.md)
  - [Stakeholder Requirements](docs/product/requirements.md)

### AI/ML Developer
- **Primary Guide**: [`docs/ai/README.md`](docs/ai/README.md)
- **Key Responsibilities**:
  - Design, develop, and implement AI algorithms and models
  - Train and fine-tune models for educational context
  - Integrate AI components with overall architecture
  - Collaborate with Data Engineer for data preprocessing
  - Conduct experiments and evaluate model performance
  - Ensure age-appropriate language processing
  - Maintain educational accuracy in responses
- **Key Resources**:
  - [AI Implementation](src/ai/)
  - [Model Configurations](config/)
  - [AI Development Guidelines](docs/ai/development_guidelines.md)
  - [Model Training Protocols](docs/ai/training_protocols.md)
  - [Performance Metrics](docs/ai/performance_metrics.md)

### Frontend Developer
- **Primary Guide**: [`docs/frontend/README.md`](docs/frontend/README.md)
- **Key Responsibilities**:
  - Design intuitive and accessible teacher interfaces
  - Conduct user research with educators
  - Create wireframes and prototypes
  - Implement responsive UI components
  - Ensure accessibility compliance
  - Collaborate on user experience improvements
- **Key Resources**:
  - [Frontend Code](src/frontend/)
  - [UI Guidelines](docs/frontend/ui_guidelines.md)
  - [Accessibility Standards](docs/frontend/accessibility.md)
  - [Design System](docs/frontend/design_system.md)
  - [User Research](docs/frontend/user_research.md)

### Documentation and Quality Specialist
- **Primary Guide**: [`docs/qa/README.md`](docs/qa/README.md)
- **Key Responsibilities**:
  - Create and maintain comprehensive documentation
  - Develop quality assurance processes
  - Conduct testing and validation
  - Track and document defects
  - Ensure educational standard compliance
  - Coordinate with Dr. Ruggles for content validation
  - Maintain documentation accuracy and clarity
- **Key Resources**:
  - [Test Files](tests/)
  - [Educational Standards](data/second_grade/utah_core_standards/)
  - [Validation Criteria](docs/qa/validation_criteria.md)
  - [Documentation Guidelines](docs/qa/documentation_guidelines.md)
  - [QA Processes](docs/qa/quality_processes.md)

### Data Engineer
- **Primary Guide**: [`docs/data/README.md`](docs/data/README.md)
- **Key Responsibilities**:
  - Design and maintain data pipelines
  - Manage educational content databases
  - Ensure data quality and security
  - Collaborate with AI team on data preprocessing
  - Optimize data storage and retrieval
  - Monitor data infrastructure
- **Key Resources**:
  - [Data Architecture](docs/data/architecture.md)
  - [Pipeline Documentation](docs/data/pipelines.md)
  - [Data Security](docs/data/security.md)
  - [Quality Standards](docs/data/quality_standards.md)

### Backend Developer
- **Primary Guide**: [`docs/backend/README.md`](docs/backend/README.md)
- **Key Responsibilities**:
  - Develop server-side logic and APIs
  - Design and manage databases
  - Ensure system scalability and performance
  - Implement security measures
  - Integrate with AI and frontend components
- **Key Resources**:
  - [API Documentation](docs/backend/api.md)
  - [Database Schema](docs/backend/database.md)
  - [Security Protocols](docs/backend/security.md)
  - [Integration Guide](docs/backend/integration.md)

### Data Analyst
- **Primary Guide**: [`docs/analysis/README.md`](docs/analysis/README.md)
- **Key Responsibilities**:
  - Analyze chatbot performance data
  - Identify usage patterns and trends
  - Create performance reports
  - Provide improvement recommendations
  - Monitor educational effectiveness
- **Key Resources**:
  - [Analysis Methods](docs/analysis/methods.md)
  - [Reporting Templates](docs/analysis/reports.md)
  - [Metrics Dashboard](docs/analysis/dashboard.md)
  - [Improvement Tracking](docs/analysis/improvements.md)

## 📋 Elementary Education Content Specialist
### Dr. Krista Ruggles
**Associate Professor - Elementary Education STEM**
School of Education, Utah Valley University

#### Contact Information
- **Email**: kruggles@uvu.edu
- **Chat**: 10800383@uvu.edu
- **Phone**: 801-863-8057
- **Office**: ME-116B

#### Availability
- **Office Hours**: Schedule via email
- **Response Time**: 24-48 hours
- **Preferred Contact Method**: Email for initial contact

### Collaboration Guidelines
1. Schedule reviews through Project Manager
2. Submit content validation requests 48 hours in advance
3. Attend monthly cross-team alignment meetings
4. Follow expert feedback implementation process

### Review Schedule
- **Content Reviews**: Every 2 weeks
- **Team Meetings**: First Monday of each month
- **Emergency Reviews**: Contact via email with "URGENT" in subject

### Key Touchpoints
- Initial scenario validation
- Content accuracy review
- Age-appropriateness verification
- Educational standard alignment
- Response pattern validation
- Cross-team standardization

### Areas of Expertise
- Elementary Education STEM
- Second Grade Curriculum Development
- Teacher Training Methodologies
- Educational Technology Integration
- Student Assessment Strategies

## 🚀 Getting Started

For detailed setup instructions, see:

- [Development Environment Setup Guide](docs/setup/README.md)
- [Windows/WSL Setup](docs/setup/windows_wsl.md)
- [Environment Configuration](docs/setup/environment.md)
- [Database Setup](docs/setup/database.md)

Quick Start:
```bash
# Clone repository
git clone https://github.com/your-org/utah-tta.git
cd utah-tta

# Follow setup guide in docs/setup/README.md
```

## 📝 Development Workflow

1. **Creating New Educational Content**
   - **Second Grade Content**
     - Create content in appropriate directory under [`data/second_grade/`](/data/second_grade/README.md)
     - Follow Utah Core Standards templates
     - Submit for Dr. Ruggles' review

   - **Teacher-Student Interactions**
     - Document interactions in [`data/interactions/`](data/interactions/)
     - Ensure age-appropriate language
     - Include teaching context and objectives

   - **Teaching Scenarios**
     - Draft scenarios in relevant subject area under [`data/scenarios/core_subjects/`](data/scenarios/core_subjects/)
     - Include classroom management considerations
     - Document special cases and adaptations

2. **Content Review Process**
   - Submit content through Product Owner
   - Schedule review with Dr. Ruggles
   - Implement expert feedback
   - Move to appropriate approved directory

3. **Making Changes**
   - Create feature branch
   - Update tests
   - Update documentation
   - Create pull request

4. **Testing and Validation**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run specific content tests
   pytest tests/second_grade/
   pytest tests/interactions/
   pytest tests/scenarios/
   ```

5. **Content Integration**
   - Verify alignment with Core Standards
   - Check cross-references between content types
   - Update relevant metadata
   - Generate embeddings for AI training

## 🔍 Key Features

1. **RAG Pipeline**
   - [Embedding Generation](src/ai/embedding.py)
   - [Vector Similarity Search](src/database/vector_ops.py)
   - [Context-aware Responses](src/ai/rag_pipeline.py)

2. **Scenario Management**
   - [Expert Validation Process](docs/validation/process.md)
   - [Version Control Guide](docs/contributing/version_control.md)
   - [Performance Tracking](docs/technical/monitoring.md)

3. **Evaluation System**
   - [Response Scoring](src/ai/evaluation.py)
   - [Feedback Templates](docs/validation/feedback_templates.md)
   - [Progress Tracking](docs/technical/progress_tracking.md)

## 📚 Documentation

- [Technical Guides](docs/technical/)
- [API Documentation](docs/technical/api/)
- [Database Schema](docs/technical/database/)
- [Architecture Overview](docs/technical/architecture/)

## 🤝 Contributing

1. Read [`docs/contributing/guidelines.md`](docs/contributing/guidelines.md)
2. Follow [role-specific guides](docs/roles/)
3. Use [templates](data/templates/)
4. Ensure test coverage
5. Update documentation

## 🔧 Configuration

- [Development Config](config/development.py)
- [Production Config](config/production.py)
- [Testing Config](config/testing.py)

## 🆘 Getting Help

1. Check [role-specific documentation](docs/roles/)
2. Review [technical guides](docs/technical/)
3. Contact team lead
4. [Create an issue](docs/contributing/creating_issues.md)

## 📊 Monitoring

- Application logs in [`logs/`](logs/)
- [Metrics Dashboard](docs/technical/metrics.md)
- [Performance Monitoring](docs/technical/performance.md)
- [Error Tracking](docs/technical/error_tracking.md)

## 🔐 Security

- [SSL/TLS Configuration](docs/technical/security/ssl_config.md)
- [Rate Limiting](docs/technical/security/rate_limiting.md)
- [Input Validation](docs/technical/security/input_validation.md)
- [Access Control](docs/technical/security/access_control.md)

## 📅 Regular Maintenance

1. [Database Backups](docs/technical/maintenance/backups.md)
2. [Log Rotation](docs/technical/maintenance/log_rotation.md)
3. [Performance Monitoring](docs/technical/maintenance/monitoring.md)
4. [Security Updates](docs/technical/maintenance/security_updates.md)

## 🚀 Deployment

### Prerequisites

- Python 3.8+
- PostgreSQL or SQLite database
- Virtual environment (recommended)
- Flask (for API backend)
- React (for frontend UI)

### Steps to Deploy

1. ***Clone*** the Repository

   ```
   git clone https://github.com/your-org/utah-tta.git
   cd utah-tta
   ```

2. **Set Up Virtual Environment**

   
bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`


3. **Install Dependencies**

   
bash
   pip install -r requirements.txt


4. **Set Up Database**

   
bash
   python manage.py migrate
   python manage.py seed_data  # Optional: Populate with sample data


5. **Run the Backend**

   
bash
   flask run --host=0.0.0.0 --port=5000


6. **Start the Frontend**

   
bash
   cd frontend
   npm install
   npm start


 
