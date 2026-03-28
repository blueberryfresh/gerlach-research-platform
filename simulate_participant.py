#!/usr/bin/env python3
"""
simulate_participant.py - AI Participant Simulator for the Gerlach Research Platform

Simulates a complete participant run through all workflow stages using the real agent
APIs and real Anthropic LLM calls. Validates each stage and reports PASS/FAIL.

Usage:
    python simulate_participant.py [options]

Options:
    --profile    {role_model,average,self_centred,reserved}  Big5 profile to simulate (default: role_model)
    --task       {noble,popcorn}     Override random task assignment
    --messages   N                   Number of dialogue messages (default: 3, max: 5)
    --cleanup                        Delete test data files after run
    --user-id    sim_test_001        Custom user ID (must start with "sim_")
    --verbose                        Print LLM response text in output
    --dry-run                        Skip real LLM API calls (pipeline logic only)

Examples:
    python simulate_participant.py --profile role_model --task noble --messages 3
    python simulate_participant.py --profile average --task popcorn --verbose
    python simulate_participant.py --dry-run --cleanup
"""

# ── Bootstrap: path and environment ───────────────────────────────────────────
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("APP_LANG", "en")

# ── Standard library ──────────────────────────────────────────────────────────
import argparse
import random
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ── Project imports (after sys.path is set) ───────────────────────────────────
from agents import (
    SupervisorAgent,
    Big5AssessmentAgent,
    DialogueCaptureAgent,
    PostExpSurveyAgent,
    SummaryReportAgent,
    WorkflowStage,
)
from agents.data_models import UserSession
from strings import T

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_DIR    = PROJECT_ROOT / "research_data"
TASK_FOLDER = PROJECT_ROOT / "Task"

NOBLE_TASK   = "NOBLE INDUSTRIES for Big5.pdf"
POPCORN_TASK = "Popcorn Brain Task for Big5-rev2.pdf"
REQUIRED_TASKS = [NOBLE_TASK, POPCORN_TASK]
TASK_CLI_MAP   = {"noble": NOBLE_TASK, "popcorn": POPCORN_TASK}
PERSONALITY_TYPES = ["average", "role_model", "self_centred", "reserved"]

# Copied verbatim from agent_research_app.py so the LLM gets the same instruction
_NOBLE_TABLE_INSTRUCTION = """
FINAL ORDER TABLE INSTRUCTION:
When you and the participant have reached final agreement on the layoff order, present a markdown table summarising the agreed order from first to last laid off. Use exactly this format:

| Order | Employee | Reason |
|-------|----------|--------|
| 1st   | [Name]   | [Brief reason] |
| 2nd   | [Name]   | [Brief reason] |

Present this table only once, after the participant has explicitly confirmed they are satisfied with the complete order. Do not present the table until that confirmation.
"""

# Survey keys
LIKERT_KEYS = [
    "q1",  "q3",  "q4",  "q5",  "q6",  "q7",  "q8",  "q9",  "q10",
    "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19",
    "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q31",
]
TEXT_KEYS = ["q32", "q33", "q34", "q35", "q36", "q38", "q39"]

# Realistic dialogue messages per task
DIALOGUE_MESSAGES = {
    NOBLE_TASK: [
        "I've read through the employee data. Based on performance ratings and the supervisors' comments, who do you think should be considered first for the layoff?",
        "What weight should we give to the supervisors' comments versus the quantitative performance scores?",
        "I think we should prioritise performance criteria over seniority. The numbers tell a clearer story.",
        "What if we also factor in how difficult it would be to replace certain skill sets?",
        "I'm satisfied with our ranking. I think this is a defensible and fair ordering given all the criteria.",
    ],
    POPCORN_TASK: [
        "I've read the task. Let me start brainstorming - one idea is tiered subscription plans for different engagement levels.",
        "What about expanding to digital platforms? Short-form video and social media could reach a much younger demographic.",
        "Building on the digital angle, what about interactive formats where users vote on flavours or challenge outcomes?",
        "I think we need more creative angles. What if we partnered with wellness apps to position this around mindful digital detox?",
        "Those are strong ideas across multiple dimensions. I think we've covered originality, flexibility, and elaboration well.",
    ],
}

