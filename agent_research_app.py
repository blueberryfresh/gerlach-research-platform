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
from github_storage import sync_from_github

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
    """Initialize all agents. Bump _cache_version when LLM classes change to force reinitialization."""
    _cache_version = "2026-03-27"  # noqa: F841
    supervisor = SupervisorAgent(DATA_DIR)  # creates local subdirectories
    sync_from_github(DATA_DIR)             # restore any GitHub data on fresh deploy
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

if 'ko_consent_given' not in st.session_state:
    st.session_state.ko_consent_given = False

if 'ko_consent_declined' not in st.session_state:
    st.session_state.ko_consent_declined = False


_STAGE_LABELS = T["stage_labels"]


def render_korean_welcome():
    """Korean-only: IRB consent/welcome page shown before registration."""
    st.markdown("## 연구 참여 안내 및 동의서")

    # Declined state — show exit message only
    if st.session_state.ko_consent_declined:
        st.error(
            "연구 참여에 동의하지 않으셨습니다. 참여해 주셔서 감사합니다. "
            "브라우저 창을 닫으셔도 됩니다."
        )
        return

    welcome_text = """
안녕하세요. 본 연구에 참여해주셔서 감사합니다.
연구 참가 시작 전, 본 연구에 대해 설명드리도록 하겠습니다.

**1. 연구의 배경과 목적**
본 연구는 인공지능(AI) 챗봇과의 협업 과제 수행 경험이 사용자의 만족도 및 결과물 인식에 어떠한 영향을 미치는지를 탐색하는 연구입니다.

**2. 연구대상자의 참여 기간, 절차 및 소요 시간**
연구 시작일로부터 일주일간 참여가능하며, 소요 시간은 약 20~30분 정도입니다. 모든 절차는 참여자 본인의 기기를 통해 온라인으로 진행되며, 모집 공고에 안내된 QR코드 또는 링크를 통해 접속하여 순서에 따라 진행됩니다.

**3. 연구대상자에게 예상되는 위험 및 이익**
본 연구는 온라인 설문 응답 및 AI 챗봇과의 협업 과제 수행으로만 구성되어 있으며, 참여자에게 신체적·심리적 위험은 없습니다. 다만 설문 응답 및 과제 수행에 약 20~30분의 시간이 소요되는 점이 경미한 불편함으로 작용할 수 있습니다. 또한 참여자 개인에게 직접적인 이익은 없습니다. 다만 본 연구의 결과는 사용자 맞춤형 AI 시스템 설계 및 인간-AI 협업 경험 개선을 위한 학술적 기초 자료로 활용될 것으로 기대됩니다.

**4. 연구참여에 대한 보상**
본 연구 참여를 완료한 참여자 전원에게 스타벅스 1만원 모바일 기프티콘이 제공됩니다. 참여자는 언제든지 불이익 없이 참여를 중단할 수 있습니다. 단, 보상은 설문 및 과제 수행을 모두 완료한 참여자에 한하여 지급되며, 중도 철회 시에는 보상이 제공되지 않습니다. 보상 지급을 위해 참여자의 핸드폰 번호를 별도로 수집하며, 보상 지급 후 즉시 폐기됩니다. 해당 정보는 보상 지급 외의 목적으로는 사용되지 않으며, 연구 데이터와 분리하여 관리됩니다.

**5. 연구 참여에 따른 손실에 대한 보상**
본 설문 연구에 참가에 따른 예상되는 위험, 손실 및 상해는 없습니다. 추가적인 정보나 설명을 원할 경우를 대비하여 담당 연구원의 전화 번호 및 이메일이 제공될 것입니다.

**6. 참여 철회 및 중지 보장**
귀하는 본 연구 참가 진행 도중 언제든지 중도에 참여를 철회 및 중지 할 수 있으며, 이로 인한 어떠한 불이익도 없습니다. 참여 포기 시, 개인의 자료 및 정보는 즉시 삭제되며, 자료가 보관되거나 분석에 사용되지 않습니다. 또한 중도 철회 시에는 보상이 지급되지 않습니다.

**7. 개인정보와 비밀 보장에 관한 사항**
연구에서는 개인을 특정할 수 있는 정보 (이름, 주민등록번호 등)을 수집하지 않으며, 통계적인 분석에 사용될 간단한 인구통계학적 정보 성별과 전공만을 수집합니다.

수집된 데이터는 연구책임자 관리 하에 컴퓨터의 데이터 파일(엑셀 혹은 SPSS 데이터 파일 형식)로 연구실 내 통계 자료 분석용 컴퓨터에 저장될 것이며, 연구가 종료 된 후 3년 보관 후 관련 전자 문서는 영구 삭제할 것이며, 인쇄 문서는 파기할 것입니다. 또한 통계 분석은 연구실 내에서만 이루어집니다. 이 연구에서 얻어진 개인 정보가 학회지나 학회에 공개 될 때 응답자의 이름과 다른 개인 정보는 사용되지 않습니다. 연구대상자의 참여가 중지되거나 철회될 경우 연구대상자의 자료 및 정보는 즉시 폐기될 것입니다.

보상 지급을 위해 필요한 최소한의 개인정보(예: 연락처)는 별도로 수집되며, 연구 데이터와 분리하여 관리됩니다. 해당 정보는 보상 지급 목적에 한하여 사용되며, 연구책임자만 접근 가능하도록 제한됩니다. 보상 지급이 완료된 후 즉시 삭제되며, 연구 데이터와 결합되어 분석에 사용되지 않습니다.

**8. 연구 문의**
본 연구와 관련하여 문의할 사항이 있으시면 아래 연락처로 연락주시기 바랍니다.

- **연구담당자 연락처**
  연세대학교 경영대 연구실 (010-3460-0613)
  연구자 임일 (il.im@yonsei.ac.kr)

- **연구대상자 권리 정보에 관한 문의처**
  연세대학교 생명윤리위원회 (02-2123-5143)
"""
    st.markdown(welcome_text)

    st.markdown("---")
    st.markdown(
        "위의 연구 설명을 아래 항목에 동의하는지, 혹은 동의하지 않는지 응답해 주십시오.  \n"
        "**모든 항목에 동의하셔야 연구에 참여하실 수 있습니다.**"
    )
    st.markdown("")

    consent1 = st.radio(
        "본 연구의 연구 목적을 이해하고 연구에 참여하기를 희망합니다.",
        options=["동의한다", "동의하지 않는다"],
        index=None,
        horizontal=True,
        key="ko_consent_item1",
    )
    consent2 = st.radio(
        "연구 도중 자유롭게 참여를 철회할 수 있음을 이해하였습니다.",
        options=["동의한다", "동의하지 않는다"],
        index=None,
        horizontal=True,
        key="ko_consent_item2",
    )

    st.markdown("")
    if st.button("확인", type="primary", use_container_width=False):
        if consent1 is None or consent2 is None:
            st.warning("모든 항목에 응답해 주십시오.")
        elif consent1 == "동의하지 않는다" or consent2 == "동의하지 않는다":
            st.session_state.ko_consent_declined = True
            st.rerun()
        else:
            st.session_state.ko_consent_given = True
            st.rerun()


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

    if T.get("big5_info"):
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
NOBLE_TASK   = "NOBLE INDUSTRIES for Big5.pdf"

