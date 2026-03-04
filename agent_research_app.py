"""
Multi-Agent Research Application
Integrated Streamlit interface for the complete research workflow
"""

import random
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
import admin_download

# Configuration
DATA_DIR = Path(__file__).parent / "research_data"
TASK_FOLDER = Path(__file__).parent / "Task"

st.set_page_config(
    page_title="Gerlach Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
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

if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False


_STAGE_LABELS = {
    "registration":   "Step 1 of 3 — Questionnaires",
    "big5_assessment":"Step 1 of 3 — Questionnaires",
    "task_selection": "Step 2 of 3 — Collaboration Task",
    "task_dialogue":  "Step 2 of 3 — Collaboration Task",
    "task_response":  "Step 2 of 3 — Collaboration Task",
    "post_survey":    "Step 3 of 3 — Follow-up Questionnaire",
    "completed":      "Completed",
}


def render_registration():
    """Stage 1: User Registration"""
    st.header("Welcome to Our Study")

    st.markdown("""
    Thank you for participating. In this study, you will be asked to:

    1. Answer a few questionnaires
    2. Collaborate on a task with a Large Language Model (LLM)
    3. Complete a brief follow-up questionnaire
    """)

    st.markdown("---")

    tab_new, tab_resume = st.tabs(["New Participant", "Resume Session"])

    # ── New Participant ───────────────────────────────────────────────────────
    with tab_new:
        with st.form("registration_form"):
            st.markdown("**Enter the participant ID provided to you by the researcher.**")

            user_id = st.text_input(
                "Participant ID:",
                placeholder="e.g., P001",
                help="This ID will be used to track and save your progress."
            )

            consent = st.checkbox(
                "I consent to participate in this research study",
                help="Your data will be anonymised and used for research purposes only."
            )

            submit = st.form_submit_button("Begin Study", use_container_width=True)

            if submit:
                if not user_id:
                    st.error("Please enter your participant ID.")
                elif not consent:
                    st.error("Please tick the consent box to continue.")
                else:
                    existing = agents['supervisor'].find_active_session_by_user(user_id.strip())
                    if existing:
                        # Already has a session — silently resume so they don't create a duplicate
                        st.session_state.user_id = user_id.strip()
                        st.session_state.current_session = existing
                        if existing.dialogue_ids:
                            st.session_state.current_dialogue_id = existing.dialogue_ids[-1]
                        st.rerun()
                    else:
                        session = agents['supervisor'].create_user_session(
                            user_id=user_id.strip(),
                            metadata={"consent_given": True, "start_time": datetime.now().isoformat()}
                        )
                        st.session_state.user_id = user_id.strip()
                        st.session_state.current_session = session
                        agents['supervisor'].advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
                        st.rerun()

    # ── Resume Session ────────────────────────────────────────────────────────
    with tab_resume:
        st.markdown(
            "If you started the study earlier and need to continue, "
            "enter your **Participant ID** below."
        )

        with st.form("resume_form"):
            resume_id = st.text_input(
                "Participant ID:",
                placeholder="e.g., P001",
                key="resume_id_input"
            )
            resume_btn = st.form_submit_button("Resume My Session", use_container_width=True)

            if resume_btn:
                if not resume_id:
                    st.error("Please enter your participant ID.")
                else:
                    existing = agents['supervisor'].find_active_session_by_user(resume_id.strip())
                    if existing:
                        stage_label = _STAGE_LABELS.get(existing.current_stage.value, "In progress")
                        st.session_state.user_id = resume_id.strip()
                        st.session_state.current_session = existing
                        if existing.dialogue_ids:
                            st.session_state.current_dialogue_id = existing.dialogue_ids[-1]
                        st.success(f"Welcome back! Resuming from: **{stage_label}**")
                        st.rerun()
                    else:
                        st.warning(
                            "No active session found for that ID. "
                            "If you have already completed the study, thank you for your participation. "
                            "If you believe this is an error, please contact the researcher."
                        )


def render_big5_assessment():
    """Stage 2: Big5 Personality Assessment"""
    st.header("📋 Personality Assessment")

    st.markdown("""
    The following questions are designed to learn about the kinds of personality attributes you have.
    You will be presented with a series of statements describing how people may think, feel, or behave.
    For each statement, please indicate how much you agree or disagree based on how you generally are —
    there are no right or wrong answers.

    Please rate each statement on a scale of 1–5:
    - **1** = Strongly Disagree
    - **2** = Disagree
    - **3** = Neutral
    - **4** = Agree
    - **5** = Strongly Agree

    There are 50 statements in total. Please select one option for each statement before submitting.
    """)

    st.markdown("---")

    items = agents['assessment'].get_assessment_items()

    with st.form("assessment_form"):
        responses = {}

        for i, item in enumerate(items, 1):
            responses[item['id']] = st.radio(
                f"**{i}.** {item['text']}",
                options=[1, 2, 3, 4, 5],
                index=None,
                horizontal=True,
                key=f"q_{item['id']}"
            )
            if i % 10 == 0 and i < len(items):
                st.markdown("---")

        submit = st.form_submit_button("Submit Assessment", use_container_width=True)

        if submit:
            unanswered = [k for k, v in responses.items() if v is None]
            if unanswered:
                st.toast(
                    f"Almost there! Please answer all {len(unanswered)} remaining question(s) before continuing.",
                    icon="💬"
                )
                st.warning(
                    f"**Almost there!** It looks like {len(unanswered)} question(s) still need a response. "
                    "Please scroll through and make sure every item has been rated before submitting."
                )
            else:
                assessment = agents['assessment'].conduct_assessment(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.current_session.session_id,
                    responses=responses
                )

                session = st.session_state.current_session
                session.big5_assessment_id = assessment.assessment_id
                session.save(DATA_DIR)

                agents['supervisor'].advance_stage(session.session_id, WorkflowStage.TASK_SELECTION)

                st.success("✅ Assessment completed!")
                st.balloons()
                st.rerun()


PERSONALITY_LABELS = {
    "average": "⚖️ Average",
    "role_model": "⭐ Role Model",
    "self_centred": "🎯 Self-Centred",
    "reserved": "🤫 Reserved",
}

REQUIRED_TASKS = ["NOBLE INDUSTRIES for Big5.pdf", "Popcorn brain task for Big5.pdf"]


@st.cache_data
def _read_task_pdf_b64(task_name: str) -> str:
    """Read PDF as base64 string for inline embedding. Cached per session."""
    import base64
    task_path = TASK_FOLDER / task_name
    if not task_path.exists():
        return ""
    return base64.b64encode(task_path.read_bytes()).decode()


def _get_or_assign(session):
    """Return (task, personality), randomly assigning on first call and persisting in metadata."""
    if "assigned_task" not in session.metadata:
        # Validate task files exist before assigning
        if not TASK_FOLDER.exists():
            return None, None
        task_names = [t.name for t in TASK_FOLDER.glob("*.pdf")]
        missing = [t for t in REQUIRED_TASKS if t not in task_names]
        if missing:
            return None, None

        session.metadata["assigned_task"] = random.choice(REQUIRED_TASKS)
        session.metadata["assigned_personality"] = random.choice(list(PERSONALITY_LABELS.keys()))
        session.save(DATA_DIR)

    return session.metadata["assigned_task"], session.metadata["assigned_personality"]


def render_task_selection():
    """Stage 3: Show assigned task description for participant to read."""
    session = st.session_state.current_session

    # Validate task files
    if not TASK_FOLDER.exists():
        st.error("Task folder not found. Please ensure the `Task/` directory exists with the required PDFs.")
        return
    task_names = [t.name for t in TASK_FOLDER.glob("*.pdf")]
    missing = [t for t in REQUIRED_TASKS if t not in task_names]
    if missing:
        st.error(f"Required task files missing from `Task/` folder: {', '.join(missing)}")
        return

    assigned_task, assigned_personality = _get_or_assign(session)
    if not assigned_task:
        st.error("Could not assign a task. Please contact the researcher.")
        return

    task_display_name = assigned_task.replace(".pdf", "")
    st.header(f"📄 Your Task: {task_display_name}")
    st.markdown("Please read the task description carefully before beginning.")
    st.markdown("---")

    # Embed the PDF directly so all original formatting and tables are preserved
    pdf_b64 = _read_task_pdf_b64(assigned_task)
    if pdf_b64:
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
            f'width="100%" height="720px" style="border:none;border-radius:6px;"></iframe>',
            unsafe_allow_html=True
        )
    else:
        st.info("Task document loaded. Please refer to any printed materials provided.")

    st.markdown("---")
    st.info("When you have finished reading and are ready to begin, click the button below. "
            "An AI assistant will be available to help you work through the task.")

    if st.button("I have read the task — Begin", use_container_width=True, type="primary"):
        if not agents['llm_ready']:
            st.error("LLM Manager not ready. Please set ANTHROPIC_API_KEY.")
        else:
            dialogue = agents['dialogue'].start_dialogue(
                user_id=st.session_state.user_id,
                session_id=session.session_id,
                task_name=assigned_task,
                llm_personality=assigned_personality
            )

            st.session_state.current_dialogue_id = dialogue.dialogue_id
            st.session_state.current_messages = []

            session.dialogue_records.append(dialogue.dialogue_id)
            session.save(DATA_DIR)

            agents['supervisor'].advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
            st.rerun()


