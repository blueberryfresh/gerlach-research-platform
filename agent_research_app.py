"""
Multi-Agent Research Application
Integrated Streamlit interface for the complete research workflow
"""

import os
import streamlit as st

# Bootstrap APP_LANG from secrets before any sub-module imports strings.py,
# so that os.environ.get("APP_LANG") works reliably at import time.
try:
    _lang = st.secrets.get("APP_LANG", "en")
    if _lang:
        os.environ.setdefault("APP_LANG", _lang)
except Exception:
    pass

import random
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
from strings import T, APP_LANG

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

if 'show_save_exit' not in st.session_state:
    st.session_state.show_save_exit = False


_STAGE_LABELS = T["stage_labels"]


def render_registration():
    """Stage 1: User Registration"""
    st.header(T["reg_header"])

    st.markdown(T["reg_intro"])

    st.markdown("---")

    tab_new, tab_resume = st.tabs([T["tab_new"], T["tab_resume"]])

    # ── New Participant ───────────────────────────────────────────────────────
    with tab_new:
        with st.form("registration_form"):
            st.markdown(T["reg_id_instruction"])

            user_id = st.text_input(
                T["reg_id_label"],
                placeholder=T["reg_id_placeholder"],
                help=T["reg_id_help"]
            )

            consent = st.checkbox(
                T["reg_consent"],
                help=T["reg_consent_help"]
            )

            submit = st.form_submit_button(T["reg_begin_btn"], use_container_width=True)

            if submit:
                if not user_id:
                    st.error(T["reg_err_no_id"])
                elif not consent:
                    st.error(T["reg_err_no_consent"])
                else:
                    existing = agents['supervisor'].find_active_session_by_user(user_id.strip())
                    if existing:
                        # Already has a session — silently resume so they don't create a duplicate
                        st.session_state.user_id = user_id.strip()
                        st.session_state.current_session = existing
                        if existing.dialogue_records:
                            st.session_state.current_dialogue_id = existing.dialogue_records[-1]
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
        st.markdown(T["resume_instructions"])

        with st.form("resume_form"):
            resume_id = st.text_input(
                T["reg_id_label"],
                placeholder=T["reg_id_placeholder"],
                key="resume_id_input"
            )
            resume_btn = st.form_submit_button(T["resume_btn"], use_container_width=True)

            if resume_btn:
                if not resume_id:
                    st.error(T["reg_err_no_id"])
                else:
                    existing = agents['supervisor'].find_active_session_by_user(resume_id.strip())
                    if existing:
                        stage_label = _STAGE_LABELS.get(existing.current_stage.value, "In progress")
                        st.session_state.user_id = resume_id.strip()
                        st.session_state.current_session = existing
                        if existing.dialogue_records:
                            st.session_state.current_dialogue_id = existing.dialogue_records[-1]
                        st.success(T["resume_success"].format(stage_label=stage_label))
                        st.rerun()
                    else:
                        st.warning(T["resume_not_found"])


def render_big5_assessment():
    """Stage 2: Big5 Personality Assessment"""
    st.header(T["big5_header"])

    st.info(T["big5_info"])

    st.markdown(T["big5_instructions"])

    st.markdown("---")

    items = agents['assessment'].get_assessment_items()

    with st.form("assessment_form"):
        responses = {}
        item_numbers = {}  # id -> display number

        for i, item in enumerate(items, 1):
            item_numbers[item['id']] = i
            responses[item['id']] = st.radio(
                f"**{i}.** {item['text']}",
                options=[1, 2, 3, 4, 5],
                index=None,
                horizontal=True,
                key=f"q_{item['id']}"
            )
            if i % 10 == 0 and i < len(items):
                st.markdown("---")

        submit = st.form_submit_button(T["big5_submit_btn"], use_container_width=True)

        if submit:
            unanswered = [k for k, v in responses.items() if v is None]
            if unanswered:
                nums = sorted(item_numbers[k] for k in unanswered)
                nums_str = ", ".join(str(n) for n in nums)
                st.toast(
                    T["big5_toast_unanswered"].format(nums_str=nums_str),
                    icon="💬"
                )
                st.warning(T["big5_warning_unanswered"].format(nums_str=nums_str))
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

                st.success(T["big5_success"])
                st.balloons()
                st.rerun()


PERSONALITY_LABELS = {
    "average": "⚖️ Average",
    "role_model": "⭐ Role Model",
    "self_centred": "🎯 Self-Centred",
    "reserved": "🤫 Reserved",
}

REQUIRED_TASKS = ["NOBLE INDUSTRIES for Big5.pdf", "Popcorn Brain Task for Big5-rev2.pdf"]
POPCORN_TASK = "Popcorn Brain Task for Big5-rev2.pdf"