# ── Terminal colour helpers ────────────────────────────────────────────────────
def _supports_color() -> bool:
    if sys.platform == "win32":
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or "TERM_PROGRAM" in os.environ
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = _supports_color()

def _c(text: str, *codes: str) -> str:
    if not USE_COLOR:
        return text
    return "".join(codes) + text + "\033[0m"

def ok(msg: str)    -> str: return _c(f"[PASS] {msg}", "\033[92m")
def fail(msg: str)  -> str: return _c(f"[FAIL] {msg}", "\033[91m")
def info(msg: str)  -> str: return _c(f"       {msg}", "\033[96m")
def warn(msg: str)  -> str: return _c(f"[WARN] {msg}", "\033[93m")
def bold(msg: str)  -> str: return _c(msg, "\033[1m")
def dim(msg: str)   -> str: return _c(msg, "\033[2m")

def stage_header(name: str) -> None:
    print(f"\n{bold('-' * 58)}")
    print(bold(f"  {name}"))
    print(bold('-' * 58))


# ── Results tracker ────────────────────────────────────────────────────────────
class SimulationResults:
    def __init__(self):
        self.stages: List[Dict] = []
        self.start_time = time.monotonic()
        self.api_calls  = 0

    def record(self, stage: str, passed: bool, detail: str = "", duration_s: float = 0.0):
        self.stages.append({"stage": stage, "passed": passed, "detail": detail, "duration": duration_s})
        sym = ok(stage) if passed else fail(stage)
        dur = f"  {dim(f'({duration_s:.1f}s)')}" if duration_s else ""
        print(f"  {sym}{dur}")
        if detail:
            print(f"  {dim(detail)}")

    def summary(self) -> bool:
        total   = len(self.stages)
        n_pass  = sum(1 for s in self.stages if s["passed"])
        n_fail  = total - n_pass
        elapsed = time.monotonic() - self.start_time

        print(f"\n{bold('=' * 58)}")
        print(bold("  SIMULATION SUMMARY"))
        print(bold('=' * 58))
        for s in self.stages:
            sym = ok(s["stage"]) if s["passed"] else fail(s["stage"])
            d = s["duration"]
            dur = f"  {dim(f'({d:.1f}s)')}" if d else ""
            print(f"  {sym}{dur}")
            if not s["passed"] and s["detail"]:
                print(f"    {_c(s['detail'], chr(27) + '[91m')}")

        print()
        print(f"  Passed   : {_c(str(n_pass), chr(27)+'[92m')} / {total}")
        print(f"  API calls: {self.api_calls}")
        print(f"  Elapsed  : {elapsed:.1f}s")
        verdict = bold(_c("ALL PASSED", "\033[92m") if n_fail == 0 else _c(f"{n_fail} STAGE(S) FAILED", "\033[91m"))
        print(f"\n  Result   : {verdict}")
        print(bold('=' * 58))
        return n_fail == 0


