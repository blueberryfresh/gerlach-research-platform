"""
Task Response Data Models
Data structures for task-specific responses (Noble Industries, Popcorn Brain)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from pathlib import Path


@dataclass
class CandidateRanking:
    """Single candidate ranking in Noble Industries task"""
    rank: int
    candidate_name: str
    rationale: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NobleIndustriesResponse:
    """Noble Industries task response - candidate rankings and rationales"""
    task_response_id: str
    session_id: str
    dialogue_id: str
    user_id: str
    submitted_at: str
    
    # Rankings data
    rankings: List[CandidateRanking] = field(default_factory=list)
    
    # Metadata
    total_candidates: int = 0
    time_to_complete_seconds: Optional[float] = None
    ranking_changes: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_ranking(self, rank: int, candidate_name: str, rationale: str):
        """Add a candidate ranking"""
        ranking = CandidateRanking(
            rank=rank,
            candidate_name=candidate_name,
            rationale=rationale
        )
        self.rankings.append(ranking)
        self.total_candidates = len(self.rankings)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        return data
    
    def save(self, data_dir: Path):
        """Save Noble Industries response to JSON file"""
        response_file = data_dir / "task_responses" / "noble" / f"{self.task_response_id}.json"
        response_file.parent.mkdir(parents=True, exist_ok=True)
        with open(response_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, task_response_id: str, data_dir: Path):
        """Load Noble Industries response from JSON file"""
        response_file = data_dir / "task_responses" / "noble" / f"{task_response_id}.json"
        with open(response_file, 'r') as f:
            data = json.load(f)
        
        # Reconstruct CandidateRanking objects
        rankings = [CandidateRanking(**r) for r in data.pop('rankings', [])]
        response = cls(**data)
        response.rankings = rankings
        return response


@dataclass
class CreativeDimension:
    """Single creative dimension measurement"""
    self_rating: int  # 1-7 scale
    computed_count: int  # Actual count from dialogue
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PopcornBrainResponse:
    """Popcorn Brain task response - creative performance metrics"""
    task_response_id: str
    session_id: str
    dialogue_id: str
    user_id: str
    submitted_at: str
    
    # Self-assessment (1-7 scale)
    originality_rating: int = 4
    flexibility_rating: int = 4
    elaboration_rating: int = 4
    fluency_rating: int = 4
    
    # Computed metrics from dialogue
    originality: Optional[CreativeDimension] = None
    flexibility: Optional[CreativeDimension] = None
    elaboration: Optional[CreativeDimension] = None
    fluency: Optional[CreativeDimension] = None
    
    # Aggregate metrics
    total_ideas: int = 0
    unique_ideas: int = 0
    alternative_approaches: int = 0
    detail_instances: int = 0
    ideas_per_minute: float = 0.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        return data
    
    def save(self, data_dir: Path):
        """Save Popcorn Brain response to JSON file"""
        response_file = data_dir / "task_responses" / "popcorn" / f"{self.task_response_id}.json"
        response_file.parent.mkdir(parents=True, exist_ok=True)
        with open(response_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, task_response_id: str, data_dir: Path):
        """Load Popcorn Brain response from JSON file"""
        response_file = data_dir / "task_responses" / "popcorn" / f"{task_response_id}.json"
        with open(response_file, 'r') as f:
            data = json.load(f)
        
        # Reconstruct CreativeDimension objects
        if data.get('originality'):
            data['originality'] = CreativeDimension(**data['originality'])
        if data.get('flexibility'):
            data['flexibility'] = CreativeDimension(**data['flexibility'])
        if data.get('elaboration'):
            data['elaboration'] = CreativeDimension(**data['elaboration'])
        if data.get('fluency'):
            data['fluency'] = CreativeDimension(**data['fluency'])
        
        return cls(**data)
