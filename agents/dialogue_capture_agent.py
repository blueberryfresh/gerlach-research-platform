"""
Dialogue Capture Agent
Records and archives all user-LLM task-solving dialogues
"""

from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import uuid
import logging

from .data_models import DialogueRecord


class DialogueCaptureAgent:
    """
    Agent responsible for capturing and archiving all dialogue interactions
    between users and LLM personalities during task-solving sessions
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.active_dialogues: Dict[str, DialogueRecord] = {}
    
    def start_dialogue(
        self,
        user_id: str,
        session_id: str,
        task_name: str,
        llm_personality: str,
        metadata: Dict = None
    ) -> DialogueRecord:
        """Start a new dialogue recording session"""
        dialogue_id = f"dialogue_{user_id}_{uuid.uuid4().hex[:8]}"
        
        dialogue = DialogueRecord(
            dialogue_id=dialogue_id,
            user_id=user_id,
            session_id=session_id,
            task_name=task_name,
            llm_personality=llm_personality,
            started_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.active_dialogues[dialogue_id] = dialogue
        dialogue.save(self.data_dir)
        
        self.logger.info(f"Started dialogue {dialogue_id} for user {user_id} with {llm_personality}")
        return dialogue
    
    def record_message(
        self,
        dialogue_id: str,
        role: str,
        content: str,
        metadata: Dict = None
    ) -> bool:
        """Record a single message in the dialogue"""
        dialogue = self.get_dialogue(dialogue_id)
        if not dialogue:
            self.logger.error(f"Dialogue {dialogue_id} not found")
            return False
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        dialogue.add_message(role, content, message_id, metadata)
        
        # Save after each message to ensure no data loss
        dialogue.save(self.data_dir)
        
        self.logger.debug(f"Recorded {role} message in dialogue {dialogue_id}")
        return True
    
    def end_dialogue(self, dialogue_id: str) -> bool:
        """End a dialogue recording session"""
        dialogue = self.get_dialogue(dialogue_id)
        if not dialogue:
            return False
        
        dialogue.end_dialogue()
        dialogue.save(self.data_dir)
        
        # Remove from active dialogues
        if dialogue_id in self.active_dialogues:
            del self.active_dialogues[dialogue_id]
        
        self.logger.info(
            f"Ended dialogue {dialogue_id}: "
            f"{dialogue.total_messages} messages, "
            f"{dialogue.duration_seconds:.1f}s duration"
        )
        return True
    
    def get_dialogue(self, dialogue_id: str) -> Optional[DialogueRecord]:
        """Get dialogue by ID"""
        if dialogue_id in self.active_dialogues:
            return self.active_dialogues[dialogue_id]
        
        try:
            dialogue = DialogueRecord.load(dialogue_id, self.data_dir)
            return dialogue
        except Exception:
            return None
    
    def get_session_dialogues(self, session_id: str) -> List[DialogueRecord]:
        """Get all dialogues for a session"""
        dialogues = []
        dialogues_dir = self.data_dir / "dialogues"
        
        if not dialogues_dir.exists():
            return dialogues
        
        for dialogue_file in dialogues_dir.glob("*.json"):
            try:
                dialogue = DialogueRecord.load(dialogue_file.stem, self.data_dir)
                if dialogue.session_id == session_id:
                    dialogues.append(dialogue)
            except Exception as e:
                self.logger.error(f"Error loading dialogue {dialogue_file}: {e}")
        
        return sorted(dialogues, key=lambda d: d.started_at)
    
    def get_dialogue_statistics(self, dialogue_id: str) -> Dict:
        """Get statistics for a specific dialogue"""
        dialogue = self.get_dialogue(dialogue_id)
        if not dialogue:
            return {"error": "Dialogue not found"}
        
        # Calculate average message length
        user_msg_lengths = [len(msg.content) for msg in dialogue.messages if msg.role == 'user']
        assistant_msg_lengths = [len(msg.content) for msg in dialogue.messages if msg.role == 'assistant']
        
        return {
            "dialogue_id": dialogue_id,
            "task_name": dialogue.task_name,
            "llm_personality": dialogue.llm_personality,
            "total_messages": dialogue.total_messages,
            "user_messages": dialogue.user_message_count,
            "assistant_messages": dialogue.assistant_message_count,
            "duration_seconds": dialogue.duration_seconds,
            "avg_user_message_length": sum(user_msg_lengths) / len(user_msg_lengths) if user_msg_lengths else 0,
            "avg_assistant_message_length": sum(assistant_msg_lengths) / len(assistant_msg_lengths) if assistant_msg_lengths else 0,
            "started_at": dialogue.started_at,
            "ended_at": dialogue.ended_at
        }
    
    def export_dialogue_transcript(self, dialogue_id: str, format: str = "markdown") -> Optional[str]:
        """Export dialogue as formatted transcript"""
        dialogue = self.get_dialogue(dialogue_id)
        if not dialogue:
            return None
        
        if format == "markdown":
            return self._export_markdown(dialogue)
        elif format == "json":
            import json
            return json.dumps(dialogue.to_dict(), indent=2)
        else:
            return None
    
    def _export_markdown(self, dialogue: DialogueRecord) -> str:
        """Export dialogue as markdown transcript"""
        md = f"# Dialogue Transcript\n\n"
        md += f"**Dialogue ID:** {dialogue.dialogue_id}\n"
        md += f"**User:** {dialogue.user_id}\n"
        md += f"**Task:** {dialogue.task_name}\n"
        md += f"**LLM Personality:** {dialogue.llm_personality}\n"
        md += f"**Started:** {dialogue.started_at}\n"
        md += f"**Ended:** {dialogue.ended_at or 'In progress'}\n"
        md += f"**Total Messages:** {dialogue.total_messages}\n\n"
        md += "---\n\n"
        
        for msg in dialogue.messages:
            role_label = "**User:**" if msg.role == "user" else f"**{dialogue.llm_personality}:**"
            timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S")
            md += f"### {role_label} [{timestamp}]\n\n"
            md += f"{msg.content}\n\n"
        
        return md
