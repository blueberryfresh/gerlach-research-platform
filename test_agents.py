"""
Quick test script for the multi-agent system
"""

from pathlib import Path
from agents import (
    SupervisorAgent,
    Big5AssessmentAgent,
    DialogueCaptureAgent,
    PostExpSurveyAgent,
    SummaryReportAgent,
    WorkflowStage
)

DATA_DIR = Path(__file__).parent / "research_data"

def test_agents():
    """Test all agents"""
    print("=" * 60)
    print("Testing Multi-Agent Research System")
    print("=" * 60)
    
    # Initialize agents
    print("\n1. Initializing agents...")
    supervisor = SupervisorAgent(DATA_DIR)
    assessment_agent = Big5AssessmentAgent(DATA_DIR)
    dialogue_agent = DialogueCaptureAgent(DATA_DIR)
    survey_agent = PostExpSurveyAgent(DATA_DIR)
    summary_agent = SummaryReportAgent(DATA_DIR)
    print("✓ All agents initialized")
    
    # Create session
    print("\n2. Creating user session...")
    session = supervisor.create_user_session(
        user_id="test_user_001",
        metadata={"test": True}
    )
    print(f"✓ Session created: {session.session_id}")
    
    # Conduct assessment
    print("\n3. Conducting Big5 assessment...")
    supervisor.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
    
    # Create sample responses (all 3s for neutral)
    responses = {}
    items = assessment_agent.get_assessment_items()
    for item in items:
        responses[item['id']] = 3
    
    assessment = assessment_agent.conduct_assessment(
        user_id="test_user_001",
        session_id=session.session_id,
        responses=responses
    )
    
    session.big5_assessment_id = assessment.assessment_id
    session.save(DATA_DIR)
    
    print(f"✓ Assessment completed: {assessment.assessment_id}")
    print(f"  - Gerlach Type: {assessment.gerlach_type}")
    print(f"  - Scores: O={assessment.openness:.1f}, C={assessment.conscientiousness:.1f}, "
          f"E={assessment.extraversion:.1f}, A={assessment.agreeableness:.1f}, N={assessment.neuroticism:.1f}")
    
    # Start dialogue
    print("\n4. Starting dialogue...")
    supervisor.advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
    
    dialogue = dialogue_agent.start_dialogue(
        user_id="test_user_001",
        session_id=session.session_id,
        task_name="Test Task",
        llm_personality="average"
    )
    
    session.dialogue_records.append(dialogue.dialogue_id)
    session.save(DATA_DIR)
    
    print(f"✓ Dialogue started: {dialogue.dialogue_id}")
    
    # Record some messages
    dialogue_agent.record_message(dialogue.dialogue_id, "user", "Hello, can you help me with this task?")
    dialogue_agent.record_message(dialogue.dialogue_id, "assistant", "Of course! I'd be happy to help you with this task.")
    dialogue_agent.record_message(dialogue.dialogue_id, "user", "Great, let's get started.")
    
    print(f"✓ Recorded 3 messages")
    
    # End dialogue
    dialogue_agent.end_dialogue(dialogue.dialogue_id)
    print(f"✓ Dialogue ended")
    
    # Conduct survey
    print("\n5. Conducting post-experiment survey...")
    supervisor.advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
    
    survey_responses = {
        "task_difficulty": 4,
        "llm_helpfulness": 5,
        "overall_satisfaction": 6,
        "what_worked_well": "The AI was very helpful and responsive.",
        "what_could_improve": "Could provide more detailed explanations.",
        "additional_comments": "Overall a great experience!"
    }
    
    survey = survey_agent.conduct_survey(
        user_id="test_user_001",
        session_id=session.session_id,
        dialogue_id=dialogue.dialogue_id,
        responses=survey_responses
    )
    
    print(f"✓ Survey completed: {survey.survey_id}")
    
    # Generate report
    print("\n6. Generating comprehensive report...")
    supervisor.advance_stage(session.session_id, WorkflowStage.COMPLETED)
    
    report = summary_agent.generate_report(
        user_id="test_user_001",
        session_id=session.session_id
    )
    
    session.report_id = report.report_id
    session.save(DATA_DIR)
    
    print(f"✓ Report generated: {report.report_id}")
    print(f"  - Total dialogues: {report.total_dialogues}")
    print(f"  - Total messages: {report.total_messages}")
    print(f"  - Average satisfaction: {report.average_satisfaction:.1f}/7")
    
    # Get system statistics
    print("\n7. System statistics...")
    stats = supervisor.get_statistics()
    print(f"✓ Total sessions: {stats['total_sessions']}")
    print(f"✓ Total assessments: {stats['total_assessments']}")
    print(f"✓ Total dialogues: {stats['total_dialogues']}")
    print(f"✓ Total surveys: {stats['total_surveys']}")
    print(f"✓ Total reports: {stats['total_reports']}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    print(f"\nData saved to: {DATA_DIR}")
    print(f"Report files:")
    print(f"  - {DATA_DIR}/reports/{report.report_id}.json")
    print(f"  - {DATA_DIR}/reports/{report.report_id}.md")
    print(f"  - {DATA_DIR}/reports/{report.report_id}.html")
    

if __name__ == "__main__":
    test_agents()
