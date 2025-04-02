# Educational Scenario Development Guide

## Scenario Structure
Each scenario must include:
1. **Context**: Detailed classroom situation
2. **Student Behavior**: Specific student actions/needs
3. **Expected Response**: Expert-approved teacher response
4. **Evaluation Criteria**: Specific points to assess in teacher responses
5. **Improvement Suggestions**: Common mistakes and how to improve

## Development Process
1. **Initial Draft**
   - Educational Content Specialist creates scenario draft
   - Based on common classroom situations
   - Include preliminary evaluation criteria

2. **Expert Review**
   - Product Owner schedules review with Education Expert
   - Document feedback and required changes
   - Get explicit approval for:
     - Scenario realism
     - Expected response appropriateness
     - Evaluation criteria accuracy

3. **Documentation**
   - Store approved scenarios in structured format:
   ```json
   {
     "id": "scenario_001",
     "context": "4th-grade math class, 25 students",
     "situation": "Student consistently interrupts other students during discussion",
     "student_background": "Struggles with impulse control, high academic performance",
     "expected_response": "Detailed expert-approved response",
     "evaluation_criteria": [
       "Addresses behavior privately",
       "Maintains student dignity",
       "Sets clear expectations",
       "Provides support strategies"
     ],
     "improvement_suggestions": [
       "Avoid public confrontation",
       "Don't ignore the behavior",
       "Don't punish without support"
     ],
     "expert_notes": "Focus on positive reinforcement",
     "approval_date": "2024-03-15",
     "expert_id": "exp_001"
   }
   ```

4. **Implementation**
   - AI team implements approved scenarios
   - Create embeddings for scenarios
   - Test response generation
   - Validate against expert criteria

5. **Quality Assurance**
   - Test scenario implementation
   - Verify response evaluation
   - Check alignment with expert approval
   - Document test results

## Continuous Improvement
1. **Usage Tracking**
   - Monitor scenario usage
   - Track teacher response patterns
   - Identify common difficulties

2. **Regular Review**
   - Schedule periodic expert reviews
   - Update scenarios based on feedback
   - Add new scenarios for gaps

3. **Performance Metrics**
   - Track approval rates
   - Monitor response accuracy
   - Measure teacher satisfaction
   - Document improvement suggestions

## Expert Communication Protocol
1. **Meeting Schedule**
   - Regular monthly reviews
   - Ad-hoc reviews for new scenarios
   - Emergency consultations if needed

2. **Documentation Requirements**
   - Meeting minutes
   - Scenario approval status
   - Expert suggestions
   - Follow-up actions

3. **Approval Process**
   - Submit scenarios 1 week before review
   - Get written approval
   - Document any conditions
   - Schedule follow-up if needed 