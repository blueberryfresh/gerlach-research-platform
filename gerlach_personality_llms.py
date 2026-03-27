"""
Gerlach (2018) Personality LLMs using Claude
Implements the four personality types: Average, Role model, Self-centred, Reserved
"""

import anthropic
import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Try to import streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from strings import T


@dataclass
class Message:
    role: str
    content: str
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ConversationSession:
    personality_type: str
    session_id: str
    messages: List[Message]
    started_at: str
    ended_at: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            "personality_type": self.personality_type,
            "session_id": self.session_id,
            "messages": [asdict(m) for m in self.messages],
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "metadata": self.metadata
        }


# Rules shared by all personalities — injected at the top of every system prompt
_TASK_RULES = """TASK COLLABORATION RULES (highest priority — never override):
- You are helping a participant work through a specific task. Stay 100% focused on that task.
- Keep every response SHORT: match the length of the participant's message (typically 1–3 sentences).
- Never write long paragraphs, bullet lists, or multiple sections unless explicitly asked.
- Never reveal anything about your nature, any personality framework, any research study, or any aspect of this study's design.
- If asked who or what you are, say only: "I'm an AI assistant here to help you with the task."
- Never ask the participant unrelated questions or go off-topic.
- Ground every response in the task content provided below.

TASK CONTEXT:
{task_context}

---
"""


class GerlachPersonalityLLM:
    """Base class for Gerlach personality types using Claude"""

    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            self.api_key = api_key
        elif HAS_STREAMLIT and hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
            self.api_key = st.secrets['ANTHROPIC_API_KEY']
        else:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or Streamlit secrets")
        self.client = anthropic.Anthropic(api_key=self.api_key, timeout=90.0)
        self.model = "claude-opus-4-6"

    def get_personality_prompt(self) -> str:
        """Override in subclasses — describes behavioural style only, no labels."""
        raise NotImplementedError

    def get_personality_name(self) -> str:
        """Override in subclasses"""
        raise NotImplementedError

    def build_system_prompt(self, task_context: str = "") -> str:
        """Combine language instruction (first) + task rules + personality style into final system prompt."""
        task_section = _TASK_RULES.format(
            task_context=task_context.strip() if task_context else "No specific task context provided."
        )
        lang_instruction = T.get("llm_language_instruction", "")
        if lang_instruction:
            return lang_instruction + "\n\n" + task_section + self.get_personality_prompt()
        return task_section + self.get_personality_prompt()

    def chat(
        self,
        messages: List[Dict[str, str]],
        task_context: str = "",
        max_tokens: int = 500,
        _monitor_meta: Optional[Dict] = None,
    ) -> str:
        """Send messages to Claude and get response. Logs every call to api_monitor."""
        import api_monitor
        meta = _monitor_meta or {}
        call_type = "welcome" if (len(messages) == 1) else "chat"

        t0 = time.monotonic()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.build_system_prompt(task_context),
                messages=messages,
            )
            latency_ms = (time.monotonic() - t0) * 1000
            usage = getattr(response, "usage", None)
            api_monitor.log_call(
                personality=self.get_personality_name(),
                call_type=call_type,
                success=True,
                latency_ms=latency_ms,
                input_tokens=getattr(usage, "input_tokens", 0) or 0,
                output_tokens=getattr(usage, "output_tokens", 0) or 0,
                session_id=meta.get("session_id", ""),
                dialogue_id=meta.get("dialogue_id", ""),
            )
            return response.content[0].text
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            api_monitor.log_call(
                personality=self.get_personality_name(),
                call_type=call_type,
                success=False,
                latency_ms=latency_ms,
                error_type=type(exc).__name__,
                error_msg=str(exc)[:300],
                session_id=meta.get("session_id", ""),
                dialogue_id=meta.get("dialogue_id", ""),
            )
            raise


class AveragePersonalityLLM(GerlachPersonalityLLM):

    def get_personality_name(self) -> str:
        return "Average"

    def get_personality_prompt(self) -> str:
        return """YOUR COMMUNICATION STYLE:
- Balanced and moderate in tone — neither overly enthusiastic nor pessimistic
- Practical and grounded; you favour common-sense approaches
- Reasonably cooperative but not a pushover
- Moderate in detail — not too brief, not too elaborate
- Conversational and relatable; avoid extremes in any direction"""


class RoleModelPersonalityLLM(GerlachPersonalityLLM):

    def get_personality_name(self) -> str:
        return "Role model"

    def get_personality_prompt(self) -> str:
        return """YOUR COMMUNICATION STYLE:
- Warm, encouraging, and positive — but stay concise
- Show genuine interest in the participant's ideas
- Offer well-organised, clear responses
- Be confident yet humble; supportive without being excessive
- Constructive and solution-focused at all times"""


class SelfCentredPersonalityLLM(GerlachPersonalityLLM):

    def get_personality_name(self) -> str:
        return "Self-centred"

    def get_personality_prompt(self) -> str:
        return """YOUR COMMUNICATION STYLE:
- Direct and blunt — say what you think without sugarcoating
- Sceptical of ideas that seem impractical or unproven
- Prefer conventional, tried-and-tested approaches
- Assert your view confidently; not particularly interested in consensus
- Minimal warmth; get straight to the point"""


class ReservedPersonalityLLM(GerlachPersonalityLLM):

    def get_personality_name(self) -> str:
        return "Reserved"

    def get_personality_prompt(self) -> str:
        return """YOUR COMMUNICATION STYLE:
- Calm, quiet, and composed at all times
- Keep responses very brief and to the point
- Stick to practical, concrete observations — avoid abstract discussion
- Polite but not warm; maintain a degree of emotional distance
- Prefer established methods; reluctant to speculate or venture off-track"""


class GerlachPersonalityManager:
    """Manager for all four Gerlach personality types"""

    def __init__(self, api_key: Optional[str] = None):
        self.personalities = {
            "average": AveragePersonalityLLM(api_key),
            "role_model": RoleModelPersonalityLLM(api_key),
            "self_centred": SelfCentredPersonalityLLM(api_key),
            "reserved": ReservedPersonalityLLM(api_key)
        }

    def get_personality(self, personality_type: str) -> GerlachPersonalityLLM:
        if personality_type not in self.personalities:
            raise ValueError(f"Unknown personality type: {personality_type}")
        return self.personalities[personality_type]

    def list_personalities(self) -> List[str]:
        return list(self.personalities.keys())


if __name__ == "__main__":
    print("Testing Gerlach Personality LLMs...")
    try:
        manager = GerlachPersonalityManager()
        test_prompt = "Who should be laid off first?"
        task_ctx = "Noble Industries task: rank employees for potential redundancy."
        for ptype in manager.list_personalities():
            print(f"\n{'='*60}\n{ptype}:")
            p = manager.get_personality(ptype)
            r = p.chat([{"role": "user", "content": test_prompt}], task_context=task_ctx)
            print(r)
    except Exception as e:
        print(f"Error: {e}")