# ── Big5 response profile generator ───────────────────────────────────────────
def build_big5_responses(profile: str) -> Dict[str, int]:
    """
    Generate IPIP-50 responses that reliably classify as the requested Gerlach type.

    Classification thresholds (from classify_gerlach_type):
      role_model  : distance = 100 - (20 per criterion: N<40, E>60, O>60, A>60, C>60)
      self_centred: distance = 100 - (33.3 per criterion: O<40, A<40, C<40)
      reserved    : distance = 100 - (50 per criterion: N<40, O<40)
      average     : distance = mean absolute deviation from 50

    Strategy: set answers so all items in a trait contribute the minimum or maximum,
    guaranteeing the target type wins with distance = 0.
    """
    # (forward_answer, reverse_answer) - for each trait
    # forward items:  score = answer
    # reverse items:  score = 6 - answer
    # so to get max contribution (5) from every item use: forward=5, reverse=1
    # to get min contribution (1) from every item use: forward=1, reverse=5
    # to get mid contribution (3) from every item use: forward=3, reverse=3
    RULES: Dict[str, Dict[str, Tuple[int, int]]] = {
        "role_model": {
            # N sum → 10 (score=0, N<40 ✓)  E/O/A/C sum → 50 (score=100, each >60 ✓)
            "extraversion":      (5, 1),
            "agreeableness":     (5, 1),
            "conscientiousness": (5, 1),
            "neuroticism":       (1, 5),
            "openness":          (5, 1),
        },
        "self_centred": {
            # O/A/C sum → 10 (score=0, each <40 ✓)  E/N sum → 30 (score=50, moderate)
            "openness":          (1, 5),
            "agreeableness":     (1, 5),
            "conscientiousness": (1, 5),
            "extraversion":      (3, 3),
            "neuroticism":       (3, 3),
        },
        "reserved": {
            # N/O sum → 10 (score=0, each <40 ✓)  E/A/C sum → 30 (score=50, moderate)
            "neuroticism":       (1, 5),
            "openness":          (1, 5),
            "extraversion":      (3, 3),
            "agreeableness":     (3, 3),
            "conscientiousness": (3, 3),
        },
        "average": {
            # All sums → 30 (score=50)  average distance from 50 = 0 ✓
            "extraversion":      (3, 3),
            "agreeableness":     (3, 3),
            "conscientiousness": (3, 3),
            "neuroticism":       (3, 3),
            "openness":          (3, 3),
        },
    }

    rules = RULES[profile]
    responses: Dict[str, int] = {}
    items = Big5AssessmentAgent.ASSESSMENT_ITEMS

    for trait, item_list in items.items():
        fwd, rev = rules[trait]
        for item in item_list:
            responses[item["id"]] = rev if item["reverse"] else fwd

    return responses


# ── Survey response generator ─────────────────────────────────────────────────
def generate_survey_responses(profile: str, seed: int = 42) -> Dict:
    """Generate plausible Likert responses for the given personality profile."""
    rng = random.Random(seed)
    BIASES = {
        "role_model":   (5, 0.8),   # positive, satisfied collaborator
        "average":      (4, 1.2),   # moderate
        "self_centred": (3, 1.2),   # critical / indifferent
        "reserved":     (3, 0.7),   # neutral, quiet
    }
    mean, std = BIASES.get(profile, (4, 1.2))
    responses: Dict = {}
    for key in LIKERT_KEYS:
        val = int(round(rng.gauss(mean, std)))
        responses[key] = max(1, min(7, val))
    for key in TEXT_KEYS:
        responses[key] = ""   # text fields are optional in the app
    return responses


# ── PDF task content reader (mirrors _read_task_content in agent_research_app.py) ──
def read_task_content(task_name: str) -> str:
    task_path = TASK_FOLDER / task_name
    if not task_path.exists():
        return ""
    try:
        import pdfplumber
        output = []
        with pdfplumber.open(str(task_path)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
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
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(task_path))
            return "\n\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except Exception:
            return ""


# ── Regression checks (known production incidents) ────────────────────────────