_NOBLE_TABLE_INSTRUCTION = """
FINAL ORDER TABLE INSTRUCTION:
When you and the participant have reached final agreement on the layoff order, present a markdown table summarising the agreed order from first to last laid off. Use exactly this format:

| Order | Employee | Reason |
|-------|----------|--------|
| 1st   | [Name]   | [Brief reason] |
| 2nd   | [Name]   | [Brief reason] |

Present this table only once, after the participant has explicitly confirmed they are satisfied with the complete order. Do not present the table until that confirmation.
"""


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
    """Stage 3: Silently assign task + create dialogue, then advance to TASK_DIALOGUE."""
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

    if not agents['llm_ready']:
        st.error(T["task_sel_err_no_llm"])
        return

    with st.spinner(T.get("task_sel_loading", "Loading your task…")):
        dialogue = agents['dialogue'].start_dialogue(
            user_id=st.session_state.user_id,
            session_id=session.session_id,
            task_name=assigned_task,
            llm_personality=assigned_personality
        )

        st.session_state.current_dialogue_id = dialogue.dialogue_id
        st.session_state.current_messages = []

        # Write static welcome message — no API call needed, text is predetermined
        agents['dialogue'].record_message(dialogue.dialogue_id, "assistant", T["task_dial_welcome_text"])

        session.dialogue_records.append(dialogue.dialogue_id)
        session.save(DATA_DIR)

        agents['supervisor'].advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
    st.rerun()