def _format_task_content(task_name: str, raw: str) -> str:
    """Return localised, well-formatted markdown for each task."""
    if not raw:
        return raw

    if task_name == POPCORN_TASK:
        return T["task_popcorn_md"]

    elif task_name == "NOBLE INDUSTRIES for Big5.pdf":
        return T["task_noble_md"]

    return raw


@st.cache_data
def _read_task_content(task_name: str) -> str:
    """Extract text + tables from PDF using pdfplumber.
    Tables are rendered as markdown tables; all other text is plain markdown."""
    task_path = TASK_FOLDER / task_name
    if not task_path.exists():
        return ""
    try:
        import pdfplumber
        output = []
        with pdfplumber.open(str(task_path)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                # Crop away table regions so text extraction doesn't duplicate them
                cropped = page
                for table_obj in page.find_tables():
                    cropped = cropped.outside_bbox(table_obj.bbox)
                text = cropped.extract_text() or ""
                if text.strip():
                    output.append(text.strip())
                for table in tables:
                    if not table or not table[0]:
                        continue
                    header = [str(c or "").strip() for c in table[0]]
                    rows   = [[str(c or "").strip() for c in row] for row in table[1:]]
                    md  = "| " + " | ".join(header) + " |\n"
                    md += "| " + " | ".join(["---"] * len(header)) + " |\n"
                    for row in rows:
                        md += "| " + " | ".join(row) + " |\n"
                    output.append(md)
        return "\n\n".join(output)
    except Exception:
        # Fallback to plain PyPDF2 extraction
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(task_path))
            return "\n\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except Exception:
            return ""


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
        st.error(T["task_sel_err_folder"])
        return
    task_names = [t.name for t in TASK_FOLDER.glob("*.pdf")]
    missing = [t for t in REQUIRED_TASKS if t not in task_names]
    if missing:
        st.error(T["task_sel_err_files_missing"])
        return

    assigned_task, assigned_personality = _get_or_assign(session)
    if not assigned_task:
        st.error(T["task_sel_err_assign"])
        return

    st.header(T["task_sel_header"])
    st.markdown(T["task_sel_subtitle"])
    st.markdown("---")

    # Render text normally; tables detected by pdfplumber are formatted as markdown tables
    task_content = _read_task_content(assigned_task)
    formatted   = _format_task_content(assigned_task, task_content)
    if formatted:
        st.markdown(formatted, unsafe_allow_html=True)
    else:
        st.info(T["task_sel_no_content"])

    st.markdown("---")
    st.info(T["task_sel_begin_info"])

    if st.button(T["task_sel_begin_btn"], use_container_width=True, type="primary"):
        if not agents['llm_ready']:
            st.error(T["task_sel_err_no_llm"])
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
        st.error(T["task_dial_err_not_found"])
        return

    # Generate a one-time welcome message when the dialogue is brand new
    if len(dialogue.messages) == 0 and agents['llm_ready']:
        personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
        task_context = _read_task_content(dialogue.task_name) or dialogue.task_name.replace(".pdf", "")
        welcome_prompt = [{
            "role": "user",
            "content": T["task_dial_welcome_prompt"]
        }]
        with st.spinner(T["task_dial_spinner_welcome"]):
            welcome = personality.chat(welcome_prompt, task_context=task_context)
        agents['dialogue'].record_message(dialogue_id, "assistant", welcome)
        st.rerun()

    st.header(T["task_dial_header"])

    # ── Task description (always accessible at top) ─────────────────────────
    with st.expander(T["task_dial_expander"], expanded=True):
        task_content = _read_task_content(dialogue.task_name)
        formatted    = _format_task_content(dialogue.task_name, task_content)
        if formatted:
            st.markdown(formatted, unsafe_allow_html=True)
        else:
            st.info(T["task_dial_no_desc"])

    st.markdown("---")

    # ── Dialogue history (scrollable) ───────────────────────────────────────
    for msg in dialogue.messages:
        if msg.role == "user":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant", avatar="🤖").write(msg.content)

    # ── Complete Task button (below conversation) ────────────────────────────
    st.markdown("---")
    st.warning(T["task_dial_warning"])
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(T["task_dial_messages_metric"], dialogue.total_messages)
    with col2:
        if st.button(T["task_dial_complete_btn"], use_container_width=True, type="primary"):
            agents['dialogue'].end_dialogue(dialogue_id)
            agents['supervisor'].advance_stage(
                st.session_state.current_session.session_id,
                WorkflowStage.TASK_RESPONSE
            )
            st.rerun()

    # ── Collaboration guide (at bottom, always visible) ──────────────────────
    with st.expander(T["task_dial_guide_expander"], expanded=True):
        st.markdown(T["task_dial_guide"])

    # ── Chat input (Streamlit renders this sticky at viewport bottom) ────────
    user_input = st.chat_input(T["task_dial_chat_placeholder"])

    if user_input:
        agents['dialogue'].record_message(dialogue_id, "user", user_input)

        personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
        messages = [{"role": m.role, "content": m.content} for m in dialogue.messages]

        # Reuse cached extraction — already handles tables and plain text
        task_context = _read_task_content(dialogue.task_name) or dialogue.task_name.replace(".pdf", "")

        with st.spinner(T["task_dial_spinner_thinking"]):
            response = personality.chat(messages, task_context=task_context)

        agents['dialogue'].record_message(dialogue_id, "assistant", response)
        st.rerun()