def sim_regression_checks(supervisor: SupervisorAgent, results: SimulationResults, user_id: str) -> bool:
    """
    Targeted regression tests for bugs that caused blank screens in production.
    Run automatically before the main simulation.

    Incidents covered
    -----------------
    2026-03-27 (participants 130-13, 170-3):
      Sessions stuck at REGISTRATION stage had no matching branch in the app's
      routing block, producing a completely blank main content area while the
      sidebar still rendered normally. Root cause: GitHub sync restored stale
      session files saved *before* advance_stage() persisted the BIG5_ASSESSMENT
      transition. Fix: detect REGISTRATION stage in routing and auto-advance.
    """
    stage_header("REGRESSION CHECKS")
    all_passed = True

    # ── Regression 1: REGISTRATION stage must auto-advance to BIG5_ASSESSMENT ──
    # Incident: participants 130-13, 170-3 — blank screen (2026-03-27)
    t0 = time.monotonic()
    reg_session_id = None
    try:
        reg_user = f"{user_id}_regtest"
        # Create a session — it starts at REGISTRATION (simulates stale GitHub restore)
        reg_session = supervisor.create_user_session(
            user_id=reg_user,
            metadata={"simulated": True, "regression_test": "REGISTRATION_fallthrough"},
        )
        reg_session_id = reg_session.session_id

        assert reg_session.current_stage == WorkflowStage.REGISTRATION, (
            f"New session should start at REGISTRATION, got {reg_session.current_stage}"
        )

        # Replicate the routing fix from agent_research_app.py:
        # if stage == REGISTRATION → advance to BIG5, then render Big5 page
        if reg_session.current_stage == WorkflowStage.REGISTRATION:
            supervisor.advance_stage(reg_session.session_id, WorkflowStage.BIG5_ASSESSMENT)
            reg_session = supervisor.get_session(reg_session.session_id)

        assert reg_session is not None, "get_session() returned None after advance"
        assert reg_session.current_stage == WorkflowStage.BIG5_ASSESSMENT, (
            f"Expected BIG5_ASSESSMENT after auto-advance, got {reg_session.current_stage}"
        )

        results.record(
            "REGRESSION: REGISTRATION->BIG5 auto-advance",
            True,
            "Session stuck at REGISTRATION now auto-advances to BIG5_ASSESSMENT (incident 2026-03-27)",
            time.monotonic() - t0,
        )
    except Exception as exc:
        results.record(
            "REGRESSION: REGISTRATION->BIG5 auto-advance",
            False,
            str(exc),
            time.monotonic() - t0,
        )
        all_passed = False
    finally:
        # Always clean up the temporary regression session
        if reg_session_id:
            f = DATA_DIR / "sessions" / f"{reg_session_id}.json"
            if f.exists():
                f.unlink()

    # ── Regression 2: stage routing must cover ALL WorkflowStage values ──
    # Any stage without a matching branch silently produces a blank page.
    t0 = time.monotonic()
    try:
        routed_stages = {
            WorkflowStage.REGISTRATION,
            WorkflowStage.BIG5_ASSESSMENT,
            WorkflowStage.TASK_SELECTION,
            WorkflowStage.TASK_DIALOGUE,
            WorkflowStage.TASK_RESPONSE,
            WorkflowStage.POST_SURVEY,
            WorkflowStage.COMPLETED,
        }
        all_stages   = set(WorkflowStage)
        unrouted     = all_stages - routed_stages
        assert not unrouted, (
            f"WorkflowStage value(s) have no routing branch in agent_research_app.py: "
            + ", ".join(s.value for s in unrouted)
        )
        results.record(
            "REGRESSION: all stages routed",
            True,
            f"All {len(all_stages)} WorkflowStage values have a routing branch",
            time.monotonic() - t0,
        )
    except Exception as exc:
        results.record(
            "REGRESSION: all stages routed",
            False,
            str(exc),
            time.monotonic() - t0,
        )
        all_passed = False

    return all_passed


# ── Stage simulators ──────────────────────────────────────────────────────────

def sim_registration(supervisor, user_id: str, results: SimulationResults) -> Optional[UserSession]:
    stage_header("STAGE 1 - REGISTRATION")
    t0 = time.monotonic()
    try:
        existing = supervisor.find_active_session_by_user(user_id)
        if existing:
            print(warn(f"Found existing incomplete session {existing.session_id} - reusing it"))
            session = existing
        else:
            session = supervisor.create_user_session(
                user_id=user_id,
                metadata={"consent_given": True, "start_time": datetime.now().isoformat(), "simulated": True},
            )
            supervisor.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
            session = supervisor.get_session(session.session_id)

        assert session is not None,                           "Session is None after creation"
        assert session.user_id == user_id,                    f"user_id mismatch: {session.user_id}"
        assert session.current_stage == WorkflowStage.BIG5_ASSESSMENT, \
            f"Wrong stage: {session.current_stage}"

        results.record("REGISTRATION", True,
                       f"session_id = {session.session_id}",
                       time.monotonic() - t0)
        return session
    except Exception as exc:
        results.record("REGISTRATION", False, str(exc), time.monotonic() - t0)
        return None