def render_task_dialogue():
    """Stage 4: Task Dialogue — task description at top, chat in middle, complete at bottom."""
    dialogue_id = st.session_state.current_dialogue_id
    dialogue = agents['dialogue'].get_dialogue(dialogue_id)

    if not dialogue:
        st.error("Dialogue not found")
        return

    task_display_name = dialogue.task_name.replace(".pdf", "")
    st.header(f"💬 {task_display_name}")

    # ── Task description (always accessible at top) ─────────────────────────
    pdf_b64 = _read_task_pdf_b64(dialogue.task_name)
    with st.expander("📄 Task Description (click to expand / collapse)", expanded=True):
        if pdf_b64:
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
                f'width="100%" height="500px" style="border:none;border-radius:6px;"></iframe>',
                unsafe_allow_html=True
            )
        else:
            st.info(f"Task: {task_display_name}")

    st.markdown("---")

    # ── Dialogue history (scrollable) ───────────────────────────────────────
    for msg in dialogue.messages:
        if msg.role == "user":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant", avatar="🤖").write(msg.content)

    # ── Complete Task button (below conversation) ────────────────────────────
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric("Messages exchanged", dialogue.total_messages)
    with col2:
        if st.button("Complete Task", use_container_width=True, type="primary"):
            agents['dialogue'].end_dialogue(dialogue_id)
            agents['supervisor'].advance_stage(
                st.session_state.current_session.session_id,
                WorkflowStage.TASK_RESPONSE
            )
            st.rerun()

    # ── Chat input (Streamlit renders this sticky at viewport bottom) ────────
    user_input = st.chat_input("Type your message to the AI assistant…")

    if user_input:
        agents['dialogue'].record_message(dialogue_id, "user", user_input)

        personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
        messages = [{"role": m.role, "content": m.content} for m in dialogue.messages]

        # Extract task text for LLM context (plain text fallback from PDF bytes)
        task_context = ""
        try:
            from PyPDF2 import PdfReader
            import io, base64
            raw = _read_task_pdf_b64(dialogue.task_name)
            if raw:
                pdf_bytes = base64.b64decode(raw)
                reader = PdfReader(io.BytesIO(pdf_bytes))
                task_context = "\n\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except Exception:
            task_context = dialogue.task_name.replace(".pdf", "")

        with st.spinner("AI Assistant is thinking…"):
            response = personality.chat(messages, task_context=task_context)

        agents['dialogue'].record_message(dialogue_id, "assistant", response)
        st.rerun()


