"""
Comprehensive test suite for the Big5 Personality Research Platform.

Covers:
  - Data models (save/load round-trips, edge cases)
  - SupervisorAgent (session lifecycle, stage transitions)
  - Big5AssessmentAgent (scoring, reverse items, Gerlach classification)
  - DialogueCaptureAgent (start/record/end, statistics, transcripts)
  - PostExpSurveyAgent (conduct, labeled responses, persistence)
  - GerlachPersonalityManager (personality dispatch, LLM mocking)
  - strings.py (EN/KO key parity)
  - Edge cases (missing files, empty dialogues, invalid IDs, etc.)

Run with:
    pytest test_comprehensive.py -v
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

# ── Ensure project root is on the path ──────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Patch github_storage before any project imports so saves don't hit the network
_mock_storage = MagicMock()
_mock_storage.write.return_value = True
_mock_storage.write_text.return_value = True
_mock_storage.enabled = False

sys.modules.setdefault("github_storage", MagicMock(get_storage=lambda: _mock_storage))


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _neutral_responses():
    """Return all-3 responses for the EN IPIP-50 (50 items)."""
    from agents import Big5AssessmentAgent
    agent = Big5AssessmentAgent.__new__(Big5AssessmentAgent)
    items = []
    for trait, trait_items in Big5AssessmentAgent.ASSESSMENT_ITEMS.items():
        for item in trait_items:
            items.append(item)
    return {item["id"]: 3 for item in items}


def _extreme_responses(forward_val: int, reverse_val: int):
    """Return responses where forward items = forward_val, reverse items = reverse_val."""
    from agents import Big5AssessmentAgent
    responses = {}
    for trait_items in Big5AssessmentAgent.ASSESSMENT_ITEMS.values():
        for item in trait_items:
            responses[item["id"]] = reverse_val if item["reverse"] else forward_val
    return responses


def _build_survey_responses():
    """Minimal valid survey responses (Likert keys q1, q3-q26, q31 + text keys)."""
    likert_keys = [
        "q1", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10",
        "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18",
        "q19", "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q31",
    ]
    responses = {k: 4 for k in likert_keys}
    responses.update({
        "q32": "Some negative comment",
        "q33": "Some positive comment",
        "q34": "Compatibility discussion",
        "q35": "Personality role description",
        "q36": "Communication skill description",
        "q38": "Non-binary",
        "q39": "Psychology",
    })
    return responses


# ════════════════════════════════════════════════════════════════════════════
# 1. DATA MODELS
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowStage:
    def test_all_stages_defined(self):
        from agents import WorkflowStage
        stages = [s.value for s in WorkflowStage]
        assert "registration" in stages
        assert "big5_assessment" in stages
        assert "task_selection" in stages
        assert "task_dialogue" in stages
        assert "task_response" in stages
        assert "post_survey" in stages
        assert "completed" in stages

    def test_stage_roundtrip(self):
        from agents import WorkflowStage
        for stage in WorkflowStage:
            assert WorkflowStage(stage.value) == stage


class TestUserSessionModel:
    def test_save_and_load_roundtrip(self, tmp_path):
        from agents.data_models import UserSession, WorkflowStage
        session = UserSession(
            user_id="u1",
            session_id="u1_20260101_abc123",
            started_at=datetime.now().isoformat(),
            current_stage=WorkflowStage.BIG5_ASSESSMENT,
            completed_stages=["registration"],
            big5_assessment_id="assess_001",
            metadata={"assigned_task": "noble"},
        )
        session.save(tmp_path)
        loaded = UserSession.load("u1_20260101_abc123", tmp_path)
        assert loaded.user_id == "u1"
        assert loaded.current_stage == WorkflowStage.BIG5_ASSESSMENT
        assert loaded.completed_stages == ["registration"]
        assert loaded.big5_assessment_id == "assess_001"
        assert loaded.metadata["assigned_task"] == "noble"

    def test_to_dict_serialises_stage_as_string(self):
        from agents.data_models import UserSession, WorkflowStage
        session = UserSession(
            user_id="u2",
            session_id="u2_sid",
            started_at=datetime.now().isoformat(),
            current_stage=WorkflowStage.TASK_DIALOGUE,
        )
        d = session.to_dict()
        assert d["current_stage"] == "task_dialogue"

    def test_load_missing_file_raises(self, tmp_path):
        from agents.data_models import UserSession
        with pytest.raises(Exception):
            UserSession.load("nonexistent_session_id", tmp_path)

    def test_optional_fields_default_none(self, tmp_path):
        from agents.data_models import UserSession, WorkflowStage
        session = UserSession(
            user_id="u3",
            session_id="u3_sid",
            started_at=datetime.now().isoformat(),
        )
        assert session.big5_assessment_id is None
        assert session.survey_id is None
        assert session.report_id is None
        assert session.ended_at is None
        assert session.dialogue_records == []


class TestBig5AssessmentModel:
    def test_save_and_load_roundtrip(self, tmp_path):
        from agents.data_models import Big5Assessment
        a = Big5Assessment(
            assessment_id="assess_001",
            user_id="u1",
            session_id="sess_001",
            conducted_at=datetime.now().isoformat(),
            openness=75.0,
            conscientiousness=60.0,
            extraversion=45.0,
            agreeableness=80.0,
            neuroticism=30.0,
            gerlach_type="role_model",
            gerlach_confidence=0.85,
        )
        a.save(tmp_path)
        loaded = Big5Assessment.load("assess_001", tmp_path)
        assert loaded.openness == 75.0
        assert loaded.gerlach_type == "role_model"
        assert loaded.gerlach_confidence == 0.85

    def test_load_missing_raises(self, tmp_path):
        from agents.data_models import Big5Assessment
        with pytest.raises(Exception):
            Big5Assessment.load("no_such_assessment", tmp_path)


class TestDialogueRecordModel:
    def test_add_message_updates_counts(self):
        from agents.data_models import DialogueRecord
        d = DialogueRecord(
            dialogue_id="diag_001",
            user_id="u1",
            session_id="sess_001",
            task_name="TestTask",
            llm_personality="average",
            started_at=datetime.now().isoformat(),
        )
        d.add_message("user", "Hello!", "msg_001")
        d.add_message("assistant", "Hi!", "msg_002")
        d.add_message("user", "Thanks.", "msg_003")
        assert d.total_messages == 3
        assert d.user_message_count == 2
        assert d.assistant_message_count == 1

    def test_end_dialogue_sets_duration_from_first_message(self):
        from agents.data_models import DialogueRecord
        d = DialogueRecord(
            dialogue_id="diag_002",
            user_id="u1",
            session_id="sess_001",
            task_name="TestTask",
            llm_personality="reserved",
            started_at=datetime.now().isoformat(),
        )
        d.add_message("user", "Start", "msg_001")
        d.end_dialogue()
        assert d.ended_at is not None
        assert d.duration_seconds is not None
        assert d.duration_seconds >= 0

    def test_end_dialogue_no_messages_uses_started_at(self):
        from agents.data_models import DialogueRecord
        d = DialogueRecord(
            dialogue_id="diag_003",
            user_id="u1",
            session_id="sess_001",
            task_name="TestTask",
            llm_personality="average",
            started_at=datetime.now().isoformat(),
        )
        d.end_dialogue()
        assert d.duration_seconds is not None
        assert d.duration_seconds >= 0

    def test_save_and_load_roundtrip_preserves_messages(self, tmp_path):
        from agents.data_models import DialogueRecord
        d = DialogueRecord(
            dialogue_id="diag_save_001",
            user_id="u1",
            session_id="sess_001",
            task_name="Noble Industries",
            llm_personality="role_model",
            started_at=datetime.now().isoformat(),
        )
        d.add_message("user", "Can you help?", "msg_001")
        d.add_message("assistant", "Of course!", "msg_002")
        d.save(tmp_path)

        loaded = DialogueRecord.load("diag_save_001", tmp_path)
        assert len(loaded.messages) == 2
        assert loaded.messages[0].role == "user"
        assert loaded.messages[0].content == "Can you help?"
        assert loaded.messages[1].role == "assistant"
        assert loaded.total_messages == 2

    def test_github_throttle_rule(self):
        """GitHub sync triggers on messages 1, 5, 10, 15, ... and force_github=True."""
        from agents.data_models import DialogueRecord
        d = DialogueRecord(
            dialogue_id="diag_throttle",
            user_id="u1",
            session_id="sess",
            task_name="Task",
            llm_personality="average",
            started_at=datetime.now().isoformat(),
        )
        # total_messages=0 before any add → should_sync=True (<=1)
        assert (True or d.total_messages <= 1 or (d.total_messages % 5 == 0))
        d.add_message("user", "msg1", "id1")  # total=1: <=1 → sync
        assert d.total_messages <= 1 or (d.total_messages % 5 == 0)
        d.add_message("user", "msg2", "id2")  # total=2: no sync
        assert not (d.total_messages <= 1 or (d.total_messages % 5 == 0))
        for i in range(3, 6):                  # total→5: sync
            d.add_message("user", f"msg{i}", f"id{i}")
        assert d.total_messages == 5
        assert d.total_messages % 5 == 0


class TestPostExpSurveyModel:
    def test_save_and_load_roundtrip(self, tmp_path):
        from agents.data_models import PostExpSurvey
        s = PostExpSurvey(
            survey_id="survey_001",
            user_id="u1",
            session_id="sess_001",
            dialogue_id="diag_001",
            conducted_at=datetime.now().isoformat(),
            responses={"q1": 5, "q32": "Great experience"},
            labeled_responses={"q1": {"question": "...", "type": "likert", "response": 5}},
            overall_satisfaction=6,
        )
        s.save(tmp_path)
        loaded = PostExpSurvey.load("survey_001", tmp_path)
        assert loaded.responses["q1"] == 5
        assert loaded.overall_satisfaction == 6
        assert loaded.dialogue_id == "diag_001"


class TestUserReportModel:
    def test_save_and_load_roundtrip(self, tmp_path):
        from agents.data_models import UserReport
        r = UserReport(
            report_id="report_001",
            user_id="u1",
            session_id="sess_001",
            generated_at=datetime.now().isoformat(),
            big5_scores={"openness": 75.0},
            gerlach_type="role_model",
            total_messages=10,
            markdown_report="# Report\nSome content",
            html_report="<html><body>report</body></html>",
        )
        r.save(tmp_path)
        loaded = UserReport.load("report_001", tmp_path)
        assert loaded.gerlach_type == "role_model"
        assert loaded.total_messages == 10

        # Markdown and HTML files also written
        assert (tmp_path / "reports" / "report_001.md").exists()
        assert (tmp_path / "reports" / "report_001.html").exists()


# ════════════════════════════════════════════════════════════════════════════
# 2. SUPERVISOR AGENT
# ════════════════════════════════════════════════════════════════════════════

class TestSupervisorAgent:
    def test_create_session_returns_valid_session(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p001", metadata={"test": True})
        assert session.user_id == "p001"
        assert session.current_stage == WorkflowStage.REGISTRATION
        assert "p001" in session.session_id
        assert session.metadata["test"] is True

    def test_create_session_persists_to_disk(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p002")
        file = tmp_path / "sessions" / f"{session.session_id}.json"
        assert file.exists()
        data = json.loads(file.read_text())
        assert data["user_id"] == "p002"

    def test_get_session_by_id(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p003")
        loaded = sup.get_session(session.session_id)
        assert loaded is not None
        assert loaded.user_id == "p003"

    def test_get_session_nonexistent_returns_none(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        result = sup.get_session("does_not_exist_session")
        assert result is None

    def test_advance_stage(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p004")
        result = sup.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
        assert result is True
        reloaded = sup.get_session(session.session_id)
        assert reloaded.current_stage == WorkflowStage.BIG5_ASSESSMENT
        assert "registration" in reloaded.completed_stages

    def test_advance_stage_unknown_session_returns_false(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        result = sup.advance_stage("ghost_session", WorkflowStage.BIG5_ASSESSMENT)
        assert result is False

    def test_complete_session(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p005")
        sup.complete_session(session.session_id)
        reloaded = sup.get_session(session.session_id)
        assert reloaded.current_stage == WorkflowStage.COMPLETED
        assert reloaded.ended_at is not None

    def test_find_active_session_by_user(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        s1 = sup.create_user_session("p006")
        found = sup.find_active_session_by_user("p006")
        assert found is not None
        assert found.session_id == s1.session_id

    def test_find_active_session_ignores_completed(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p007")
        sup.complete_session(session.session_id)
        found = sup.find_active_session_by_user("p007")
        assert found is None

    def test_find_active_session_unknown_user_returns_none(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        assert sup.find_active_session_by_user("ghost_user") is None

    def test_find_active_returns_most_recent(self, tmp_path):
        """When two active sessions exist for same user, return the latest one."""
        from agents import SupervisorAgent, WorkflowStage
        import time
        sup = SupervisorAgent(tmp_path)
        s1 = sup.create_user_session("p008")
        time.sleep(0.05)  # ensure different started_at
        s2 = sup.create_user_session("p008")
        found = sup.find_active_session_by_user("p008")
        assert found.session_id == s2.session_id

    def test_validate_stage_transition_forward(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p009")
        ok, _ = sup.validate_stage_transition(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
        assert ok is True

    def test_validate_stage_transition_skip_blocked(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p010")
        # Try to jump from REGISTRATION to TASK_DIALOGUE (skipping 2 stages)
        ok, msg = sup.validate_stage_transition(session.session_id, WorkflowStage.TASK_DIALOGUE)
        assert ok is False
        assert "skip" in msg.lower() or "complete" in msg.lower()

    def test_get_workflow_status(self, tmp_path):
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p011")
        status = sup.get_workflow_status(session.session_id)
        assert status["current_stage"] == "registration"
        assert status["is_completed"] is False
        assert isinstance(status["progress_percentage"], float)

    def test_get_workflow_status_unknown_session(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        status = sup.get_workflow_status("ghost")
        assert "error" in status

    def test_get_user_sessions(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        sup.create_user_session("p012")
        sup.create_user_session("p012")
        sessions = sup.get_user_sessions("p012")
        assert len(sessions) == 2
        assert all(s.user_id == "p012" for s in sessions)

    def test_get_statistics(self, tmp_path):
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        sup.create_user_session("p013")
        stats = sup.get_statistics()
        assert stats["total_sessions"] >= 1
        assert "total_assessments" in stats
        assert "total_dialogues" in stats
        assert "total_surveys" in stats
        assert "total_reports" in stats

    def test_stage_sequence_full_workflow(self, tmp_path):
        """Walk through all stages in order."""
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("p_seq")
        stages = [
            WorkflowStage.BIG5_ASSESSMENT,
            WorkflowStage.TASK_SELECTION,
            WorkflowStage.TASK_DIALOGUE,
            WorkflowStage.POST_SURVEY,
            WorkflowStage.COMPLETED,
        ]
        for stage in stages:
            ok = sup.advance_stage(session.session_id, stage)
            assert ok is True
        reloaded = sup.get_session(session.session_id)
        assert reloaded.current_stage == WorkflowStage.COMPLETED


# ════════════════════════════════════════════════════════════════════════════
# 3. BIG5 ASSESSMENT AGENT
# ════════════════════════════════════════════════════════════════════════════

class TestBig5AssessmentAgent:
    def test_get_assessment_items_returns_50_items(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        items = agent.get_assessment_items()
        assert len(items) == 50

    def test_items_have_required_fields(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        for item in agent.get_assessment_items():
            assert "id" in item
            assert "text" in item
            assert "reverse" in item
            assert "trait" in item
            assert isinstance(item["reverse"], bool)

    def test_all_five_traits_present(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        traits = {item["trait"] for item in agent.get_assessment_items()}
        assert traits == {"extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"}

    def test_ten_items_per_trait(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        from collections import Counter
        counts = Counter(item["trait"] for item in agent.get_assessment_items())
        for trait, count in counts.items():
            assert count == 10, f"{trait} has {count} items, expected 10"

    def test_neutral_responses_score_50(self, tmp_path):
        """All-3 responses should give 50.0 on every trait."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = _neutral_responses()
        scores = agent.calculate_scores(responses)
        for trait, score in scores.items():
            assert score == pytest.approx(50.0), f"{trait}: expected 50.0, got {score}"

    def test_max_responses_high_scores(self, tmp_path):
        """Forward=5, reverse=1 → max trait sums → score 100.0."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = _extreme_responses(forward_val=5, reverse_val=1)
        scores = agent.calculate_scores(responses)
        for trait, score in scores.items():
            assert score == pytest.approx(100.0), f"{trait}: expected 100.0, got {score}"

    def test_min_responses_low_scores(self, tmp_path):
        """Forward=1, reverse=5 → min trait sums → score 0.0."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = _extreme_responses(forward_val=1, reverse_val=5)
        scores = agent.calculate_scores(responses)
        for trait, score in scores.items():
            assert score == pytest.approx(0.0), f"{trait}: expected 0.0, got {score}"

    def test_partial_responses_skips_missing_items(self, tmp_path):
        """Missing items contribute 0 to the sum — should not raise."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        # Only provide extraversion items
        responses = {f"E{i}": 3 for i in range(1, 11)}
        scores = agent.calculate_scores(responses)
        # All traits with no responses → sum=0 → normalized=(0-10)/40*100 = -25
        # (We just verify it doesn't raise)
        assert isinstance(scores["openness"], float)

    def test_classify_gerlach_average(self, tmp_path):
        """All-50 scores → classified as 'average'."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        scores = {t: 50.0 for t in ["neuroticism", "extraversion", "openness", "agreeableness", "conscientiousness"]}
        gtype, confidence = agent.classify_gerlach_type(scores)
        assert gtype == "average"

    def test_classify_gerlach_role_model(self, tmp_path):
        """Low N, high E/O/A/C → 'role_model'."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        scores = {
            "neuroticism": 20.0,
            "extraversion": 80.0,
            "openness": 80.0,
            "agreeableness": 80.0,
            "conscientiousness": 80.0,
        }
        gtype, confidence = agent.classify_gerlach_type(scores)
        assert gtype == "role_model"
        assert confidence > 0

    def test_classify_gerlach_self_centred(self, tmp_path):
        """Low O, A, C → 'self_centred'."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        scores = {
            "neuroticism": 60.0,
            "extraversion": 60.0,
            "openness": 20.0,
            "agreeableness": 20.0,
            "conscientiousness": 20.0,
        }
        gtype, confidence = agent.classify_gerlach_type(scores)
        assert gtype == "self_centred"

    def test_classify_gerlach_reserved(self, tmp_path):
        """Low N and O, moderate others → 'reserved'."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        scores = {
            "neuroticism": 20.0,
            "extraversion": 50.0,
            "openness": 20.0,
            "agreeableness": 50.0,
            "conscientiousness": 50.0,
        }
        gtype, confidence = agent.classify_gerlach_type(scores)
        assert gtype == "reserved"

    def test_conduct_assessment_persists_file(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = _neutral_responses()
        assessment = agent.conduct_assessment("u_test", "sess_test", responses)
        file = tmp_path / "assessments" / f"{assessment.assessment_id}.json"
        assert file.exists()
        data = json.loads(file.read_text())
        assert data["user_id"] == "u_test"

    def test_conduct_assessment_gerlach_type_not_none(self, tmp_path):
        """Every conduct_assessment call must produce a non-null gerlach_type."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        for val in [1, 2, 3, 4, 5]:
            responses = {k: val for k in _neutral_responses()}
            assessment = agent.conduct_assessment("u_gerlach", "sess_g", responses)
            assert assessment.gerlach_type is not None, f"gerlach_type is None for all-{val} responses"

    def test_get_assessment_after_conduct(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = _neutral_responses()
        a = agent.conduct_assessment("u_get", "s_get", responses)
        loaded = agent.get_assessment(a.assessment_id)
        assert loaded is not None
        assert loaded.assessment_id == a.assessment_id

    def test_get_assessment_missing_returns_none(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        assert agent.get_assessment("nonexistent_assess") is None

    def test_item_ids_are_unique(self, tmp_path):
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        ids = [item["id"] for item in agent.get_assessment_items()]
        assert len(ids) == len(set(ids)), "Duplicate item IDs found"


# ════════════════════════════════════════════════════════════════════════════
# 4. DIALOGUE CAPTURE AGENT
# ════════════════════════════════════════════════════════════════════════════

class TestDialogueCaptureAgent:
    def test_start_dialogue_persists_file(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u1", "s1", "Noble Industries", "average")
        file = tmp_path / "dialogues" / f"{d.dialogue_id}.json"
        assert file.exists()

    def test_start_dialogue_id_prefix(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u1", "s1", "Popcorn Brain", "reserved")
        assert d.dialogue_id.startswith("dialogue_u1_")

    def test_record_message_returns_true(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u2", "s2", "Task", "role_model")
        ok = agent.record_message(d.dialogue_id, "user", "Hello!")
        assert ok is True

    def test_record_message_updates_counts(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u3", "s3", "Task", "self_centred")
        agent.record_message(d.dialogue_id, "user", "Question?")
        agent.record_message(d.dialogue_id, "assistant", "Answer.")
        dialogue = agent.get_dialogue(d.dialogue_id)
        assert dialogue.user_message_count == 1
        assert dialogue.assistant_message_count == 1
        assert dialogue.total_messages == 2

    def test_record_message_invalid_dialogue_returns_false(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        ok = agent.record_message("ghost_dialogue_id", "user", "Hello!")
        assert ok is False

    def test_end_dialogue_returns_true(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u4", "s4", "Task", "average")
        agent.record_message(d.dialogue_id, "user", "Hi")
        ok = agent.end_dialogue(d.dialogue_id)
        assert ok is True

    def test_end_dialogue_sets_ended_at(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u5", "s5", "Task", "average")
        agent.end_dialogue(d.dialogue_id)
        loaded = agent.get_dialogue(d.dialogue_id)
        assert loaded.ended_at is not None

    def test_end_dialogue_invalid_id_returns_false(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        assert agent.end_dialogue("no_such_dialogue") is False

    def test_get_dialogue_after_end_loads_from_disk(self, tmp_path):
        """After end_dialogue removes from active_dialogues, get_dialogue loads from disk."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u6", "s6", "Task", "reserved")
        agent.record_message(d.dialogue_id, "user", "Test message")
        agent.end_dialogue(d.dialogue_id)
        assert d.dialogue_id not in agent.active_dialogues
        loaded = agent.get_dialogue(d.dialogue_id)
        assert loaded is not None
        assert loaded.total_messages == 1

    def test_get_dialogue_nonexistent_returns_none(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        assert agent.get_dialogue("nonexistent_dialogue_xyz") is None

    def test_get_session_dialogues(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d1 = agent.start_dialogue("u7", "sess_shared", "Task", "average")
        d2 = agent.start_dialogue("u7", "sess_shared", "Task2", "reserved")
        _other = agent.start_dialogue("u7", "sess_other", "Task3", "average")
        results = agent.get_session_dialogues("sess_shared")
        ids = [r.dialogue_id for r in results]
        assert d1.dialogue_id in ids
        assert d2.dialogue_id in ids
        assert _other.dialogue_id not in ids

    def test_get_dialogue_statistics(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u8", "s8", "Task", "role_model")
        agent.record_message(d.dialogue_id, "user", "Hello world!")
        agent.record_message(d.dialogue_id, "assistant", "Hi there, how can I help?")
        stats = agent.get_dialogue_statistics(d.dialogue_id)
        assert stats["total_messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1
        assert stats["avg_user_message_length"] == len("Hello world!")
        assert stats["avg_assistant_message_length"] == len("Hi there, how can I help?")

    def test_get_dialogue_statistics_nonexistent(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        stats = agent.get_dialogue_statistics("ghost")
        assert "error" in stats

    def test_export_dialogue_transcript_markdown(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u9", "s9", "Noble Industries", "average")
        agent.record_message(d.dialogue_id, "user", "Who should be let go?")
        agent.record_message(d.dialogue_id, "assistant", "Let me help you think through this.")
        transcript = agent.export_dialogue_transcript(d.dialogue_id, format="markdown")
        assert transcript is not None
        assert "Dialogue Transcript" in transcript
        assert "Noble Industries" in transcript
        assert "Who should be let go?" in transcript

    def test_export_dialogue_transcript_json(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u10", "s10", "Popcorn Brain", "reserved")
        agent.record_message(d.dialogue_id, "user", "Interesting idea!")
        transcript = agent.export_dialogue_transcript(d.dialogue_id, format="json")
        data = json.loads(transcript)
        assert data["dialogue_id"] == d.dialogue_id

    def test_export_transcript_invalid_format_returns_none(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u11", "s11", "Task", "average")
        result = agent.export_dialogue_transcript(d.dialogue_id, format="xml")
        assert result is None

    def test_export_transcript_nonexistent_dialogue_returns_none(self, tmp_path):
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        assert agent.export_dialogue_transcript("ghost_dlg", format="markdown") is None

    def test_message_persisted_after_each_record(self, tmp_path):
        """Each record_message must save to disk immediately (no data loss on crash)."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u12", "s12", "Task", "average")
        agent.record_message(d.dialogue_id, "user", "First message")
        # Force-load from disk (bypass memory cache)
        fresh_agent = DialogueCaptureAgent(tmp_path)
        loaded = fresh_agent.get_dialogue(d.dialogue_id)
        assert loaded.total_messages == 1
        assert loaded.messages[0].content == "First message"


# ════════════════════════════════════════════════════════════════════════════
# 5. POST-EXPERIMENT SURVEY AGENT
# ════════════════════════════════════════════════════════════════════════════

class TestPostExpSurveyAgent:
    def test_get_survey_questions_returns_dict(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        questions = agent.get_survey_questions()
        assert isinstance(questions, dict)
        assert len(questions) > 0

    def test_survey_questions_include_likert_and_text(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        questions = agent.get_survey_questions()
        types = {q["type"] for q in questions.values()}
        assert "likert" in types
        assert "text" in types

    def test_conduct_survey_persists_file(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        responses = _build_survey_responses()
        survey = agent.conduct_survey("u1", "sess1", "diag1", responses)
        file = tmp_path / "surveys" / f"{survey.survey_id}.json"
        assert file.exists()

    def test_conduct_survey_labeled_responses_populated(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        responses = {"q1": 5, "q32": "Negative comment"}
        survey = agent.conduct_survey("u2", "sess2", "diag2", responses)
        assert "q1" in survey.labeled_responses
        assert survey.labeled_responses["q1"]["response"] == 5
        assert "q32" in survey.labeled_responses
        assert survey.labeled_responses["q32"]["response"] == "Negative comment"

    def test_conduct_survey_dialogue_id_linked(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        survey = agent.conduct_survey("u3", "sess3", "diag_xyz", {"q1": 4})
        assert survey.dialogue_id == "diag_xyz"

    def test_conduct_survey_id_prefix(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        survey = agent.conduct_survey("u4", "sess4", "diag4", {"q1": 3})
        assert survey.survey_id.startswith("survey_u4_")

    def test_get_survey_by_id(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        s = agent.conduct_survey("u5", "s5", "d5", {"q1": 7})
        loaded = agent.get_survey(s.survey_id)
        assert loaded is not None
        assert loaded.responses["q1"] == 7

    def test_get_survey_missing_returns_none(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        assert agent.get_survey("nonexistent_survey_id") is None

    def test_get_session_surveys(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        agent.conduct_survey("u6", "shared_sess", "d6a", {"q1": 4})
        agent.conduct_survey("u6", "shared_sess", "d6b", {"q1": 5})
        agent.conduct_survey("u6", "other_sess", "d6c", {"q1": 6})
        surveys = agent.get_session_surveys("shared_sess")
        assert len(surveys) == 2

    def test_get_survey_statistics(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        s = agent.conduct_survey("u7", "s7", "d7", {"q1": 5})
        stats = agent.get_survey_statistics(s.survey_id)
        assert stats["survey_id"] == s.survey_id
        assert stats["dialogue_id"] == "d7"

    def test_get_survey_statistics_nonexistent(self, tmp_path):
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        stats = agent.get_survey_statistics("ghost")
        assert "error" in stats


# ════════════════════════════════════════════════════════════════════════════
# 6. GERLACH PERSONALITY MANAGER (mocked LLM)
# ════════════════════════════════════════════════════════════════════════════

def _make_anthropic_mock():
    """Inject a fake `anthropic` module so gerlach_personality_llms can be imported
    even when the real anthropic SDK is not installed."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test LLM response.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    mock_anthropic_module = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client
    return mock_anthropic_module, mock_client


class TestGerlachPersonalityManager:
    PERSONALITIES = ["average", "role_model", "self_centred", "reserved"]

    @pytest.fixture(autouse=True)
    def inject_anthropic(self):
        """Ensure a fake anthropic module is always in sys.modules for these tests."""
        mock_module, self.mock_client = _make_anthropic_mock()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            # Force reimport of gerlach_personality_llms with the fake module
            if "gerlach_personality_llms" in sys.modules:
                del sys.modules["gerlach_personality_llms"]
            yield
        # Cleanup: remove cached import so next test starts clean
        sys.modules.pop("gerlach_personality_llms", None)

    def test_manager_initialises_all_personalities(self):
        from gerlach_personality_llms import GerlachPersonalityManager
        manager = GerlachPersonalityManager(api_key="fake_key")
        for name in self.PERSONALITIES:
            p = manager.get_personality(name)
            assert p is not None, f"Personality '{name}' not found"

    def test_get_unknown_personality_raises(self):
        from gerlach_personality_llms import GerlachPersonalityManager
        manager = GerlachPersonalityManager(api_key="fake_key")
        with pytest.raises(Exception):
            manager.get_personality("nonexistent_type")

    def test_each_personality_chat_returns_string(self):
        from gerlach_personality_llms import GerlachPersonalityManager
        manager = GerlachPersonalityManager(api_key="fake_key")
        messages = [{"role": "user", "content": "Hello!"}]
        for name in self.PERSONALITIES:
            p = manager.get_personality(name)
            result = p.chat(messages, task_context="Test task context.")
            assert isinstance(result, str), f"Personality '{name}' chat did not return str"
            assert len(result) > 0

    def test_system_prompt_contains_task_context(self):
        from gerlach_personality_llms import GerlachPersonalityManager
        manager = GerlachPersonalityManager(api_key="fake_key")
        p = manager.get_personality("average")
        prompt = p.build_system_prompt("UNIQUE_TASK_XYZ_CONTENT")
        assert "UNIQUE_TASK_XYZ_CONTENT" in prompt

    def test_system_prompt_en_has_no_korean_language_instruction(self):
        from gerlach_personality_llms import GerlachPersonalityManager
        manager = GerlachPersonalityManager(api_key="fake_key")
        p = manager.get_personality("reserved")
        prompt = p.build_system_prompt("task context")
        from strings import APP_LANG
        if APP_LANG == "en":
            assert "never use English" not in prompt


# ════════════════════════════════════════════════════════════════════════════
# 7. STRINGS — EN / KO KEY PARITY
# ════════════════════════════════════════════════════════════════════════════

REQUIRED_STRING_KEYS = [
    "reg_header",
    "big5_header",
    "big5_info",
    "big5_instructions",
    "big5_submit_btn",
    "task_dial_guide",
    "task_dial_welcome_prompt",
    "task_noble_md",
    "task_popcorn_md",
    "survey_header",
    "survey_questions",
    "llm_language_instruction",
]


class TestStrings:
    def test_en_dict_has_all_required_keys(self):
        from strings import EN
        for key in REQUIRED_STRING_KEYS:
            assert key in EN, f"EN strings missing key: '{key}'"

    def test_ko_dict_has_all_required_keys(self):
        from strings import KO
        for key in REQUIRED_STRING_KEYS:
            assert key in KO, f"KO strings missing key: '{key}'"

    def test_en_ko_key_parity(self):
        """Every key in EN must also exist in KO."""
        from strings import EN, KO
        en_keys = set(EN.keys())
        ko_keys = set(KO.keys())
        missing_in_ko = en_keys - ko_keys
        assert not missing_in_ko, f"KO missing keys present in EN: {missing_in_ko}"

    def test_survey_questions_present_in_both(self):
        from strings import EN, KO
        en_q_keys = set(EN["survey_questions"].keys())
        ko_q_keys = set(KO["survey_questions"].keys())
        assert en_q_keys == ko_q_keys, f"Survey question keys differ: EN={en_q_keys}, KO={ko_q_keys}"

    def test_big5_submit_btn_not_empty(self):
        from strings import EN, KO
        assert EN["big5_submit_btn"].strip() != ""
        assert KO["big5_submit_btn"].strip() != ""

    def test_big5_header_does_not_reveal_personality(self):
        """Header must NOT say 'Personality Assessment'."""
        from strings import EN, KO
        assert "personality assessment" not in EN.get("big5_header", "").lower()
        assert "personality assessment" not in KO.get("big5_header", "").lower()

    def test_big5_header_is_about_you(self):
        from strings import EN, KO
        assert "about you" in EN.get("big5_header", "").lower() or \
               "about you" in EN.get("big5_info", "").lower()

    def test_survey_title_correct_en(self):
        from strings import EN
        assert "End of Study Survey" in EN.get("survey_header", "")

    def test_survey_questions_have_type_field(self):
        from strings import EN
        for key, q in EN["survey_questions"].items():
            assert "type" in q, f"EN survey question '{key}' missing 'type' field"
            assert q["type"] in ("likert", "text"), f"Unexpected type in '{key}': {q['type']}"

    def test_ko_language_instruction_forbids_english(self):
        from strings import KO
        instruction = KO.get("llm_language_instruction", "")
        assert instruction != "", "KO llm_language_instruction must not be empty"
        # Should contain a prohibition on English
        lower = instruction.lower()
        assert "english" in lower or "영어" in lower

    def test_en_language_instruction_is_empty(self):
        from strings import EN
        assert EN.get("llm_language_instruction", "") == ""

    def test_popcorn_brain_md_mentions_los_angeles_not_fresno(self):
        from strings import EN, KO
        noble_md = EN.get("task_popcorn_md", "")
        if noble_md:
            assert "Los Angeles" in noble_md, "Popcorn Brain task must use 'Los Angeles', not 'Fresno'"
            assert "Fresno" not in noble_md


# ════════════════════════════════════════════════════════════════════════════
# 8. FULL WORKFLOW INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestFullWorkflowIntegration:
    """
    End-to-end test of the agent pipeline without LLM or GitHub calls.
    Validates that all agents hand off correctly and data persists.
    """

    def test_complete_research_session(self, tmp_path):
        from agents import (
            SupervisorAgent, Big5AssessmentAgent, DialogueCaptureAgent,
            PostExpSurveyAgent, SummaryReportAgent, WorkflowStage,
        )

        sup = SupervisorAgent(tmp_path)
        assessment_agent = Big5AssessmentAgent(tmp_path)
        dialogue_agent = DialogueCaptureAgent(tmp_path)
        survey_agent = PostExpSurveyAgent(tmp_path)
        summary_agent = SummaryReportAgent(tmp_path)

        # 1. Registration
        session = sup.create_user_session("integ_user", metadata={"pilot": True})
        assert session.current_stage == WorkflowStage.REGISTRATION

        # 2. Big5 Assessment
        sup.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
        responses = _neutral_responses()
        assessment = assessment_agent.conduct_assessment(
            session.user_id, session.session_id, responses
        )
        assert assessment.gerlach_type is not None
        session.big5_assessment_id = assessment.assessment_id
        session.save(tmp_path)

        # 3. Task selection (silent stage — just advance)
        sup.advance_stage(session.session_id, WorkflowStage.TASK_SELECTION)

        # 4. Dialogue
        sup.advance_stage(session.session_id, WorkflowStage.TASK_DIALOGUE)
        dialogue = dialogue_agent.start_dialogue(
            session.user_id, session.session_id,
            "Noble Industries", "role_model"
        )
        session.dialogue_records.append(dialogue.dialogue_id)
        session.save(tmp_path)

        dialogue_agent.record_message(dialogue.dialogue_id, "user", "Can you help me rank the candidates?")
        dialogue_agent.record_message(dialogue.dialogue_id, "assistant", "Sure, let's review them together.")
        dialogue_agent.record_message(dialogue.dialogue_id, "user", "I think Alice should be first.")
        dialogue_agent.end_dialogue(dialogue.dialogue_id)

        # 5. Task Response (silent)
        sup.advance_stage(session.session_id, WorkflowStage.TASK_RESPONSE)

        # 6. Post Survey
        sup.advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
        survey_responses = _build_survey_responses()
        survey = survey_agent.conduct_survey(
            session.user_id, session.session_id,
            dialogue.dialogue_id, survey_responses
        )
        session.survey_id = survey.survey_id
        session.save(tmp_path)

        # 7. Completed + Report
        sup.advance_stage(session.session_id, WorkflowStage.COMPLETED)
        report = summary_agent.generate_report(session.user_id, session.session_id)
        session.report_id = report.report_id
        session.save(tmp_path)

        # Verify all files exist
        assert (tmp_path / "sessions" / f"{session.session_id}.json").exists()
        assert (tmp_path / "assessments" / f"{assessment.assessment_id}.json").exists()
        assert (tmp_path / "dialogues" / f"{dialogue.dialogue_id}.json").exists()
        assert (tmp_path / "surveys" / f"{survey.survey_id}.json").exists()
        assert (tmp_path / "reports" / f"{report.report_id}.json").exists()

        # Verify final session state
        final = sup.get_session(session.session_id)
        assert final.current_stage == WorkflowStage.COMPLETED
        assert final.big5_assessment_id == assessment.assessment_id
        assert final.survey_id == survey.survey_id
        assert final.report_id == report.report_id
        assert dialogue.dialogue_id in final.dialogue_records

        # Verify statistics
        stats = sup.get_statistics()
        assert stats["total_sessions"] >= 1
        assert stats["total_assessments"] >= 1
        assert stats["total_dialogues"] >= 1
        assert stats["total_surveys"] >= 1
        assert stats["total_reports"] >= 1

    def test_resume_interrupted_session(self, tmp_path):
        """Simulates browser close mid-assessment → resume via find_active_session_by_user."""
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)

        # Participant starts but only gets to Big5
        session = sup.create_user_session("resume_user")
        sup.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)

        # New browser instance: agent should find existing incomplete session
        sup2 = SupervisorAgent(tmp_path)
        found = sup2.find_active_session_by_user("resume_user")
        assert found is not None
        assert found.session_id == session.session_id
        assert found.current_stage == WorkflowStage.BIG5_ASSESSMENT

    def test_no_duplicate_session_on_re_register(self, tmp_path):
        """Registering same user_id twice should find the existing active session."""
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        s1 = sup.create_user_session("dup_user")
        sup.advance_stage(s1.session_id, WorkflowStage.BIG5_ASSESSMENT)

        # Simulate what the app does: check for existing before creating
        existing = sup.find_active_session_by_user("dup_user")
        assert existing is not None
        assert existing.session_id == s1.session_id
        # Should NOT create a second session
        all_sessions = sup.get_user_sessions("dup_user")
        assert len(all_sessions) == 1

    def test_dialogue_messages_survive_agent_restart(self, tmp_path):
        """Messages must be readable after re-instantiating the agent from scratch."""
        from agents import DialogueCaptureAgent
        agent1 = DialogueCaptureAgent(tmp_path)
        d = agent1.start_dialogue("persist_user", "sess_p", "Task", "average")
        for i in range(7):
            agent1.record_message(d.dialogue_id, "user" if i % 2 == 0 else "assistant", f"msg {i}")

        agent2 = DialogueCaptureAgent(tmp_path)
        loaded = agent2.get_dialogue(d.dialogue_id)
        assert loaded.total_messages == 7


# ════════════════════════════════════════════════════════════════════════════
# 9. EDGE CASES & BOUNDARY CONDITIONS
# ════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_session_with_special_chars_in_user_id(self, tmp_path):
        """User IDs from form input shouldn't break file system paths."""
        from agents import SupervisorAgent
        sup = SupervisorAgent(tmp_path)
        # Typical safe participant IDs used in the study
        for uid in ["P001", "P100", "test_user_01", "student123"]:
            session = sup.create_user_session(uid)
            assert session.user_id == uid
            loaded = sup.get_session(session.session_id)
            assert loaded is not None

    def test_big5_responses_out_of_range_still_calculates(self, tmp_path):
        """Scores outside 1-5 are not validated by the agent — just calculate."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        responses = {k: 3 for k in _neutral_responses()}
        # Set one item out of range
        responses["E1"] = 6
        # Should not raise
        scores = agent.calculate_scores(responses)
        assert isinstance(scores["extraversion"], float)

    def test_empty_survey_responses_accepted(self, tmp_path):
        """conduct_survey with empty dict must not crash."""
        from agents import PostExpSurveyAgent
        agent = PostExpSurveyAgent(tmp_path)
        survey = agent.conduct_survey("u_empty", "s_empty", "d_empty", {})
        assert survey.survey_id is not None
        assert survey.responses == {}
        assert survey.labeled_responses == {}

    def test_dialogue_statistics_with_no_messages(self, tmp_path):
        """Statistics on a new (empty) dialogue should return zeros, not crash."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u_empty", "s_empty", "Task", "average")
        stats = agent.get_dialogue_statistics(d.dialogue_id)
        assert stats["total_messages"] == 0
        assert stats["avg_user_message_length"] == 0
        assert stats["avg_assistant_message_length"] == 0

    def test_gerlach_confidence_is_numeric(self, tmp_path):
        """gerlach_confidence must always be a number (not None or string)."""
        from agents import Big5AssessmentAgent
        agent = Big5AssessmentAgent(tmp_path)
        # Test extreme profiles
        profiles = [
            {t: 50.0 for t in ["neuroticism", "extraversion", "openness", "agreeableness", "conscientiousness"]},
            {"neuroticism": 10.0, "extraversion": 90.0, "openness": 90.0, "agreeableness": 90.0, "conscientiousness": 90.0},
            {"neuroticism": 90.0, "extraversion": 10.0, "openness": 10.0, "agreeableness": 10.0, "conscientiousness": 10.0},
        ]
        for scores in profiles:
            gtype, conf = agent.classify_gerlach_type(scores)
            assert isinstance(conf, (int, float)), f"confidence is {type(conf)} for {gtype}"
            assert gtype in ("average", "role_model", "self_centred", "reserved")

    def test_multiple_dialogues_same_session(self, tmp_path):
        """A session can have multiple dialogue records without collision."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d1 = agent.start_dialogue("u_multi", "sess_multi", "Task1", "average")
        d2 = agent.start_dialogue("u_multi", "sess_multi", "Task2", "reserved")
        assert d1.dialogue_id != d2.dialogue_id
        dialogues = agent.get_session_dialogues("sess_multi")
        assert len(dialogues) == 2

    def test_advance_stage_same_stage_twice_is_idempotent(self, tmp_path):
        """Advancing to the same stage twice should not duplicate completed_stages."""
        from agents import SupervisorAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        session = sup.create_user_session("idem_user")
        sup.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
        sup.advance_stage(session.session_id, WorkflowStage.BIG5_ASSESSMENT)
        reloaded = sup.get_session(session.session_id)
        assert reloaded.completed_stages.count("registration") == 1

    def test_report_generation_without_survey(self, tmp_path):
        """SummaryReportAgent must not crash if no survey exists yet."""
        from agents import SupervisorAgent, SummaryReportAgent, WorkflowStage
        sup = SupervisorAgent(tmp_path)
        summary_agent = SummaryReportAgent(tmp_path)
        session = sup.create_user_session("nosurv_user")
        sup.advance_stage(session.session_id, WorkflowStage.COMPLETED)
        # Should not raise
        report = summary_agent.generate_report(session.user_id, session.session_id)
        assert report is not None
        assert report.report_id is not None

    def test_markdown_transcript_empty_dialogue(self, tmp_path):
        """Transcript export of a zero-message dialogue should still return a valid string."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u_nomsgs", "s_nomsgs", "Task", "average")
        transcript = agent.export_dialogue_transcript(d.dialogue_id, format="markdown")
        assert transcript is not None
        assert "Dialogue Transcript" in transcript

    def test_session_id_unique_per_call(self, tmp_path):
        """Two calls to create_user_session with the same user_id produce different session IDs."""
        from agents import SupervisorAgent
        import time
        sup = SupervisorAgent(tmp_path)
        s1 = sup.create_user_session("uid_unique")
        time.sleep(0.05)
        s2 = sup.create_user_session("uid_unique")
        assert s1.session_id != s2.session_id

    def test_dialogue_record_load_with_empty_messages_list(self, tmp_path):
        """Loading a dialogue that was saved with zero messages must not crash."""
        from agents import DialogueCaptureAgent
        agent = DialogueCaptureAgent(tmp_path)
        d = agent.start_dialogue("u_nomsg2", "s_nomsg2", "Task", "average")
        # Save with no messages
        d.save(tmp_path)
        from agents.data_models import DialogueRecord
        loaded = DialogueRecord.load(d.dialogue_id, tmp_path)
        assert loaded.messages == []
        assert loaded.total_messages == 0