def render_task_dialogue():
    """Stage 4: Task Dialogue — task description at top, chat in middle, complete at bottom."""
    dialogue_id = st.session_state.current_dialogue_id

    # ── Render page structure FIRST — no early returns before this point ───────
    st.header(T["task_dial_header"])

    if not dialogue_id:
        st.error(T["task_dial_err_not_found"])
        return

    dialogue = agents['dialogue'].get_dialogue(dialogue_id)

    if not dialogue:
        st.error(T["task_dial_err_not_found"])
        return

    try:

        # ── Task description (always accessible at top) ─────────────────────
        with st.expander(T["task_dial_expander"], expanded=True):
            task_content = _read_task_content(dialogue.task_name)
            formatted    = _format_task_content(dialogue.task_name, task_content)
            if formatted:
                st.markdown(formatted, unsafe_allow_html=True)
            else:
                st.info(T["task_dial_no_desc"])

        st.markdown("---")

        # ── Collaboration guide (above dialogue) ─────────────────────────────
        with st.expander(T["task_dial_guide_expander"], expanded=True):
            st.markdown(T["task_dial_guide"])

        st.markdown("---")

        # Safety net: write static welcome if task setup somehow left messages empty
        if len(dialogue.messages) == 0:
            agents['dialogue'].record_message(dialogue_id, "assistant", T["task_dial_welcome_text"])
            st.rerun()

        # ── Dialogue history (at bottom, just above complete button) ─────────
        for msg in dialogue.messages:
            if msg.role == "user":
                st.chat_message("user").write(msg.content)
            else:
                st.chat_message("assistant", avatar="🤖").write(msg.content)

        # ── Complete Task button (last on page) ───────────────────────────────
        st.markdown("---")
        st.warning(T["task_dial_warning"])

        is_noble = dialogue.task_name == NOBLE_TASK
        if is_noble:
            confirmed = st.checkbox(
                T["task_dial_noble_confirm_label"],
                key=f"noble_confirm_{dialogue_id}"
            )
        else:
            confirmed = True

        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric(T["task_dial_messages_metric"], dialogue.total_messages)
        with col2:
            if st.button(T["task_dial_complete_btn"], use_container_width=True, type="primary"):
                if dialogue.user_message_count == 0:
                    st.toast(T["task_dial_no_messages_warning"])
                    st.warning(T["task_dial_no_messages_warning"])
                elif not confirmed:
                    st.toast(T["task_dial_noble_confirm_warning"])
                    st.warning(T["task_dial_noble_confirm_warning"])
                else:
                    agents['dialogue'].end_dialogue(dialogue_id)
                    agents['supervisor'].advance_stage(
                        st.session_state.current_session.session_id,
                        WorkflowStage.TASK_RESPONSE
                    )
                    st.rerun()

        # ── Chat input (Streamlit renders this sticky at viewport bottom) ────
        st.caption(T["task_dial_offtopic_reminder"])
        user_input = st.chat_input(T["task_dial_chat_placeholder"])

        if user_input:
            if not agents['llm_ready']:
                st.error(T.get("task_dial_err_llm", "The AI assistant could not be reached. Please refresh the page to try again."))
            else:
                agents['dialogue'].record_message(dialogue_id, "user", user_input)

                personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
                # Reload dialogue after record_message to get the authoritative current state.
                # This works whether the dialogue lives in active_dialogues (same object, already
                # updated) or was loaded from disk (record_message saved the new message to disk,
                # reload picks it up). Avoids duplicating the user message.
                # Anthropic also requires messages[0].role == "user", so strip leading assistant turns.
                fresh = agents['dialogue'].get_dialogue(dialogue_id)
                all_msgs = [{"role": m.role, "content": m.content} for m in (fresh or dialogue).messages]
                first_user = next((i for i, m in enumerate(all_msgs) if m["role"] == "user"), None)
                messages = all_msgs[first_user:] if first_user is not None else all_msgs

                # Reuse cached extraction — already handles tables and plain text
                task_context = _read_task_content(dialogue.task_name) or dialogue.task_name.replace(".pdf", "")
                if dialogue.task_name == NOBLE_TASK:
                    task_context += _NOBLE_TABLE_INSTRUCTION

                try:
                    with st.spinner(T["task_dial_spinner_thinking"]):
                        response = personality.chat(messages, task_context=task_context,
                            _monitor_meta={"session_id": st.session_state.current_session.session_id,
                                           "dialogue_id": dialogue_id})
                    agents['dialogue'].record_message(dialogue_id, "assistant", response)
                    st.rerun()
                except Exception:
                    st.error(T.get("task_dial_err_llm", "The AI assistant could not be reached. Please refresh the page to try again."))

    except Exception:
        st.error(T["task_dial_err_not_found"])


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
                survey = agents['survey'].conduct_survey(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.current_session.session_id,
                    dialogue_id=dialogue_id,
                    responses=responses
                )
                # Write survey_id back to session so CSV export and reports can find it
                session = st.session_state.current_session
                session.survey_id = survey.survey_id
                session.save(DATA_DIR)
                agents['supervisor'].advance_stage(
                    session.session_id,
                    WorkflowStage.COMPLETED
                )
                st.rerun()