def sim_big5_assessment(
    assessment_agent, supervisor, session: UserSession,
    profile: str, results: SimulationResults
) -> Optional[UserSession]:
    stage_header("STAGE 2 - BIG5 ASSESSMENT")
    t0 = time.monotonic()
    try:
        responses = build_big5_responses(profile)
        assert len(responses) == 50, f"Expected 50 responses, got {len(responses)}"

        assessment = assessment_agent.conduct_assessment(
            user_id=session.user_id,
            session_id=session.session_id,
            responses=responses,
        )

        # Write assessment_id back to session (mirrors app logic in render_big5_assessment)
        session.big5_assessment_id = assessment.assessment_id
        session.save(DATA_DIR)

        supervisor.advance_stage(session.session_id, WorkflowStage.TASK_SELECTION)
        session = supervisor.get_session(session.session_id)

        assert assessment.gerlach_type == profile, (
            f"Expected gerlach_type={profile!r}, got {assessment.gerlach_type!r} - "
            f"N={assessment.neuroticism:.0f} E={assessment.extraversion:.0f} "
            f"O={assessment.openness:.0f} A={assessment.agreeableness:.0f} C={assessment.conscientiousness:.0f}"
        )
        assert session.current_stage == WorkflowStage.TASK_SELECTION

        results.record(
            "BIG5_ASSESSMENT", True,
            f"gerlach_type={assessment.gerlach_type}  confidence={assessment.gerlach_confidence:.1f}%  "
            f"N={assessment.neuroticism:.0f} E={assessment.extraversion:.0f} "
            f"O={assessment.openness:.0f} A={assessment.agreeableness:.0f} C={assessment.conscientiousness:.0f}",
            time.monotonic() - t0,
        )
        return session
    except Exception as exc:
        results.record("BIG5_ASSESSMENT", False, str(exc), time.monotonic() - t0)
        return None


def sim_task_selection(
    supervisor, dialogue_agent, session: UserSession,
    task_override: Optional[str], results: SimulationResults
) -> Tuple[Optional[UserSession], Optional[object]]:
    stage_header("STAGE 3 - TASK SELECTION")
    t0 = time.monotonic()
    try:
        assigned_task        = task_override or random.choice(REQUIRED_TASKS)
        assigned_personality = random.choice(PERSONALITY_TYPES)

        # Persist assignment (mirrors _get_or_assign)
        session.metadata["assigned_task"]        = assigned_task
        session.metadata["assigned_personality"] = assigned_personality
        session.save(DATA_DIR)

        # Start dialogue record
        dialogue = dialogue_agent.start_dialogue(
            user_id=session.user_id,
            session_id=session.session_id,
            task_name=assigned_task,
            llm_personality=assigned_personality,
        )

        # Write static welcome message - no API call (mirrors render_task_selection)
        dialogue_agent.record_message(
            dialogue.dialogue_id, "assistant", T["task_dial_welcome_text"]
        )

        session.dialogue_records.append(dialogue.dialogue_id)
        session.save(DATA_DIR)

        supervisor.advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
        session = supervisor.get_session(session.session_id)

        fresh = dialogue_agent.get_dialogue(dialogue.dialogue_id)
        assert session.current_stage == WorkflowStage.TASK_DIALOGUE
        assert fresh.total_messages == 1, f"Expected 1 welcome msg, got {fresh.total_messages}"
        assert fresh.task_name        == assigned_task
        assert fresh.llm_personality  == assigned_personality

        results.record(
            "TASK_SELECTION", True,
            f"task = {assigned_task[:40]}  personality = {assigned_personality}",
            time.monotonic() - t0,
        )
        return session, dialogue
    except Exception as exc:
        results.record("TASK_SELECTION", False, str(exc), time.monotonic() - t0)
        return None, None


