"""
Data models for the multi-agent system
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class WorkflowStage(Enum):
    """Workflow stages for user session"""
    REGISTRATION = "registration"
    BIG5_ASSESSMENT = "big5_assessment"
    TASK_SELECTION = "task_selection"
    TASK_DIALOGUE = "task_dialogue"
    TASK_RESPONSE = "task_response"
    POST_SURVEY = "post_survey"
    COMPLETED = "completed"


@dataclass
class UserSession:
    """Main user session tracking all activities"""
    user_id: str
    session_id: str
    started_at: str
    current_stage: WorkflowStage = WorkflowStage.REGISTRATION
    completed_stages: List[str] = field(default_factory=list)
    big5_assessment_id: Optional[str] = None
    dialogue_records: List[str] = field(default_factory=list)  # List of dialogue IDs
    task_response_ids: List[str] = field(default_factory=list)  # List of task response IDs
    survey_id: Optional[str] = None
    report_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ended_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['current_stage'] = self.current_stage.value
        return data
    
    def save(self, data_dir: Path):
        """Save session to JSON file and GitHub."""
        data = self.to_dict()
        session_file = data_dir / "sessions" / f"{self.session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
        try:
            from github_storage import get_storage
            get_storage().write(f"sessions/{self.session_id}.json", data)
        except Exception:
            pass
    
    @classmethod
    def load(cls, session_id: str, data_dir: Path):
        """Load session from JSON file"""
        session_file = data_dir / "sessions" / f"{session_id}.json"
        with open(session_file, 'r') as f:
            data = json.load(f)
        data['current_stage'] = WorkflowStage(data['current_stage'])
        return cls(**data)


@dataclass
class Big5Assessment:
    """Big5 personality assessment results"""
    assessment_id: str
    user_id: str
    session_id: str
    conducted_at: str
    
    # Big5 scores (0-100 scale)
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    
    # Raw responses
    responses: Dict[str, Any] = field(default_factory=dict)
    
    # Gerlach personality type classification
    gerlach_type: Optional[str] = None
    gerlach_confidence: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def save(self, data_dir: Path):
        """Save assessment to JSON file and GitHub."""
        data = self.to_dict()
        assessment_file = data_dir / "assessments" / f"{self.assessment_id}.json"
        assessment_file.parent.mkdir(parents=True, exist_ok=True)
        with open(assessment_file, 'w') as f:
            json.dump(data, f, indent=2)
        try:
            from github_storage import get_storage
            get_storage().write(f"assessments/{self.assessment_id}.json", data)
        except Exception:
            pass
    
    @classmethod
    def load(cls, assessment_id: str, data_dir: Path):
        """Load assessment from JSON file"""
        assessment_file = data_dir / "assessments" / f"{assessment_id}.json"
        with open(assessment_file, 'r') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class DialogueMessage:
    """Single message in dialogue"""
    timestamp: str
    role: str  # 'user' or 'assistant'
    content: str
    message_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueRecord:
    """Complete dialogue record for a task session"""
    dialogue_id: str
    user_id: str
    session_id: str
    task_name: str
    llm_personality: str
    started_at: str
    ended_at: Optional[str] = None
    
    messages: List[DialogueMessage] = field(default_factory=list)
    
    # Analytics
    total_messages: int = 0
    user_message_count: int = 0
    assistant_message_count: int = 0
    duration_seconds: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, message_id: str, metadata: Dict = None):
        """Add a message to the dialogue"""
        msg = DialogueMessage(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            message_id=message_id,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.total_messages += 1
        if role == 'user':
            self.user_message_count += 1
        else:
            self.assistant_message_count += 1
    
    def end_dialogue(self):
        """Mark dialogue as ended and calculate duration from first message to Complete click."""
        self.ended_at = datetime.now().isoformat()
        end = datetime.fromisoformat(self.ended_at)
        if self.messages:
            # Duration = first message sent → Complete button clicked
            first_msg_time = datetime.fromisoformat(self.messages[0].timestamp)
            self.duration_seconds = (end - first_msg_time).total_seconds()
        else:
            # No messages — fall back to dialogue creation time
            self.duration_seconds = (end - datetime.fromisoformat(self.started_at)).total_seconds()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        return data
    
    def save(self, data_dir: Path):
        """Save dialogue to JSON file and GitHub."""
        data = self.to_dict()
        dialogue_file = data_dir / "dialogues" / f"{self.dialogue_id}.json"
        dialogue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dialogue_file, 'w') as f:
            json.dump(data, f, indent=2)
        try:
            from github_storage import get_storage
            get_storage().write(f"dialogues/{self.dialogue_id}.json", data)
        except Exception:
            pass
    
    @classmethod
    def load(cls, dialogue_id: str, data_dir: Path):
        """Load dialogue from JSON file"""
        dialogue_file = data_dir / "dialogues" / f"{dialogue_id}.json"
        with open(dialogue_file, 'r') as f:
            data = json.load(f)
        # Reconstruct DialogueMessage objects
        messages = [DialogueMessage(**msg) for msg in data.pop('messages', [])]
        record = cls(**data)
        record.messages = messages
        return record


@dataclass
class PostExpSurvey:
    """Post-experiment survey responses"""
    survey_id: str
    user_id: str
    session_id: str
    dialogue_id: str
    conducted_at: str
    
    # Survey responses (customizable)
    responses: Dict[str, Any] = field(default_factory=dict)

    # Labeled responses: q-key → {question, response} — for admin readability
    labeled_responses: Dict[str, Any] = field(default_factory=dict)

    # Satisfaction ratings (1-7 scale)
    task_difficulty: Optional[int] = None
    llm_helpfulness: Optional[int] = None
    overall_satisfaction: Optional[int] = None
    
    # Open-ended feedback
    what_worked_well: Optional[str] = None
    what_could_improve: Optional[str] = None
    additional_comments: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def save(self, data_dir: Path):
        """Save survey to JSON file and GitHub."""
        data = self.to_dict()
        survey_file = data_dir / "surveys" / f"{self.survey_id}.json"
        survey_file.parent.mkdir(parents=True, exist_ok=True)
        with open(survey_file, 'w') as f:
            json.dump(data, f, indent=2)
        try:
            from github_storage import get_storage
            get_storage().write(f"surveys/{self.survey_id}.json", data)
        except Exception:
            pass
    
    @classmethod
    def load(cls, survey_id: str, data_dir: Path):
        """Load survey from JSON file"""
        survey_file = data_dir / "surveys" / f"{survey_id}.json"
        with open(survey_file, 'r') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class UserReport:
    """Comprehensive user report with analytics"""
    report_id: str
    user_id: str
    session_id: str
    generated_at: str
    
    # Summary statistics
    big5_scores: Dict[str, float] = field(default_factory=dict)
    gerlach_type: Optional[str] = None
    total_dialogues: int = 0
    total_messages: int = 0
    total_time_seconds: float = 0.0
    
    # Task performance
    tasks_completed: List[str] = field(default_factory=list)
    llm_personalities_used: List[str] = field(default_factory=list)
    
    # Survey insights
    average_satisfaction: Optional[float] = None
    average_task_difficulty: Optional[float] = None
    
    # Detailed data references
    assessment_id: Optional[str] = None
    dialogue_ids: List[str] = field(default_factory=list)
    survey_ids: List[str] = field(default_factory=list)
    
    # Generated report content
    markdown_report: Optional[str] = None
    html_report: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def save(self, data_dir: Path):
        """Save report to JSON file and GitHub."""
        data = self.to_dict()
        report_file = data_dir / "reports" / f"{self.report_id}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Save markdown report if available
        if self.markdown_report:
            md_file = data_dir / "reports" / f"{self.report_id}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(self.markdown_report)

        # Save HTML report if available
        if self.html_report:
            html_file = data_dir / "reports" / f"{self.report_id}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(self.html_report)

        try:
            from github_storage import get_storage
            gh = get_storage()
            gh.write(f"reports/{self.report_id}.json", data)
            if self.markdown_report:
                gh.write_text(f"reports/{self.report_id}.md", self.markdown_report)
            if self.html_report:
                gh.write_text(f"reports/{self.report_id}.html", self.html_report)
        except Exception:
            pass
    
    @classmethod
    def load(cls, report_id: str, data_dir: Path):
        """Load report from JSON file"""
        report_file = data_dir / "reports" / f"{report_id}.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return cls(**data)
