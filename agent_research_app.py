"""
Multi-Agent Research Application
Integrated Streamlit interface for the complete research workflow
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent))

from agents import (
    SupervisorAgent,
    Big5AssessmentAgent,
    DialogueCaptureAgent,
    PostExpSurveyAgent,
    SummaryReportAgent,
    TaskResponseAgent,
    WorkflowStage
)
from gerlach_personality_llms import GerlachPersonalityManager
from task_response_ui import render_task_response

# Configuration
DATA_DIR = Path(__file__).parent / "research_data"
TASK_FOLDER = Path(__file__).parent / "Task"

st.set_page_config(
    page_title="Gerlach Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize agents
@st.cache_resource
def init_agents():
    """Initialize all agents"""
    supervisor = SupervisorAgent(DATA_DIR)
    assessment_agent = Big5AssessmentAgent(DATA_DIR)
    dialogue_agent = DialogueCaptureAgent(DATA_DIR)
    task_response_agent = TaskResponseAgent(DATA_DIR)
    survey_agent = PostExpSurveyAgent(DATA_DIR)
    summary_agent = SummaryReportAgent(DATA_DIR)
    
    try:
        llm_manager = GerlachPersonalityManager()
        llm_ready = True
    except Exception as e:
        llm_manager = None
        llm_ready = False
        st.error(f"LLM Manager initialization failed: {e}")
    
    return {
        'supervisor': supervisor,
        'assessment': assessment_agent,
        'dialogue': dialogue_agent,
        'task_response': task_response_agent,
        'survey': survey_agent,
        'summary': summary_agent,
        'llm_manager': llm_manager,
        'llm_ready': llm_ready
    }

agents = init_agents()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'current_session' not in st.session_state:
    st.session_state.current_session = None

if 'current_dialogue_id' not in st.session_state:
    st.session_state.current_dialogue_id = None

if 'assessment_responses' not in st.session_state:
    st.session_state.assessment_responses = {}

if 'current_messages' not in st.session_state:
    st.session_state.current_messages = []

if 'survey_responses' not in st.session_state:
    st.session_state.survey_responses = {}


def render_registration():
    """Stage 1: User Registration"""
    st.header("🔬 Welcome to the Gerlach Personality Research Platform")
    
    st.markdown("""
    This research platform allows you to:
    1. Complete a Big Five personality assessment
    2. Solve tasks with AI personalities
    3. Provide feedback through surveys
    4. Receive a comprehensive research report
    """)
    
    st.markdown("---")
    
    with st.form("registration_form"):
        st.subheader("Participant Registration")
        
        user_id = st.text_input(
            "Enter your participant ID:",
            placeholder="e.g., P001, participant_123",
            help="This ID will be used to track your session"
        )
        
        consent = st.checkbox(
            "I consent to participate in this research study",
            help="Your data will be anonymized and used for research purposes only"
        )
        
        submit = st.form_submit_button("Begin Research Session", use_container_width=True)
        
        if submit:
            if not user_id:
                st.error("Please enter a participant ID")
            elif not consent:
                st.error("Please provide consent to participate")
            else:
                # Create new session
                session = agents['supervisor'].create_user_session(
                    user_id=user_id,
                    metadata={"consent_given": True, "start_time": datetime.now().isoformat()}
                )
                
                st.session_state.user_id = user_id
                st.session_state.current_session = session
                
                # Advance to assessment stage
                agents['supervisor'].advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
                
                st.success(f"Session created! Session ID: {session.session_id}")
                st.rerun()


def render_big5_assessment():
    """Stage 2: Big5 Personality Assessment"""
    st.header("📋 Big Five Personality Assessment")
    
    st.markdown("""
    Please rate how much you agree with each statement on a scale of 1-5:
    - **1** = Strongly Disagree
    - **2** = Disagree
    - **3** = Neutral
    - **4** = Agree
    - **5** = Strongly Agree
    """)
    
    st.markdown("---")
    
    items = agents['assessment'].get_assessment_items()
    
    with st.form("assessment_form"):
        responses = {}
        
        # Group by trait for better organization
        traits = {
            "extraversion": "Extraversion (Social & Energetic)",
            "agreeableness": "Agreeableness (Cooperative & Trusting)",
            "conscientiousness": "Conscientiousness (Organized & Disciplined)",
            "neuroticism": "Neuroticism (Emotional Stability)",
            "openness": "Openness (Creative & Curious)"
        }
        
        for trait_key, trait_name in traits.items():
            with st.expander(f"📌 {trait_name}", expanded=False):
                trait_items = [item for item in items if item['trait'] == trait_key]
                
                for item in trait_items:
                    responses[item['id']] = st.radio(
                        item['text'],
                        options=[1, 2, 3, 4, 5],
                        index=2,
                        horizontal=True,
                        key=f"q_{item['id']}"
                    )
        
        submit = st.form_submit_button("Submit Assessment", use_container_width=True)
        
        if submit:
            # Conduct assessment
            assessment = agents['assessment'].conduct_assessment(
                user_id=st.session_state.user_id,
                session_id=st.session_state.current_session.session_id,
                responses=responses
            )
            
            # Update session
            session = st.session_state.current_session
            session.big5_assessment_id = assessment.assessment_id
            session.save(DATA_DIR)
            
            # Advance to task selection
            agents['supervisor'].advance_stage(session.session_id, WorkflowStage.TASK_SELECTION)
            
            st.success("✅ Assessment completed!")
            st.balloons()
            
            # Show results
            st.markdown("### Your Big Five Scores")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            cols = [col1, col2, col3, col4, col5]
            traits_list = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
            
            for col, trait in zip(cols, traits_list):
                score = getattr(assessment, trait)
                col.metric(trait.title(), f"{score:.1f}")
            
            st.info(f"**Gerlach Personality Type:** {assessment.gerlach_type.replace('_', ' ').title()}")
            
            st.rerun()


def render_task_selection():
    """Stage 3: Task Selection"""
    st.header("📄 Select a Task")
    
    st.markdown("Choose a task to work on with an AI personality:")
    
    # Get available tasks
    if TASK_FOLDER.exists():
        tasks = list(TASK_FOLDER.glob("*.pdf")) + list(TASK_FOLDER.glob("*.txt")) + list(TASK_FOLDER.glob("*.md"))
        task_names = [t.name for t in tasks]
    else:
        task_names = []
        st.warning("No tasks folder found")
    
    # Get assessment to show personality type
    session = st.session_state.current_session
    if session.big5_assessment_id:
        assessment = agents['assessment'].get_assessment(session.big5_assessment_id)
        if assessment:
            st.info(f"Your personality type: **{assessment.gerlach_type.replace('_', ' ').title()}**")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Task")
        selected_task = st.selectbox(
            "Choose a task:",
            task_names if task_names else ["No tasks available"],
            key="task_selection"
        )
    
    with col2:
        st.subheader("Select AI Personality")
        personalities = {
            "average": "⚖️ Average - Balanced & Practical",
            "role_model": "⭐ Role Model - Optimistic & Organized",
            "self_centred": "🎯 Self-Centred - Direct & Competitive",
            "reserved": "🤫 Reserved - Calm & Conventional"
        }
        
        selected_personality = st.selectbox(
            "Choose AI personality:",
            list(personalities.keys()),
            format_func=lambda x: personalities[x],
            key="personality_selection"
        )
    
    if st.button("Start Task Dialogue", use_container_width=True, type="primary"):
        if not agents['llm_ready']:
            st.error("LLM Manager not ready. Please set ANTHROPIC_API_KEY.")
        else:
            # Start dialogue
            dialogue = agents['dialogue'].start_dialogue(
                user_id=st.session_state.user_id,
                session_id=session.session_id,
                task_name=selected_task,
                llm_personality=selected_personality
            )
            
            st.session_state.current_dialogue_id = dialogue.dialogue_id
            st.session_state.current_messages = []
            
            # Update session
            session.dialogue_records.append(dialogue.dialogue_id)
            session.save(DATA_DIR)
            
            # Advance to dialogue stage
            agents['supervisor'].advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
            
            st.success(f"Started dialogue with {personalities[selected_personality]}")
            st.rerun()


def render_task_dialogue():
    """Stage 4: Task Dialogue"""
    dialogue_id = st.session_state.current_dialogue_id
    dialogue = agents['dialogue'].get_dialogue(dialogue_id)
    
    if not dialogue:
        st.error("Dialogue not found")
        return
    
    st.header(f"💬 Task Dialogue: {dialogue.task_name}")
    
    personality_info = {
        "average": {"emoji": "⚖️", "name": "Average", "color": "#7570b3"},
        "role_model": {"emoji": "⭐", "name": "Role Model", "color": "#1b9e77"},
        "self_centred": {"emoji": "🎯", "name": "Self-Centred", "color": "#d95f02"},
        "reserved": {"emoji": "🤫", "name": "Reserved", "color": "#e7298a"}
    }
    
    info = personality_info.get(dialogue.llm_personality, {})
    
    st.markdown(
        f"""<div style='background:{info.get('color', '#666')};color:white;padding:15px;border-radius:10px;margin-bottom:20px;'>
        <h3 style='margin:0;'>{info.get('emoji', '')} Chatting with: {info.get('name', dialogue.llm_personality)}</h3>
        <p style='margin:5px 0 0 0;'>Task: {dialogue.task_name}</p>
        </div>""",
        unsafe_allow_html=True
    )
    
    # Display messages
    for msg in dialogue.messages:
        if msg.role == "user":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant", avatar=info.get('emoji', '🤖')).write(msg.content)
    
    # Chat input
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # Record user message
        agents['dialogue'].record_message(dialogue_id, "user", user_input)
        
        # Get LLM response
        personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
        
        # Build message history
        messages = [{"role": m.role, "content": m.content} for m in dialogue.messages]
        
        with st.spinner(f"{info.get('emoji', '🤖')} Thinking..."):
            response = personality.chat(messages)
        
        # Record assistant message
        agents['dialogue'].record_message(dialogue_id, "assistant", response)
        
        st.rerun()
    
    # End dialogue button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric("Messages Exchanged", dialogue.total_messages)
    
    with col2:
        if st.button("End Dialogue", use_container_width=True, type="primary"):
            agents['dialogue'].end_dialogue(dialogue_id)
            
            # Advance to task response (task-specific data capture)
            agents['supervisor'].advance_stage(
                st.session_state.current_session.session_id,
                WorkflowStage.TASK_RESPONSE
            )
            
            st.success("Dialogue ended!")
            st.rerun()


def render_post_survey():
    """Stage 5: Post-Experiment Survey"""
    st.header("📊 Post-Experiment Survey")
    
    dialogue_id = st.session_state.current_dialogue_id
    dialogue = agents['dialogue'].get_dialogue(dialogue_id)
    
    if dialogue:
        st.info(f"Please provide feedback on your experience with **{dialogue.llm_personality.replace('_', ' ').title()}** on task: **{dialogue.task_name}**")
    
    st.markdown("---")
    
    questions = agents['survey'].get_survey_questions()
    
    st.markdown("""
    **Instructions**: There are 37 questions total. Please read carefully and answer as best as you can.
    
    For rating questions (1-31): Use the scale where **1 = Strongly Disagree** and **7 = Strongly Agree**
    """)
    
    with st.form("survey_form"):
        responses = {}
        
        # Likert scale questions (Q1-Q31)
        st.subheader("Part 1: Rating Questions (1-31)")
        st.markdown("*Rate each statement on a scale of 1-7*")
        
        likert_questions = {k: v for k, v in questions.items() if v['type'] == 'likert'}
        
        # Display in groups for better organization
        for i, (key, q_data) in enumerate(likert_questions.items(), 1):
            responses[key] = st.slider(
                f"**Q{i}.** {q_data['question']}",
                min_value=q_data['scale'][0],
                max_value=q_data['scale'][1],
                value=4,
                help="1 = Strongly Disagree, 4 = Neutral, 7 = Strongly Agree",
                key=f"survey_{key}"
            )
            
            # Add spacing every 5 questions for readability
            if i % 5 == 0 and i < len(likert_questions):
                st.markdown("---")
        
        st.markdown("---")
        st.subheader("Part 2: Open-Ended Questions (32-37)")
        st.markdown("*Please provide detailed responses*")
        
        # Text questions (Q32-Q37)
        text_questions = {k: v for k, v in questions.items() if v['type'] == 'text'}
        
        for i, (key, q_data) in enumerate(text_questions.items(), 32):
            responses[key] = st.text_area(
                f"**Q{i}.** {q_data['question']}",
                placeholder=q_data.get('placeholder', ''),
                key=f"survey_{key}",
                height=120
            )
        
        submit = st.form_submit_button("Submit Survey", use_container_width=True)
        
        if submit:
            # Conduct survey
            survey = agents['survey'].conduct_survey(
                user_id=st.session_state.user_id,
                session_id=st.session_state.current_session.session_id,
                dialogue_id=dialogue_id,
                responses=responses
            )
            
            st.success("✅ Survey submitted!")
            
            # Check if user wants to do another task or finish
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Work on Another Task", use_container_width=True):
                    # Go back to task selection
                    agents['supervisor'].advance_stage(
                        st.session_state.current_session.session_id,
                        WorkflowStage.TASK_SELECTION
                    )
                    st.session_state.current_dialogue_id = None
                    st.rerun()
            
            with col2:
                if st.button("Complete Session & Generate Report", use_container_width=True, type="primary"):
                    # Generate report and complete
                    agents['supervisor'].advance_stage(
                        st.session_state.current_session.session_id,
                        WorkflowStage.COMPLETED
                    )
                    st.rerun()


def render_completed():
    """Stage 6: Session Completed & Report"""
    st.header("✅ Session Completed!")
    
    st.success("Thank you for participating in this research study!")
    
    session = st.session_state.current_session
    
    # Generate report
    if st.button("Generate Comprehensive Report", use_container_width=True, type="primary"):
        with st.spinner("Generating your research report..."):
            report = agents['summary'].generate_report(
                user_id=st.session_state.user_id,
                session_id=session.session_id
            )
            
            session.report_id = report.report_id
            session.save(DATA_DIR)
        
        st.success(f"Report generated! Report ID: {report.report_id}")
        
        # Display report
        st.markdown("---")
        st.markdown("## Your Research Report")
        
        tabs = st.tabs(["📊 Summary", "📄 Full Report", "💾 Downloads"])
        
        with tabs[0]:
            # Summary view
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Dialogues", report.total_dialogues)
            col2.metric("Messages", report.total_messages)
            col3.metric("Time (min)", f"{report.total_time_seconds / 60:.1f}")
            
            if report.average_satisfaction:
                col4.metric("Avg Satisfaction", f"{report.average_satisfaction:.1f}/7")
            
            if report.big5_scores:
                st.markdown("### Your Big Five Profile")
                
                for trait, score in report.big5_scores.items():
                    st.progress(score / 100, text=f"{trait.title()}: {score:.1f}")
                
                st.info(f"**Personality Type:** {report.gerlach_type.replace('_', ' ').title()}")
        
        with tabs[1]:
            # Full markdown report
            if report.markdown_report:
                st.markdown(report.markdown_report)
        
        with tabs[2]:
            # Download options
            st.markdown("### Download Your Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if report.markdown_report:
                    st.download_button(
                        "📄 Download Markdown Report",
                        data=report.markdown_report,
                        file_name=f"report_{report.report_id}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            with col2:
                if report.html_report:
                    st.download_button(
                        "🌐 Download HTML Report",
                        data=report.html_report,
                        file_name=f"report_{report.report_id}.html",
                        mime="text/html",
                        use_container_width=True
                    )
    
    st.markdown("---")
    
    if st.button("Start New Session", use_container_width=True):
        # Clear session state
        st.session_state.user_id = None
        st.session_state.current_session = None
        st.session_state.current_dialogue_id = None
        st.rerun()


# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔬 Research Platform")
        
        if st.session_state.current_session:
            session = st.session_state.current_session
            
            st.markdown(f"**User:** {st.session_state.user_id}")
            st.markdown(f"**Session:** {session.session_id[:12]}...")
            
            # Workflow progress
            st.markdown("---")
            st.markdown("### Workflow Progress")
            
            stages = [
                ("Registration", WorkflowStage.REGISTRATION),
                ("Assessment", WorkflowStage.BIG5_ASSESSMENT),
                ("Task Selection", WorkflowStage.TASK_SELECTION),
                ("Dialogue", WorkflowStage.TASK_DIALOGUE),
                ("Task Response", WorkflowStage.TASK_RESPONSE),
                ("Survey", WorkflowStage.POST_SURVEY),
                ("Completed", WorkflowStage.COMPLETED)
            ]
            
            for stage_name, stage_enum in stages:
                if stage_enum.value in session.completed_stages:
                    st.markdown(f"✅ {stage_name}")
                elif session.current_stage == stage_enum:
                    st.markdown(f"▶️ **{stage_name}** (current)")
                else:
                    st.markdown(f"⏸️ {stage_name}")
            
            # Statistics
            st.markdown("---")
            st.markdown("### Statistics")
            
            stats = agents['supervisor'].get_statistics()
            st.metric("Total Sessions", stats['total_sessions'])
            st.metric("Total Dialogues", stats['total_dialogues'])
        
        else:
            st.info("No active session")
    
    # Main content
    if not st.session_state.current_session:
        render_registration()
    else:
        session = st.session_state.current_session
        
        if session.current_stage == WorkflowStage.BIG5_ASSESSMENT:
            render_big5_assessment()
        elif session.current_stage == WorkflowStage.TASK_SELECTION:
            render_task_selection()
        elif session.current_stage == WorkflowStage.TASK_DIALOGUE:
            render_task_dialogue()
        elif session.current_stage == WorkflowStage.TASK_RESPONSE:
            render_task_response(agents, session, st.session_state.current_dialogue_id)
        elif session.current_stage == WorkflowStage.POST_SURVEY:
            render_post_survey()
        elif session.current_stage == WorkflowStage.COMPLETED:
            render_completed()


if __name__ == "__main__":
    main()