def render_post_survey():
    """Stage 5: Post-Task Survey"""
    st.header(T["survey_header"])

    st.markdown(T["survey_instructions"])
    st.markdown("---")

    dialogue_id = st.session_state.current_dialogue_id
    questions = agents['survey'].get_survey_questions()
    likert_questions = {k: v for k, v in questions.items() if v['type'] == 'likert'}
    text_questions = {k: v for k, v in questions.items() if v['type'] == 'text'}

    with st.form("survey_form"):
        responses = {}

        # Likert items — no section headers, no default selection
        survey_item_numbers = {}  # key -> display number
        for i, (key, q_data) in enumerate(likert_questions.items(), 1):
            survey_item_numbers[key] = i
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

        submit = st.form_submit_button(T["survey_submit_btn"], use_container_width=True, type="primary")

        if submit:
            # Validate all Likert items answered
            unanswered = [k for k in likert_questions if responses.get(k) is None]
            if unanswered:
                nums = sorted(survey_item_numbers[k] for k in unanswered)
                nums_str = ", ".join(str(n) for n in nums)
                st.toast(
                    T["survey_toast_unanswered"].format(nums_str=nums_str),
                    icon="💬"
                )
                st.warning(T["survey_warning_unanswered"].format(nums_str=nums_str))
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
    """Stage 6: Session Completed"""
    st.header(T["completed_header"])

    st.success(T["completed_success"])

    st.markdown("---")


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

    # If admin panel is active, render it and skip participant UI
    if st.session_state.get("show_admin_page"):
        admin_download.admin_page()
        with st.sidebar:
            st.markdown("---")
            if st.button(T["sidebar_back_btn"], use_container_width=True):
                st.session_state.show_admin_page = False
                st.rerun()
        return

    # Participant sidebar
    with st.sidebar:
        st.markdown(T["sidebar_header"])

        if st.session_state.current_session:
            session = st.session_state.current_session
            stage_label = _STAGE_LABELS.get(session.current_stage.value, "In progress")
            st.markdown(T["sidebar_participant_id_label"])
            st.markdown(f"<span style='font-size:1.6rem;font-weight:700;letter-spacing:0.05em;'>{st.session_state.user_id}</span>", unsafe_allow_html=True)
            st.markdown(T["sidebar_progress_label"].format(stage_label=stage_label))
            st.markdown("---")

            # Always-visible instructions
            st.info(T["sidebar_need_to_stop"])
            st.info(T["sidebar_returning"].format(user_id=st.session_state.user_id))
            st.markdown("---")

            if st.button(T["sidebar_reload_btn"], use_container_width=True, key="reload_page"):
                fresh = agents['supervisor'].find_active_session_by_user(st.session_state.user_id)
                if fresh:
                    st.session_state.current_session = fresh
                    if fresh.dialogue_records:
                        st.session_state.current_dialogue_id = fresh.dialogue_records[-1]
                st.rerun()

            if st.button(T["sidebar_save_exit_btn"], use_container_width=True):
                st.session_state.show_save_exit = True

            if st.session_state.get("show_save_exit"):
                st.success(T["sidebar_saved_msg"].format(user_id=st.session_state.user_id))
                if st.button(T["sidebar_close_btn"], key="close_save_exit"):
                    st.session_state.show_save_exit = False
                    st.rerun()
        else:
            st.info(T["sidebar_no_session"])

        # Admin button — bottom of sidebar, small and unobtrusive
        st.markdown("<br>" * 3, unsafe_allow_html=True)
        st.markdown("---")
        if st.button(T["sidebar_admin_btn"], use_container_width=False, key="admin_entry"):
            st.session_state.show_admin_page = True
            st.rerun()

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
