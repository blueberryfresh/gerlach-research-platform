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

if 'show_save_exit' not in st.session_state:
    st.session_state.show_save_exit = False


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
                        if existing.dialogue_records:
                            st.session_state.current_dialogue_id = existing.dialogue_records[-1]
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

        submit = st.form_submit_button("Submit Assessment", use_container_width=True)

        if submit:
            unanswered = [k for k, v in responses.items() if v is None]
            if unanswered:
                nums = sorted(item_numbers[k] for k in unanswered)
                nums_str = ", ".join(str(n) for n in nums)
                st.toast(
                    f"Almost there! Please answer question(s): {nums_str}",
                    icon="💬"
                )
                st.warning(
                    f"**Almost there!** The following item(s) still need a response: "
                    f"**{nums_str}**. Please scroll up and rate each one before submitting."
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

REQUIRED_TASKS = ["NOBLE INDUSTRIES for Big5.pdf", "Popcorn Brain Task for Big5-rev2.pdf"]
POPCORN_TASK = "Popcorn Brain Task for Big5-rev2.pdf"


def _format_task_content(task_name: str, raw: str) -> str:
    """Return hardcoded, well-formatted markdown for each task."""
    if not raw:
        return raw

    if task_name == POPCORN_TASK:
        return """\
Thank you for your participation. Please read the task description below carefully. You may want to read it \
twice to be clear. After that, start engaging a conversation with the LLM in discussing and collaborating for \
a most optimal solution. After you both have come to an agreement, click the 'complete' button on the bottom \
of the screen to finish the session. Your conversation will be saved for the researchers.

Please put in your best effort to generate a genuinely good and effective solution.

---

### Task Description

Fresno unified school district superintendent, Mr. Johnson is mulling over a new district-wide policy that will address the student-friendly and effective learning environment by utilizing digital technology, specifically AI-based applications and tools. The state governor's office is pushing for "smart classroom" initiative where the governor believes that it will strengthen the student scholastic achievement.

One of the initiative plans is to implement smart technologies such as AI-applications and devices in K-12 classroom. This includes replacing paperback textbook with digital device, interactive AI-based workbooks. The benefits of using AI in place of traditional materials are: 1) student can access dynamic 3D hyper-text, -image, -model, and moving images for better viewing and understanding, 2) student can interact with instructor and other students simultaneously for in-class group collaboration or for homework assignments, 3) it allows student to cover more materials and access more in-depth than the traditional approach.

On the other side, Parent-Teacher Organization (PTO) is raising a substantial concern about down side — *growing memory loss by depending too much on digital technologies' data storage service*. This syndrome speaks about how a human brain gradually lose its memory function and capacity as we continue to rely on digital devices in storing and retrieving much of our information. One of the recommendations is to use less of AI-based digital devices and technologies to balance the habitual dependency. The PTO is asking a more appropriate, implementable, and effective use of AI tools in the light of this concern.

Under these circumstances, you and your LLM are asked to work on a master plan to address this dilemma and find ways to enhance the student learning without sacrificing student's memory. Some questions to think about: What are some of creative ideas? Are the ideas realistic? With an idea, what are the action items? How do you satisfy the student's wish to use more AI but addressing the parents' concern? What is the teacher's role here? Should Math, Science, and English courses be different in the use of the AI devices? How? What about the school policies?
"""

    elif task_name == "NOBLE INDUSTRIES for Big5.pdf":
        return """\
Thank you for your participation. Please read the task description below carefully. You may want to read it \
twice to be clear. After that, start engaging a conversation with the LLM in discussing and collaborating for \
a most optimal solution. After you both have come to an agreement, click the 'complete' button on the bottom \
of the screen to finish the session. Your conversation will be saved for the researchers. Please put in your \
best effort to generate a genuinely good and effective solution.

---

### Task Description

Noble Industries is a mid-sized, diversified manufacturing firm with corporate headquarters located in Columbus, Ohio. The company was founded in 1958 and has experienced steady and continuous growth for most of its forty-year history. Eight manufacturing facilities are located in different parts of the United States and each plant employs approximately 250 people. Gross revenues for Noble Industries in 1997 were $105 million.

The Information Systems Division (ISD) at Noble Industries is functionally distributed throughout the organization. Each plant is responsible for developing and supporting its own local IS operations (for example, ordering, production scheduling, quality assurance, decision support, etc.). All corporate-wide systems (human resources, sales forecasting, research, executive information, etc.) are managed from the central Information Systems Division at corporate headquarters. A total of 150 people are employed in the Information Systems Division (ISD).

After graduating from college in 1988 you were hired as a junior programmer at the Columbus, Ohio site. Five years later you were promoted to the position of systems analyst. Now you are a senior systems analyst in ISD. Your group is responsible for application development and software support for the Research and Development Division (RDD). There are two systems analysts, four applications programmers, and 2 clerical support staff who report directly to you.

This morning, you and the other senior systems analysts at corporate headquarters met with Bob Thompson, Vice President for Information Systems. He explained, "At yesterday's Executive Management meeting it was announced that some of our durable goods customers have found new suppliers. Based on the loss in sales, our V.P. for Finance has projected a 3-6% decline in gross revenue this year. The CEO said that unless sales increase very soon we will have to make staff reductions. All Division Vice Presidents have been asked to develop a preliminary list of people who would be laid off. For ISD, at least one and perhaps as many as ten staff members could be terminated. The final decision will be made next week."

Bob then distributed envelopes marked "Confidential". He said, "In each envelope you will find profile information on ten information systems employees. I want you to take the envelopes back to your office, read the profile and supervisor's comments, then rank the employees in the order that you think they should be laid off. Also write down the reasons for your ranking. The employees' real names don't appear on the profile page because I don't want you to have to make a decision about someone you know. As these are all good employees who have been performing well, management felt it wanted a rating by an impartial group of technical peers as input to their final decision. Use your best judgement. Then I want you to get together as a group later on today, discuss your individual rankings, and submit a final ranking and the reasons for the ranking to me by the end of the day."

Bob concluded the meeting by saying, "I understand this is not an easy task, but given the current situation we don't have any other choice." At that point, you and the other senior systems analysts went back to your offices to work on the ranking assignment.

---

### Employee Profile

| Name | Age | Title | Years with Co. | Education (highest degree) | School or College | Marital Status | Number of Dependents |
|------|:---:|-------|:--------------:|:--------------------------:|-------------------|:--------------:|:--------------------:|
| Barbara | 27 | Senior Systems Analyst | 2 | MBA | Stanford Univ. | Single | 0 |
| Chris | 35 | Systems Analyst | 10 | BS - MIS | U. of Oklahoma | Married | 4 |
| Fred | 61 | Systems Programmer | 27 | DP School | DeVry Tech. | Married | 1 |
| Harry | 27 | Applications Programmer | 4 | BS - CIS | Univ. of Bombay | Single | 3 |
| Joanne | 46 | Senior Systems Analyst | 15 | MS - MIS | Ohio State Univ. | Married | 2 |
| Lois | 54 | Database Administrator | 22 | AAS - DP | Miami Dade CC | Widowed | 0 |
| Phil | 26 | Systems Analyst | 3 | BS - CIS | Natl. Taiwan Univ. | Single | 1 |
| Sharon | 36 | Clerical | 12 | High Sch. | Harrison H.S. | Married | 6 |
| Susan | 51 | Applications Programmer | 9 | BS - CIS | Texas A&M Univ. | Divorced | 3 |
| Tom | 47 | Senior Systems Analyst | 18 | BS - Mgmt. | Purdue Univ. | Divorced | 4 |

---

### Supervisors' Comments

**Barbara:** "Barbara is very ambitious and always asks for the most challenging assignments. She believes that hard work should be recognized and rewarded. For example, at both annual performance evaluations Barbara has wanted to know when she will be considered for a promotion. She defines success in terms of position and salary. Barbara is very competitive and I suspect that she will move up in the management ranks. My only concern is that sometimes she can be too assertive."

**Chris:** "Of all the people in my department, Chris responds the quickest when I give him an assignment and he never asks why I want something done. Chris respects authority and understands that everyone needs to know their place in the organizational hierarchy. He doesn't mind bureaucracy because he knows it improves efficiency. Maybe that's why Chris enjoyed being in the army for eight years."

**Fred:** "Fred has been with us for a long time. He enjoys his work and is grateful for the job security he's had here all these years. Fred gets along with everyone and gets a lot of satisfaction out of helping others, especially some of the newer employees when they have questions. He recognizes that it's important for people who work together to agree on things. Fred doesn't like controversy, so he is willing to compromise when others disagree with him."

**Harry:** "Harry is the most technically competent guy in my department. He reads every technical report he can get his hands on. However, Harry likes doing things his own way and prefers to work alone. In this way, Harry believes that it will be easier for me, his supervisor, to reward him for the work he does without anyone else getting any credit. His priorities are very clear, he puts himself and his family above everything else in his life."

**Joanne:** "Joanne has excellent organizational skills. She understands that we need to have rules and the rules need to be followed. Joanne is the department's quality assurance leader (QAL) because she believes that order and structure are necessary for productivity. She doesn't take any unnecessary risks, and thoroughly researches something before making a recommendation to me."

**Lois:** "Lois is a real team player. She really enjoys working with others and always puts the group's interests ahead of her own. In fact, when the new database conversion was completed she suggested that the whole group be recognized for the achievement even though Lois did most of the work. I know that community service is also important to Lois. She is a volunteer at the local shelter for the homeless."

**Phil:** "Although he's only twenty-six years old, Phil tends to live his life as if he were much older. He likes to study history and the way people lived in the past. Last year when Phil's mother became ill he moved back home to take care of her. Phil has a great respect for other people and will defend them when they are being criticized, whether the criticism is justified or not."

**Sharon:** "Sharon is very dedicated. She comes to work early, usually stays late, and always completes every assignment no matter how long it takes. Sharon places a great deal of emphasis on her relationships with others. Her long-term goal is to retire in Florida, so she tries to save as much money as she can."

**Susan:** "I have known Susan for about seven years, ever since she started working here. She gets her work done and thinks that everyone should do their fair share. In fact, Susan once told an assistant plant supervisor who was visiting our plant that he should try doing her job for a day. I give Susan a lot of credit, she speaks her mind and doesn't care if you're the CEO or the mail room clerk. To her, no one is any better than anybody else."

**Tom:** "Tom is always the first to try something new. It doesn't make any difference whether it's a radio station, a place to vacation, or a style of clothes. Tom does things his own way and he's not afraid to break the rules. With me, Tom is the same way. So I generally give him the assignments that have a big risk, but potentially a big payoff."
"""

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

    st.header("📄 Your Assigned Task")
    st.markdown("Please read the task description carefully before beginning.")
    st.markdown("---")

    # Render text normally; tables detected by pdfplumber are formatted as markdown tables
    task_content = _read_task_content(assigned_task)
    formatted   = _format_task_content(assigned_task, task_content)
    if formatted:
        st.markdown(formatted, unsafe_allow_html=True)
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

    # Generate a one-time welcome message when the dialogue is brand new
    if len(dialogue.messages) == 0 and agents['llm_ready']:
        personality = agents['llm_manager'].get_personality(dialogue.llm_personality)
        task_context = _read_task_content(dialogue.task_name) or dialogue.task_name.replace(".pdf", "")
        welcome_prompt = [{
            "role": "user",
            "content": (
                "Please open our collaboration with a brief, friendly welcome message. "
                "Acknowledge that I have just finished reading the task description and "
                "invite me to share my initial thoughts or how I would like to proceed."
            )
        }]
        with st.spinner("AI Assistant is preparing…"):
            welcome = personality.chat(welcome_prompt, task_context=task_context)
        agents['dialogue'].record_message(dialogue_id, "assistant", welcome)
        st.rerun()

    st.header("💬 Task Collaboration")

    # ── Task description (always accessible at top) ─────────────────────────
    with st.expander("📄 Task Description (click to expand / collapse)", expanded=True):
        task_content = _read_task_content(dialogue.task_name)
        formatted    = _format_task_content(dialogue.task_name, task_content)
        if formatted:
            st.markdown(formatted, unsafe_allow_html=True)
        else:
            st.info("Task description not available.")

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

        # Reuse cached extraction — already handles tables and plain text
        task_context = _read_task_content(dialogue.task_name) or dialogue.task_name.replace(".pdf", "")

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

        submit = st.form_submit_button("Submit Survey", use_container_width=True, type="primary")

        if submit:
            # Validate all Likert items answered
            unanswered = [k for k in likert_questions if responses.get(k) is None]
            if unanswered:
                nums = sorted(survey_item_numbers[k] for k in unanswered)
                nums_str = ", ".join(str(n) for n in nums)
                st.toast(
                    f"Almost there! Please answer question(s): {nums_str}",
                    icon="💬"
                )
                st.warning(
                    f"**Almost there!** The following item(s) still need a response: "
                    f"**{nums_str}**. Please scroll up and rate each one before submitting."
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

    # If admin panel is active, render it and skip participant UI
    if st.session_state.get("show_admin_page"):
        admin_download.admin_page()
        with st.sidebar:
            st.markdown("---")
            if st.button("← Back to Study", use_container_width=True):
                st.session_state.show_admin_page = False
                st.rerun()
        return

    # Participant sidebar
    with st.sidebar:
        st.markdown("## Research Platform")

        if st.session_state.current_session:
            session = st.session_state.current_session
            stage_label = _STAGE_LABELS.get(session.current_stage.value, "In progress")
            st.markdown(f"**Participant ID:**")
            st.markdown(f"<span style='font-size:1.6rem;font-weight:700;letter-spacing:0.05em;'>{st.session_state.user_id}</span>", unsafe_allow_html=True)
            st.markdown(f"**Progress:** {stage_label}")
            st.markdown("---")

            # Always-visible instructions
            st.info(
                "**Need to stop?** Click the **Save & Exit** button below. "
                "Your progress will be saved automatically."
            )
            st.info(
                "**Returning to the study?** Click the **Resume Session** tab "
                f"on the home page and enter your ID **`{st.session_state.user_id}`** "
                "to continue where you left off."
            )
            st.markdown("---")

            if st.button("🔄 Reload Page", use_container_width=True, key="reload_page"):
                fresh = agents['supervisor'].find_active_session_by_user(st.session_state.user_id)
                if fresh:
                    st.session_state.current_session = fresh
                    if fresh.dialogue_records:
                        st.session_state.current_dialogue_id = fresh.dialogue_records[-1]
                st.rerun()

            if st.button("💾 Save & Exit", use_container_width=True):
                st.session_state.show_save_exit = True

            if st.session_state.get("show_save_exit"):
                st.success(
                    f"**Your progress has been saved.**\n\n"
                    f"Your Participant ID is: **{st.session_state.user_id}**\n\n"
                    "Write this down or take a screenshot. When you are ready to continue, "
                    "return to this website and use the **Resume Session** tab to pick up where you left off."
                )
                if st.button("Close", key="close_save_exit"):
                    st.session_state.show_save_exit = False
                    st.rerun()
        else:
            st.info("No active session")

        # Admin button — bottom of sidebar, small and unobtrusive
        st.markdown("<br>" * 3, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Admin", use_container_width=False, key="admin_entry"):
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