def sim_task_dialogue(
    supervisor, dialogue_agent, llm_manager,
    session: UserSession, dialogue,
    num_messages: int, verbose: bool,
    results: SimulationResults,
) -> Optional[UserSession]:
    stage_header(f"STAGE 4 - TASK DIALOGUE  (sending {num_messages} message(s) via real API)")
    t0 = time.monotonic()
    try:
        task_name    = dialogue.task_name
        task_context = read_task_content(task_name) or task_name.replace(".pdf", "")
        if not read_task_content(task_name):
            print(warn(f"PDF not readable - using task name as context fallback"))
        if task_name == NOBLE_TASK:
            task_context += _NOBLE_TABLE_INSTRUCTION

        personality    = llm_manager.get_personality(dialogue.llm_personality)
        messages_to_send = DIALOGUE_MESSAGES[task_name][:num_messages]

        for i, user_msg in enumerate(messages_to_send, 1):
            print(info(f"Message {i}/{len(messages_to_send)}: {user_msg[:70]}…"))

            dialogue_agent.record_message(dialogue.dialogue_id, "user", user_msg)

            # Reload + strip leading assistant turns (exact replica of render_task_dialogue)
            fresh    = dialogue_agent.get_dialogue(dialogue.dialogue_id)
            all_msgs = [{"role": m.role, "content": m.content} for m in (fresh or dialogue).messages]
            first_user = next((idx for idx, m in enumerate(all_msgs) if m["role"] == "user"), None)
            messages   = all_msgs[first_user:] if first_user is not None else all_msgs

            call_t0  = time.monotonic()
            response = personality.chat(
                messages,
                task_context=task_context,
                _monitor_meta={
                    "session_id":  session.session_id,
                    "dialogue_id": dialogue.dialogue_id,
                },
            )
            latency = time.monotonic() - call_t0
            results.api_calls += 1

            dialogue_agent.record_message(dialogue.dialogue_id, "assistant", response)
            print(info(f"Response received in {latency:.1f}s"))
            if verbose:
                print(f"  {dim(response[:200])}{'…' if len(response) > 200 else ''}")

        dialogue_agent.end_dialogue(dialogue.dialogue_id)
        supervisor.advance_stage(session.session_id, WorkflowStage.TASK_RESPONSE)
        session = supervisor.get_session(session.session_id)

        final = dialogue_agent.get_dialogue(dialogue.dialogue_id)
        assert final.ended_at is not None,                    "Dialogue was not ended"
        assert final.user_message_count == num_messages,      \
            f"user_message_count {final.user_message_count} != {num_messages}"
        # welcome message (written in task selection) + N LLM responses
        assert final.assistant_message_count == num_messages + 1, \
            f"assistant_message_count {final.assistant_message_count} != {num_messages + 1} (1 welcome + {num_messages} responses)"
        assert session.current_stage == WorkflowStage.TASK_RESPONSE

        results.record(
            "TASK_DIALOGUE", True,
            f"user_msgs={final.user_message_count}  total_msgs={final.total_messages}  "
            f"duration={final.duration_seconds:.1f}s",
            time.monotonic() - t0,
        )
        return session
    except Exception as exc:
        results.record("TASK_DIALOGUE", False, str(exc), time.monotonic() - t0)
        return None


def sim_task_response(supervisor, session: UserSession, results: SimulationResults) -> Optional[UserSession]:
    stage_header("STAGE 5 - TASK RESPONSE  (pass-through)")
    t0 = time.monotonic()
    try:
        assert session.current_stage == WorkflowStage.TASK_RESPONSE, \
            f"Expected TASK_RESPONSE, got {session.current_stage}"
        supervisor.advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
        session = supervisor.get_session(session.session_id)
        assert session.current_stage == WorkflowStage.POST_SURVEY
        results.record("TASK_RESPONSE", True, "advanced to POST_SURVEY", time.monotonic() - t0)
        return session
    except Exception as exc:
        results.record("TASK_RESPONSE", False, str(exc), time.monotonic() - t0)
        return None


