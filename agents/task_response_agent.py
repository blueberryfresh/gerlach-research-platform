"""
Task Response Agent
Captures and processes task-specific responses (Noble Industries, Popcorn Brain)
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import uuid
import logging
import re

from .task_response_models import (
    NobleIndustriesResponse,
    PopcornBrainResponse,
    CreativeDimension
)
from .dialogue_capture_agent import DialogueCaptureAgent


class TaskResponseAgent:
    """
    Agent responsible for capturing task-specific responses
    and computing automated metrics
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
        # Create task_responses directories
        (self.data_dir / "task_responses" / "noble").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "task_responses" / "popcorn").mkdir(parents=True, exist_ok=True)
    
    # ==================== NOBLE INDUSTRIES ====================
    
    def capture_noble_rankings(
        self,
        user_id: str,
        session_id: str,
        dialogue_id: str,
        rankings: List[Dict],
        metadata: Dict = None
    ) -> NobleIndustriesResponse:
        """
        Capture Noble Industries candidate rankings
        
        Args:
            rankings: List of dicts with {rank, candidate_name, rationale}
        """
        task_response_id = f"noble_{user_id}_{uuid.uuid4().hex[:8]}"
        
        response = NobleIndustriesResponse(
            task_response_id=task_response_id,
            session_id=session_id,
            dialogue_id=dialogue_id,
            user_id=user_id,
            submitted_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Add rankings
        for ranking in rankings:
            response.add_ranking(
                rank=ranking['rank'],
                candidate_name=ranking['candidate_name'],
                rationale=ranking['rationale']
            )
        
        # Save response
        response.save(self.data_dir)
        
        self.logger.info(f"Noble Industries response {task_response_id} captured for user {user_id}")
        return response
    
    def get_noble_response(self, task_response_id: str) -> Optional[NobleIndustriesResponse]:
        """Retrieve Noble Industries response by ID"""
        try:
            return NobleIndustriesResponse.load(task_response_id, self.data_dir)
        except FileNotFoundError:
            return None
    
    # ==================== POPCORN BRAIN ====================
    
    def capture_popcorn_assessment(
        self,
        user_id: str,
        session_id: str,
        dialogue_id: str,
        self_ratings: Dict[str, int],
        dialogue_agent: DialogueCaptureAgent,
        metadata: Dict = None
    ) -> PopcornBrainResponse:
        """
        Capture Popcorn Brain creative assessment
        
        Args:
            self_ratings: Dict with {originality, flexibility, elaboration, fluency} (1-7 scale)
            dialogue_agent: DialogueCaptureAgent to retrieve dialogue for analysis
        """
        task_response_id = f"popcorn_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Compute automated metrics from dialogue
        computed_metrics = self.compute_creative_metrics(dialogue_id, dialogue_agent)
        
        response = PopcornBrainResponse(
            task_response_id=task_response_id,
            session_id=session_id,
            dialogue_id=dialogue_id,
            user_id=user_id,
            submitted_at=datetime.now().isoformat(),
            originality_rating=self_ratings.get('originality', 4),
            flexibility_rating=self_ratings.get('flexibility', 4),
            elaboration_rating=self_ratings.get('elaboration', 4),
            fluency_rating=self_ratings.get('fluency', 4),
            originality=computed_metrics['originality'],
            flexibility=computed_metrics['flexibility'],
            elaboration=computed_metrics['elaboration'],
            fluency=computed_metrics['fluency'],
            total_ideas=computed_metrics['total_ideas'],
            unique_ideas=computed_metrics['unique_ideas'],
            alternative_approaches=computed_metrics['alternative_approaches'],
            detail_instances=computed_metrics['detail_instances'],
            ideas_per_minute=computed_metrics['ideas_per_minute'],
            metadata=metadata or {}
        )
        
        # Save response
        response.save(self.data_dir)
        
        self.logger.info(f"Popcorn Brain response {task_response_id} captured for user {user_id}")
        return response
    
    def get_popcorn_response(self, task_response_id: str) -> Optional[PopcornBrainResponse]:
        """Retrieve Popcorn Brain response by ID"""
        try:
            return PopcornBrainResponse.load(task_response_id, self.data_dir)
        except FileNotFoundError:
            return None
    
    # ==================== CREATIVE METRICS COMPUTATION ====================
    
    def compute_creative_metrics(
        self,
        dialogue_id: str,
        dialogue_agent: DialogueCaptureAgent
    ) -> Dict:
        """
        Compute creative metrics from dialogue
        Returns dict with originality, flexibility, elaboration, fluency dimensions
        """
        dialogue = dialogue_agent.get_dialogue(dialogue_id)
        if not dialogue:
            return self._empty_metrics()
        
        # Extract user messages only
        user_messages = [msg for msg in dialogue.messages if msg.role == 'user']
        
        if not user_messages:
            return self._empty_metrics()
        
        # Compute each dimension
        originality = self._compute_originality(user_messages)
        flexibility = self._compute_flexibility(user_messages)
        elaboration = self._compute_elaboration(user_messages)
        fluency = self._compute_fluency(user_messages, dialogue.duration_seconds)
        
        return {
            'originality': originality,
            'flexibility': flexibility,
            'elaboration': elaboration,
            'fluency': fluency,
            'total_ideas': fluency.computed_count,
            'unique_ideas': originality.computed_count,
            'alternative_approaches': flexibility.computed_count,
            'detail_instances': elaboration.computed_count,
            'ideas_per_minute': fluency.computed_count / (dialogue.duration_seconds / 60) if dialogue.duration_seconds else 0
        }
    
    def _compute_originality(self, messages: List) -> CreativeDimension:
        """
        Compute originality: uniqueness of ideas
        Looks for idea markers and counts unique ideas
        """
        idea_markers = [
            'could', 'should', 'what if', 'maybe', 'perhaps', 
            'idea:', 'suggestion:', 'propose', 'think we', 'how about'
        ]
        
        unique_ideas = set()
        examples = []
        
        for msg in messages:
            content = msg.content.lower()
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if any(marker in sentence for marker in idea_markers):
                    # Simple deduplication by content
                    if sentence and sentence not in unique_ideas:
                        unique_ideas.add(sentence)
                        if len(examples) < 5:  # Keep top 5 examples
                            examples.append(sentence[:100])  # Truncate long sentences
        
        return CreativeDimension(
            self_rating=4,  # Will be overwritten by user rating
            computed_count=len(unique_ideas),
            examples=examples
        )
    
    def _compute_flexibility(self, messages: List) -> CreativeDimension:
        """
        Compute flexibility: alternative approaches
        Looks for alternative markers and topic switches
        """
        alternative_markers = [
            'alternatively', 'another way', 'instead', 'or we could',
            'different approach', 'on the other hand', 'also', 'another option'
        ]
        
        alternatives = []
        examples = []
        
        for msg in messages:
            content = msg.content.lower()
            for marker in alternative_markers:
                if marker in content:
                    # Extract context around marker
                    idx = content.find(marker)
                    context = content[max(0, idx-20):min(len(content), idx+80)]
                    alternatives.append(context)
                    if len(examples) < 5:
                        examples.append(context.strip())
        
        return CreativeDimension(
            self_rating=4,
            computed_count=len(alternatives),
            examples=examples
        )
    
    def _compute_elaboration(self, messages: List) -> CreativeDimension:
        """
        Compute elaboration: detail density and synthesis
        Looks for detailed explanations and synthesis markers
        """
        detail_markers = [
            'specifically', 'in detail', 'for example', 'such as',
            'including', 'namely', 'step by step', 'first', 'second', 'then'
        ]
        
        synthesis_markers = [
            'combining', 'together', 'integrate', 'merge', 'build on',
            'expand on', 'adding to', 'based on'
        ]
        
        all_markers = detail_markers + synthesis_markers
        detail_instances = []
        examples = []
        
        for msg in messages:
            content = msg.content.lower()
            for marker in all_markers:
                if marker in content:
                    idx = content.find(marker)
                    context = content[max(0, idx-20):min(len(content), idx+80)]
                    detail_instances.append(context)
                    if len(examples) < 5:
                        examples.append(context.strip())
        
        return CreativeDimension(
            self_rating=4,
            computed_count=len(detail_instances),
            examples=examples
        )
    
    def _compute_fluency(self, messages: List, duration_seconds: Optional[float]) -> CreativeDimension:
        """
        Compute fluency: quantity of ideas
        Counts total ideas and calculates ideas per minute
        """
        idea_markers = [
            'could', 'should', 'what if', 'maybe', 'perhaps',
            'idea', 'suggestion', 'propose', 'think', 'how about',
            'let\'s', 'we can', 'we should'
        ]
        
        total_ideas = 0
        examples = []
        
        for msg in messages:
            content = msg.content.lower()
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                if any(marker in sentence for marker in idea_markers):
                    total_ideas += 1
                    if len(examples) < 5:
                        examples.append(sentence.strip()[:100])
        
        return CreativeDimension(
            self_rating=4,
            computed_count=total_ideas,
            examples=examples
        )
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        empty_dim = CreativeDimension(self_rating=4, computed_count=0, examples=[])
        return {
            'originality': empty_dim,
            'flexibility': empty_dim,
            'elaboration': empty_dim,
            'fluency': empty_dim,
            'total_ideas': 0,
            'unique_ideas': 0,
            'alternative_approaches': 0,
            'detail_instances': 0,
            'ideas_per_minute': 0.0
        }
    
    # ==================== UTILITY METHODS ====================
    
    def get_session_task_responses(self, session_id: str) -> List:
        """Get all task responses for a session"""
        responses = []
        
        # Check Noble Industries responses
        noble_dir = self.data_dir / "task_responses" / "noble"
        if noble_dir.exists():
            for response_file in noble_dir.glob("*.json"):
                try:
                    response = NobleIndustriesResponse.load(response_file.stem, self.data_dir)
                    if response.session_id == session_id:
                        responses.append(response)
                except Exception as e:
                    self.logger.error(f"Error loading Noble response {response_file}: {e}")
        
        # Check Popcorn Brain responses
        popcorn_dir = self.data_dir / "task_responses" / "popcorn"
        if popcorn_dir.exists():
            for response_file in popcorn_dir.glob("*.json"):
                try:
                    response = PopcornBrainResponse.load(response_file.stem, self.data_dir)
                    if response.session_id == session_id:
                        responses.append(response)
                except Exception as e:
                    self.logger.error(f"Error loading Popcorn response {response_file}: {e}")
        
        return responses
