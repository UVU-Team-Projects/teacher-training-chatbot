# Role-Based File Responsibilities Guide

This guide outlines which roles are responsible for maintaining specific directories and files in the UTAH-TTA project.

## 📋 Table of Contents
- [Product Owner](#product-owner)
- [Educational Content Specialist](#educational-content-specialist)
- [AI/ML Developer](#aiml-developer)
- [Frontend Developer](#frontend-developer)
- [Project Manager](#project-manager)
- [QA/Documentation Specialist](#qadocumentation-specialist)

## Product Owner

### Primary Directories
- `docs/meetings/expert_reviews/` - Expert meeting notes and feedback
- `data/scenarios/approved/` - Final approval of scenarios
- `docs/project_pipeline.md` - Project roadmap and milestones

### Key Responsibilities
- Review and approve scenario content before moving to `data/scenarios/approved/`
- Maintain documentation of expert feedback in `docs/meetings/expert_reviews/`
- Update project requirements in `docs/requirements/`
- Sign off on major version changes in configuration files

## Educational Content Specialist

### Primary Directories
- `data/scenarios/drafts/` - New scenario creation
- `data/scenarios/templates/` - Scenario templates
- `data/personas/` - Student persona development
- `data/evaluation/criteria/` - Evaluation criteria
- `data/evaluation/feedback/` - Feedback templates

### Key Responsibilities
- Create and update scenario templates
- Draft new scenarios in `data/scenarios/drafts/`
- Maintain student personas in `data/personas/`
- Define evaluation criteria in `data/evaluation/criteria/`
- Create feedback templates in `data/evaluation/feedback/`

## AI/ML Developer

### Primary Directories
- `src/ai/` - AI component implementation
- `tests/ai/` - AI component tests
- `scripts/data_processing/` - Data processing scripts
- `config/` - Model configuration files

### Key Responsibilities
- Maintain all files in `src/ai/`
- Update AI-related configuration in `config/`
- Create and maintain AI component tests in `tests/ai/`
- Develop data processing scripts in `scripts/data_processing/`
- Document AI components in `docs/technical/ai/`

## Frontend Developer

### Primary Directories
- `src/frontend/` - Frontend implementation
- `templates/` - HTML templates
- `src/api/` - API endpoints
- `tests/frontend/` - Frontend tests
- `tests/integration/` - Integration tests

### Key Responsibilities
- Maintain all files in `src/frontend/`
- Update HTML templates in `templates/`
- Implement API endpoints in `src/api/`
- Create and maintain frontend tests
- Document frontend components in `docs/technical/frontend/`

## Project Manager

### Primary Directories
- `docs/meetings/` - Meeting notes and decisions
- `docs/project_pipeline.md` - Project timeline
- `docs/roles/` - Role documentation
- `.github/` - GitHub configuration

### Key Responsibilities
- Maintain project documentation in `docs/`
- Update meeting notes in `docs/meetings/`
- Manage GitHub project configuration
- Review and update role documentation
- Coordinate documentation updates across teams

## QA/Documentation Specialist

### Primary Directories
- `tests/` - Test suite organization
- `docs/technical/` - Technical documentation
- `docs/user_guides/` - User documentation
- `.github/workflows/` - CI/CD configuration

### Key Responsibilities
- Maintain test organization and structure
- Update technical documentation
- Create and update user guides
- Configure and maintain CI/CD pipelines
- Review and validate documentation changes

## Cross-Team Responsibilities

### Version Control
- All roles must follow Git workflow defined in `docs/contributing/git_workflow.md`
- Create feature branches from `main`
- Submit pull requests for review
- Update relevant documentation with code changes

### Documentation
- Each role maintains documentation for their components
- Cross-reference documentation when updating shared components
- Follow documentation standards in `docs/contributing/documentation_guidelines.md`

### Testing
- Write tests for new features in respective test directories
- Maintain existing tests related to their components
- Participate in integration testing

## File Update Workflow

1. **New Features**
   ```
   feature_branch/
   ├── Implementation
   │   └── Update relevant src/ files
   ├── Tests
   │   └── Add tests in tests/
   └── Documentation
       └── Update docs/
   ```

2. **Bug Fixes**
   ```
   bugfix_branch/
   ├── Fix
   │   └── Update affected files
   ├── Tests
   │   └── Add regression tests
   └── Documentation
       └── Update if needed
   ```

3. **Documentation Updates**
   ```
   docs_branch/
   └── docs/
       ├── Update relevant .md files
       └── Update diagrams if needed
   ```

## Review Requirements

### Code Changes
- AI changes: AI Developer + QA review
- Frontend changes: Frontend Developer + QA review
- Content changes: Educational Specialist + Product Owner review
- Documentation: Respective role owner + Documentation Specialist review

### Content Changes
- Scenarios: Educational Specialist → Product Owner → Education Expert
- Templates: Educational Specialist → Product Owner
- Documentation: Role Owner → Documentation Specialist

## Code Review and Commit Approval

### Primary Reviewers
- **Project Manager**: Final approval for all pull requests to `main` branch
- **QA/Documentation Specialist**: Required reviewer for all code changes
- **Domain Experts**: Required based on changed components:
  - AI/ML changes: AI Developer approval required
  - Frontend changes: Frontend Developer approval required
  - Educational content: Educational Content Specialist and Product Owner approval required

### Review Process
1. **Initial Review**
   - Code author creates pull request
   - Assigns appropriate domain expert(s)
   - Adds QA/Documentation Specialist as reviewer

2. **Domain Review**
   - Domain expert(s) review technical implementation
   - Provide feedback or approval
   - May require multiple iterations

3. **QA Review**
   - QA/Documentation Specialist reviews:
     - Test coverage
     - Documentation updates
     - Code quality standards
     - Integration considerations

4. **Final Approval**
   - Project Manager reviews:
     - All required approvals are complete
     - Changes align with project goals
     - Merge conflicts are resolved
     - Documentation is updated

### Branch Protection Rules
- `main` branch requires:
  - Minimum 2 approvals
  - Project Manager's approval
  - Passing CI/CD checks
  - No merge conflicts
  - Up-to-date branch

### Emergency Procedures
- Hotfix process requires:
  - Project Manager approval
  - At least one domain expert review
  - Post-deployment review within 24 hours

## Additional Resources

- [Contributing Guidelines](../contributing/guidelines.md)
- [Git Workflow](../contributing/git_workflow.md)
- [Documentation Standards](../contributing/documentation_guidelines.md)
- [Review Process](../contributing/review_process.md)

## Support

For clarification on responsibilities:
1. Check this guide
2. Consult your team lead
3. Ask in team channel
4. Contact Project Manager 