def sim_post_survey(
    survey_agent, supervisor, session: UserSession, dialogue,
    profile: str, results: SimulationResults
) -> Optional[UserSession]:
    stage_header("STAGE 6 - POST SURVEY")
    t0 = time.monotonic()
    try:
        responses = generate_survey_responses(profile)

        missing      = [k for k in LIKERT_KEYS if k not in responses]
        out_of_range = [k for k in LIKERT_KEYS if not (1 <= responses.get(k, 0) <= 7)]
        assert not missing,      f"Missing Likert keys: {missing}"
        assert not out_of_range, f"Out-of-range values: {out_of_range}"

        survey = survey_agent.conduct_survey(
            user_id=session.user_id,
            session_id=session.session_id,
            dialogue_id=dialogue.dialogue_id,
            responses=responses,
        )

        # Write survey_id back (mirrors render_post_survey)
        session.survey_id = survey.survey_id
        session.save(DATA_DIR)

        supervisor.advance_stage(session.session_id, WorkflowStage.COMPLETED)
        session = supervisor.get_session(session.session_id)

        assert session.current_stage == WorkflowStage.COMPLETED
        assert survey.survey_id is not None

        results.record(
            "POST_SURVEY", True,
            f"survey_id = {survey.survey_id}  likert_items = {len(LIKERT_KEYS)}",
            time.monotonic() - t0,
        )
        return session
    except Exception as exc:
        results.record("POST_SURVEY", False, str(exc), time.monotonic() - t0)
        return None


def sim_completion(supervisor, summary_agent, session: UserSession, results: SimulationResults) -> Optional[UserSession]:
    stage_header("STAGE 7 - COMPLETED + REPORT")
    t0 = time.monotonic()
    try:
        supervisor.complete_session(session.session_id)
        session = supervisor.get_session(session.session_id)

        assert session.current_stage == WorkflowStage.COMPLETED
        assert session.ended_at is not None, "ended_at not set"

        report = summary_agent.generate_report(
            user_id=session.user_id,
            session_id=session.session_id,
        )

        session.report_id = report.report_id
        session.save(DATA_DIR)

        assert report.gerlach_type   is not None, "report.gerlach_type is None"
        assert report.total_messages  > 0,         "report.total_messages == 0"
        assert len(report.dialogue_ids) > 0,       "report.dialogue_ids is empty"

        results.record(
            "COMPLETED+REPORT", True,
            f"report_id = {report.report_id}  gerlach = {report.gerlach_type}  msgs = {report.total_messages}",
            time.monotonic() - t0,
        )
        return session
    except Exception as exc:
        results.record("COMPLETED+REPORT", False, str(exc), time.monotonic() - t0)
        return None