def _render_phone_collection():
    """Phone number input for Starbucks gift card compensation."""
    import json as _json
    session = st.session_state.current_session
    comp_file = DATA_DIR / "compensation" / f"{session.session_id}.json"

    # Already submitted — show confirmation without re-rendering the form
    if st.session_state.get("phone_submitted") or comp_file.exists():
        st.session_state["phone_submitted"] = True
        st.success(T["completed_phone_submitted"])
        return

    st.caption(T["completed_phone_notice"])
    phone = st.text_input(
        T["completed_phone_label"],
        placeholder=T["completed_phone_placeholder"],
        key="phone_input",
    )
    if st.button(T["completed_phone_btn"], key="phone_submit_btn"):
        if not phone.strip():
            st.warning(T["completed_phone_empty_warn"])
        else:
            comp_dir = DATA_DIR / "compensation"
            comp_dir.mkdir(parents=True, exist_ok=True)
            comp_data = {
                "user_id": session.user_id,
                "session_id": session.session_id,
                "phone_number": phone.strip(),
                "submitted_at": datetime.now().isoformat(),
            }
            with open(comp_file, "w", encoding="utf-8") as f:
                _json.dump(comp_data, f, indent=2, ensure_ascii=False)
            try:
                from github_storage import get_storage
                get_storage().write(f"compensation/{session.session_id}.json", comp_data)
            except Exception:
                pass
            st.session_state["phone_submitted"] = True
            st.rerun()


def render_completed():
    """Stage 6: Session Completed"""
    st.header(T["completed_header"])

    # Reveal participant and LLM personality types
    try:
        session = st.session_state.current_session
        llm_key = session.metadata.get("assigned_personality", "")
        llm_type = llm_key.replace("_", " ").title() if llm_key else ""

        participant_type = ""
        if session.big5_assessment_id and agents.get("big5"):
            assessment = agents["big5"].get_assessment(session.big5_assessment_id)
            if assessment and assessment.gerlach_type:
                participant_type = assessment.gerlach_type.replace("_", " ").title()

        if participant_type and llm_type and T.get("completed_personality_reveal"):
            st.info(T["completed_personality_reveal"].format(
                participant_type=participant_type,
                llm_type=llm_type,
            ))
    except Exception:
        pass

    _render_phone_collection()

    st.success(T["completed_success"])

    if T.get("completed_close_browser"):
        st.info(T["completed_close_browser"])

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

            st.info(T["sidebar_blank_page_tip"])

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
        if APP_LANG == "ko" and not st.session_state.ko_consent_given:
            render_korean_welcome()
        else:
            render_registration()
    else:
        try:
            # Always reload session from supervisor to get authoritative current_stage
            fresh = agents['supervisor'].get_session(st.session_state.current_session.session_id)
            if fresh:
                st.session_state.current_session = fresh
            session = st.session_state.current_session

            # Restore current_dialogue_id from session if lost (e.g. page refresh, browser resume)
            if not st.session_state.get('current_dialogue_id') and session.dialogue_records:
                st.session_state.current_dialogue_id = session.dialogue_records[-1]

            if session.current_stage == WorkflowStage.REGISTRATION:
                # Session exists but stuck at registration — advance to Big5 automatically.
                # This happens when GitHub restores a stale session file that was saved
                # before advance_stage() persisted the BIG5_ASSESSMENT transition.
                agents['supervisor'].advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
                st.session_state.current_session = agents['supervisor'].get_session(session.session_id)
                render_big5_assessment()
            elif session.current_stage == WorkflowStage.BIG5_ASSESSMENT:
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
        except Exception as _exc:
            import traceback as _tb
            st.error(T.get("task_dial_err_llm", "Something went wrong. Please refresh the page."))
            with st.expander("🔧 Error details (for researcher)"):
                st.code(_tb.format_exc())


if __name__ == "__main__":
    main()