def render_post_survey():
    """Stage 5: Post-Experiment Survey"""
    st.header("Post-Experiment Survey")

    st.markdown(
        "Please read each statement carefully and select the response that best reflects your experience. "
        "Use the scale: **1 = Strongly Disagree** &nbsp; **7 = Strongly Agree**"
    )
    st.markdown("---")

    dialogue_id = st.session_state.current_dialogue_id
    questions = agents['survey'].get_survey_questions()
    likert_questions = {k: v for k, v in questions.items() if v['type'] == 'likert'}
    text_questions = {k: v for k, v in questions.items() if v['type'] == 'text'}

    with st.form("survey_form"):
        responses = {}

        # Likert items — no section headers, no default selection
        for i, (key, q_data) in enumerate(likert_questions.items(), 1):
            responses[key] = st.radio(
                f"**{i}.** {q_data['question']}",
                options=[1, 2, 3, 4, 5, 6, 7],
                index=None,
                horizontal=True,
                key=f"survey_{key}"
            )
            st.markdown("")  # small vertical gap between items

        st.markdown("---")

        # Open-ended items — no section headers
        for i, (key, q_data) in enumerate(text_questions.items(), len(likert_questions) + 1):
            responses[key] = st.text_area(
                f"**{i}.** {q_data['question']}",
                placeholder=q_data.get('placeholder', ''),
                key=f"survey_{key}",
                height=120
            )

        submit = st.form_submit_button("Submit Survey", use_container_width=True, type="primary")

        if submit:
            # Validate all Likert items answered
            unanswered = [k for k in likert_questions if responses.get(k) is None]
            if unanswered:
                st.toast(
                    f"Almost there! Please answer all {len(unanswered)} remaining question(s) before continuing.",
                    icon="💬"
                )
                st.warning(
                    f"**Almost there!** It looks like {len(unanswered)} question(s) still need a response. "
                    "Please scroll through and make sure every item has been rated before submitting."
                )
            else:
                agents['survey'].conduct_survey(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.current_session.session_id,
                    dialogue_id=dialogue_id,
                    responses=responses
                )
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
    # Radio layout: number on top, circle dial below
    # st.html() injects directly into the main page (no iframe) — most reliable method
    st.html("""
<style>
/* Each option label: vertical stack, centred */
div[role="radiogroup"] > label {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 0 12px !important;
    cursor: pointer;
}
/* Circle wrapper: rendered second (bottom) */
div[role="radiogroup"] > label > div:nth-child(1) {
    order: 2 !important;
    margin: 0 !important;
}
/* Number text: rendered first (top) */
div[role="radiogroup"] > label > div:nth-child(2) {
    order: 1 !important;
    font-weight: 600;
    text-align: center !important;
}
</style>
""")

    # Admin route: ?admin=1 bypasses participant flow entirely
    if st.query_params.get("admin") == "1":
        admin_download.admin_page()
        return

    # Participant sidebar — no admin UI visible
    with st.sidebar:
        st.markdown("## Research Platform")

        if st.session_state.current_session:
            session = st.session_state.current_session
            stage_label = _STAGE_LABELS.get(session.current_stage.value, "In progress")
            st.markdown(f"**Participant ID:** `{st.session_state.user_id}`")
            st.markdown(f"**Progress:** {stage_label}")
            st.info(
                "Need to stop and return later? "
                "Simply close this window and use the **Resume Session** tab "
                f"with your ID **`{st.session_state.user_id}`** to continue where you left off."
            )
        else:
            st.info("No active session")

    # Main content
    if not st.session_state.current_session:
        render_registration()
    else:
        # Always reload session from supervisor to get authoritative current_stage
        fresh = agents['supervisor'].get_session(st.session_state.current_session.session_id)
        if fresh:
            st.session_state.current_session = fresh
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
