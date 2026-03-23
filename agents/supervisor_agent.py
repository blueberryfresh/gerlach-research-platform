"""
Supervisor Agent - Coordinates all agents and manages workflow
"""

from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import uuid
import logging

from .data_models import UserSession, WorkflowStage


class SupervisorAgent:
    """
    Supervisor Agent coordinates the entire research workflow:
    1. Registration -> 2. Big5 Assessment -> 3. Task Selection -> 
    4. Task Dialogue -> 5. Post Survey -> 6. Report Generation
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for subdir in ['sessions', 'assessments', 'dialogues', 'surveys', 'reports']:
            (self.data_dir / subdir).mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, UserSession] = {}
    
    def create_user_session(self, user_id: str, metadata: Dict = None) -> UserSession:
        """Create a new user session"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            current_stage=WorkflowStage.REGISTRATION,
            metadata=metadata or {}
        )
        
        session.save(self.data_dir)
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        try:
            session = UserSession.load(session_id, self.data_dir)
            self.active_sessions[session_id] = session
            return session
        except Exception:
            return None
    
    def advance_stage(self, session_id: str, next_stage: WorkflowStage) -> bool:
        """Advance session to next workflow stage"""
        session = self.get_session(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        # Mark current stage as completed
        if session.current_stage.value not in session.completed_stages:
            session.completed_stages.append(session.current_stage.value)
        
        # Advance to next stage
        session.current_stage = next_stage
        session.save(self.data_dir)
        
        self.logger.info(f"Session {session_id} advanced to {next_stage.value}")
        return True
    
    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.current_stage = WorkflowStage.COMPLETED
        session.ended_at = datetime.now().isoformat()
        session.save(self.data_dir)
        
        self.logger.info(f"Session {session_id} completed")
        return True
    
    def find_active_session_by_user(self, user_id: str) -> Optional["UserSession"]:
        """Return the most recent incomplete session for a user_id, or None."""
        sessions_dir = self.data_dir / "sessions"
        if not sessions_dir.exists():
            return None
        candidates = []
        for path in sessions_dir.glob("*.json"):
            try:
                session = UserSession.load(path.stem, self.data_dir)
                if session.user_id == user_id and session.current_stage != WorkflowStage.COMPLETED:
                    candidates.append(session)
            except Exception:
                continue
        if not candidates:
            return None
        # Return the most recently started session
        candidates.sort(key=lambda s: s.started_at, reverse=True)
        best = candidates[0]
        self.active_sessions[best.session_id] = best
        return best

    def get_workflow_status(self, session_id: str) -> Dict:
        """Get current workflow status for a session"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        all_stages = [stage.value for stage in WorkflowStage]
        current_index = all_stages.index(session.current_stage.value)
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "current_stage": session.current_stage.value,
            "completed_stages": session.completed_stages,
            "progress_percentage": (len(session.completed_stages) / len(all_stages)) * 100,
            "next_stage": all_stages[current_index + 1] if current_index < len(all_stages) - 1 else None,
            "is_completed": session.current_stage == WorkflowStage.COMPLETED
        }
    
    def validate_stage_transition(self, session_id: str, target_stage: WorkflowStage) -> tuple[bool, str]:
        """Validate if stage transition is allowed"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        stage_order = [
            WorkflowStage.REGISTRATION,
            WorkflowStage.BIG5_ASSESSMENT,
            WorkflowStage.TASK_SELECTION,
            WorkflowStage.TASK_DIALOGUE,
            WorkflowStage.POST_SURVEY,
            WorkflowStage.COMPLETED
        ]
        
        current_idx = stage_order.index(session.current_stage)
        target_idx = stage_order.index(target_stage)
        
        # Allow moving forward one stage at a time, or backward
        if target_idx == current_idx + 1:
            return True, "Valid transition"
        elif target_idx <= current_idx:
            return True, "Backward navigation allowed"
        else:
            return False, f"Cannot skip stages. Complete {stage_order[current_idx + 1].value} first"
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all sessions for a user"""
        sessions = []
        sessions_dir = self.data_dir / "sessions"
        
        if not sessions_dir.exists():
            return sessions
        
        for session_file in sessions_dir.glob(f"{user_id}_*.json"):
            try:
                session = UserSession.load(session_file.stem, self.data_dir)
                sessions.append(session)
            except Exception as e:
                self.logger.error(f"Error loading session {session_file}: {e}")
        
        return sorted(sessions, key=lambda s: s.started_at, reverse=True)
    
    def get_statistics(self) -> Dict:
        """Get overall system statistics"""
        sessions_dir = self.data_dir / "sessions"
        assessments_dir = self.data_dir / "assessments"
        dialogues_dir = self.data_dir / "dialogues"
        surveys_dir = self.data_dir / "surveys"
        reports_dir = self.data_dir / "reports"
        
        return {
            "total_sessions": len(list(sessions_dir.glob("*.json"))) if sessions_dir.exists() else 0,
            "total_assessments": len(list(assessments_dir.glob("*.json"))) if assessments_dir.exists() else 0,
            "total_dialogues": len(list(dialogues_dir.glob("*.json"))) if dialogues_dir.exists() else 0,
            "total_surveys": len(list(surveys_dir.glob("*.json"))) if surveys_dir.exists() else 0,
            "total_reports": len(list(reports_dir.glob("*.json"))) if reports_dir.exists() else 0,
            "data_directory": str(self.data_dir)
        }