# ── Cleanup ───────────────────────────────────────────────────────────────────
def cleanup_test_data(user_id: str) -> None:
    print(f"\n{info(f'Cleaning up test data for user_id={user_id!r}…')}")
    removed = 0
    subdirs = ["sessions", "assessments", "dialogues", "surveys", "reports", "task_responses"]
    for subdir in subdirs:
        d = DATA_DIR / subdir
        if not d.exists():
            continue
        for ext in ["*.json", "*.md", "*.html"]:
            for f in d.glob(ext):
                if user_id in f.stem:
                    f.unlink()
                    removed += 1
        # Noble / Popcorn sub-directories
        for sub in ["noble", "popcorn"]:
            sub_d = d / sub
            if sub_d.exists():
                for f in sub_d.glob("*.json"):
                    if user_id in f.stem:
                        f.unlink()
                        removed += 1
    print(f"  {ok(f'Removed {removed} file(s)')}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Simulate a research participant through the full 7-stage workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--profile",
        choices=PERSONALITY_TYPES,
        default="role_model",
        help="Gerlach personality profile to simulate (default: role_model)",
    )
    p.add_argument(
        "--task",
        choices=list(TASK_CLI_MAP.keys()),
        default=None,
        help="Override task assignment: noble or popcorn (default: random)",
    )
    p.add_argument(
        "--messages",
        type=int,
        default=3,
        metavar="N",
        help="Number of dialogue messages to send 1–5 (default: 3)",
    )
    p.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete all generated test data after the run",
    )
    p.add_argument(
        "--user-id",
        dest="user_id",
        default=None,
        metavar="ID",
        help="Custom test user ID - must start with 'sim_' (default: sim_YYYYMMDD_HHMMSS)",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print the first 200 characters of each LLM response",
    )
    p.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Skip real LLM API calls (validates pipeline logic only)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Resolve user ID
    if args.user_id:
        if not args.user_id.startswith("sim_"):
            print(fail(f"--user-id must start with 'sim_' to protect real research data. Got: {args.user_id!r}"))
            sys.exit(1)
        user_id = args.user_id
    else:
        user_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    task_override = TASK_CLI_MAP.get(args.task) if args.task else None
    num_messages  = min(max(args.messages, 1), 5)

    # Header
    print(bold("\n" + "=" * 56))
    print(bold("  Gerlach Research Platform -- Participant Simulator"))
    print(bold("=" * 56))
    print(f"  User ID  : {user_id}")
    print(f"  Profile  : {args.profile}")
    print(f"  Task     : {args.task or 'random'}")
    print(f"  Messages : {num_messages}")
    print(f"  Dry run  : {args.dry_run}")
    print(f"  Cleanup  : {args.cleanup}")
    print(f"  Verbose  : {args.verbose}")

    # API key check
    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"\n{fail('ANTHROPIC_API_KEY is not set in the environment.')}")
        print(f"  Set it with:  {dim('set ANTHROPIC_API_KEY=sk-ant-...')}")
        sys.exit(1)

    results = SimulationResults()

    # Initialise agents
    supervisor       = SupervisorAgent(DATA_DIR)
    assessment_agent = Big5AssessmentAgent(DATA_DIR)
    dialogue_agent   = DialogueCaptureAgent(DATA_DIR)
    survey_agent     = PostExpSurveyAgent(DATA_DIR)
    summary_agent    = SummaryReportAgent(DATA_DIR)

    llm_manager = None
    if not args.dry_run:
        try:
            from gerlach_personality_llms import GerlachPersonalityManager
            llm_manager = GerlachPersonalityManager()
        except ValueError as exc:
            print(f"\n{fail(f'LLM initialisation failed: {exc}')}")
            sys.exit(1)

    # ── Regression checks (run before main stages) ────────────────────────────
    regression_ok = sim_regression_checks(supervisor, results, user_id)
    if not regression_ok:
        print(f"\n{fail('Regression check(s) failed — a known bug has regressed. Fix before continuing.')}")
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    # ── Run stages ────────────────────────────────────────────────────────────
    session = sim_registration(supervisor, user_id, results)
    if session is None:
        results.summary()
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    session = sim_big5_assessment(assessment_agent, supervisor, session, args.profile, results)
    if session is None:
        results.summary()
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    session, dialogue = sim_task_selection(supervisor, dialogue_agent, session, task_override, results)
    if session is None:
        results.summary()
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    if args.dry_run:
        # Advance the stage manually without calling the LLM
        print()
        print(warn("DRY RUN - skipping real LLM API calls for TASK_DIALOGUE"))
        # Record a fake user message so user_message_count > 0 (needed for end_dialogue)
        dialogue_agent.record_message(dialogue.dialogue_id, "user", "[dry-run test message]")
        dialogue_agent.record_message(dialogue.dialogue_id, "assistant", "[dry-run test response]")
        dialogue_agent.end_dialogue(dialogue.dialogue_id)
        supervisor.advance_stage(session.session_id, WorkflowStage.TASK_RESPONSE)
        session = supervisor.get_session(session.session_id)
        results.record("TASK_DIALOGUE", True, "dry run - no API calls made", 0.0)
    else:
        session = sim_task_dialogue(
            supervisor, dialogue_agent, llm_manager,
            session, dialogue, num_messages, args.verbose, results
        )
        if session is None:
            results.summary()
            if args.cleanup:
                cleanup_test_data(user_id)
            sys.exit(1)

    session = sim_task_response(supervisor, session, results)
    if session is None:
        results.summary()
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    session = sim_post_survey(survey_agent, supervisor, session, dialogue, args.profile, results)
    if session is None:
        results.summary()
        if args.cleanup:
            cleanup_test_data(user_id)
        sys.exit(1)

    session = sim_completion(supervisor, summary_agent, session, results)

    all_passed = results.summary()

    if args.cleanup:
        cleanup_test_data(user_id)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
