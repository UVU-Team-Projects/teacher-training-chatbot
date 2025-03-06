# Repository Structure

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
│   ├── scenarios/                   # Teaching scenarios
│   │   ├── approved/               # Expert-approved scenarios
│   │   ├── drafts/                 # Scenario drafts
│   │   └── templates/              # Scenario templates
│   │
│   ├── personas/                    # Student personas
│   │   ├── templates/              # Persona templates
│   │   └── approved/               # Approved personas
│   │
│   └── evaluation/                  # Evaluation data
│       ├── criteria/               # Evaluation criteria
│       └── feedback/               # Feedback templates
│
├── docs/                            # Documentation
│   ├── project_pipeline.md          # Project pipeline
│   ├── repository_structure.md      # This file
│   │
│   ├── roles/                       # Role-specific docs
│   │   ├── product_owner.md        # Product Owner guide
│   │   ├── content_specialist.md   # Content Specialist guide
│   │   ├── ai_developer.md        # AI Developer guide
│   │   ├── frontend_developer.md  # Frontend Developer guide
│   │   └── qa_specialist.md       # QA Specialist guide
│   │
│   ├── scenarios/                   # Scenario documentation
│   │   ├── README.md               # Scenario guide
│   │   ├── creation_guide.md       # Creation process
│   │   └── examples/               # Example scenarios
│   │
│   ├── technical/                   # Technical documentation
│   │   ├── ai/                     # AI implementation docs
│   │   ├── database/               # Database docs
│   │   ├── frontend/               # Frontend docs
│   │   └── api/                    # API documentation
│   │
│   └── meetings/                    # Meeting notes
│       ├── expert_reviews/         # Expert review notes
│       └── team_meetings/          # Team meeting notes
│
├── tests/                           # Test files
│   ├── ai/                         # AI component tests
│   ├── database/                   # Database tests
│   ├── frontend/                   # Frontend tests
│   ├── integration/                # Integration tests
│   └── scenarios/                  # Scenario tests
│
├── scripts/                         # Utility scripts
│   ├── setup/                      # Setup scripts
│   ├── data_processing/            # Data processing
│   └── monitoring/                 # Monitoring scripts
│
└── config/                          # Configuration files
    ├── development.py              # Development config
    ├── production.py               # Production config
    └── testing.py                  # Testing config

## Quick Access Guides

### For Product Owner
- `/docs/roles/product_owner.md` - Role guide
- `/docs/meetings/expert_reviews/` - Expert meeting notes
- `/data/scenarios/approved/` - Approved scenarios
- `/docs/scenarios/creation_guide.md` - Scenario creation process

### For Educational Content Specialist
- `/docs/roles/content_specialist.md` - Role guide
- `/data/scenarios/templates/` - Scenario templates
- `/data/personas/templates/` - Persona templates
- `/data/evaluation/criteria/` - Evaluation criteria

### For AI Developer
- `/docs/roles/ai_developer.md` - Role guide
- `/src/ai/` - AI implementation
- `/docs/technical/ai/` - AI documentation
- `/tests/ai/` - AI tests

### For Frontend Developer
- `/docs/roles/frontend_developer.md` - Role guide
- `/src/frontend/` - Frontend code
- `/docs/technical/frontend/` - Frontend documentation
- `/tests/frontend/` - Frontend tests

### For Project Manager
- `/docs/project_pipeline.md` - Project timeline
- `/docs/meetings/` - All meeting notes
- `/docs/repository_structure.md` - Repo structure

### For QA Specialist
- `/docs/roles/qa_specialist.md` - Role guide
- `/tests/` - All test files
- `/data/scenarios/approved/` - Approved scenarios for testing
- `/docs/technical/` - Technical documentation

## File Naming Conventions

1. **Documentation Files**
   - Use lowercase with underscores
   - Include date for meeting notes: `YYYY_MM_DD_meeting_notes.md`
   - Include version for scenarios: `scenario_v1.json`

2. **Source Code**
   - Use snake_case for Python files
   - Use camelCase for JavaScript files
   - Include type in name: `user_model.py`, `ScenarioComponent.js`

3. **Test Files**
   - Prefix with `test_`: `test_embedding.py`
   - Match source file name: `embedding.py` → `test_embedding.py`

## Best Practices

1. **Documentation**
   - Keep READMEs updated
   - Document all meetings
   - Include examples in guides
   - Cross-reference related docs

2. **Code Organization**
   - Follow component structure
   - Keep related files together
   - Use appropriate config files
   - Include component tests

3. **Data Management**
   - Use version control for scenarios
   - Keep drafts separate from approved
   - Include metadata in files
   - Regular backups of approved data
``` 