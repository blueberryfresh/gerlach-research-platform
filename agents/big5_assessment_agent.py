"""
Big5 Personality Assessment Agent
Conducts Big5 assessment, scores it, and archives results
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import uuid
import logging

from .data_models import Big5Assessment
from strings import T


class Big5AssessmentAgent:
    """
    Agent responsible for conducting Big5 personality assessments
    Uses standard Big5 questionnaire (BFI-44 or IPIP-50)
    """
    
    # IPIP-50 Big Five Inventory (10 items per trait)
    ASSESSMENT_ITEMS = {
        "extraversion": [
            {"id": "E1", "text": "I am the life of the party.", "reverse": False},
            {"id": "E2", "text": "I don't talk a lot.", "reverse": True},
            {"id": "E3", "text": "I feel comfortable around people.", "reverse": False},
            {"id": "E4", "text": "I keep in the background.", "reverse": True},
            {"id": "E5", "text": "I start conversations.", "reverse": False},
            {"id": "E6", "text": "I have little to say.", "reverse": True},
            {"id": "E7", "text": "I talk to a lot of different people at parties.", "reverse": False},
            {"id": "E8", "text": "I don't like to draw attention to myself.", "reverse": True},
            {"id": "E9", "text": "I don't mind being the center of attention.", "reverse": False},
            {"id": "E10", "text": "I am quiet around strangers.", "reverse": True}
        ],
        "agreeableness": [
            {"id": "A1", "text": "I feel little concern for others.", "reverse": True},
            {"id": "A2", "text": "I am interested in people.", "reverse": False},
            {"id": "A3", "text": "I insult people.", "reverse": True},
            {"id": "A4", "text": "I sympathize with others' feelings.", "reverse": False},
            {"id": "A5", "text": "I am not interested in other people's problems.", "reverse": True},
            {"id": "A6", "text": "I have a soft heart.", "reverse": False},
            {"id": "A7", "text": "I am not really interested in others.", "reverse": True},
            {"id": "A8", "text": "I take time out for others.", "reverse": False},
            {"id": "A9", "text": "I feel others' emotions.", "reverse": False},
            {"id": "A10", "text": "I make people feel at ease.", "reverse": False}
        ],
        "conscientiousness": [
            {"id": "C1", "text": "I am always prepared.", "reverse": False},
            {"id": "C2", "text": "I leave my belongings around.", "reverse": True},
            {"id": "C3", "text": "I pay attention to details.", "reverse": False},
            {"id": "C4", "text": "I make a mess of things.", "reverse": True},
            {"id": "C5", "text": "I get chores done right away.", "reverse": False},
            {"id": "C6", "text": "I often forget to put things back in their proper place.", "reverse": True},
            {"id": "C7", "text": "I like order.", "reverse": False},
            {"id": "C8", "text": "I shirk my duties.", "reverse": True},
            {"id": "C9", "text": "I follow a schedule.", "reverse": False},
            {"id": "C10", "text": "I am exacting in my work.", "reverse": False}
        ],
        "neuroticism": [
            {"id": "N1", "text": "I get stressed out easily.", "reverse": False},
            {"id": "N2", "text": "I am relaxed most of the time.", "reverse": True},
            {"id": "N3", "text": "I worry about things.", "reverse": False},
            {"id": "N4", "text": "I seldom feel blue.", "reverse": True},
            {"id": "N5", "text": "I am easily disturbed.", "reverse": False},
            {"id": "N6", "text": "I get upset easily.", "reverse": False},
            {"id": "N7", "text": "I change my mood a lot.", "reverse": False},
            {"id": "N8", "text": "I have frequent mood swings.", "reverse": False},
            {"id": "N9", "text": "I get irritated easily.", "reverse": False},
            {"id": "N10", "text": "I often feel blue.", "reverse": False}
        ],
        "openness": [
            {"id": "O1", "text": "I have a rich vocabulary.", "reverse": False},
            {"id": "O2", "text": "I have difficulty understanding abstract ideas.", "reverse": True},
            {"id": "O3", "text": "I have a vivid imagination.", "reverse": False},
            {"id": "O4", "text": "I am not interested in abstract ideas.", "reverse": True},
            {"id": "O5", "text": "I have excellent ideas.", "reverse": False},
            {"id": "O6", "text": "I do not have a good imagination.", "reverse": True},
            {"id": "O7", "text": "I am quick to understand things.", "reverse": False},
            {"id": "O8", "text": "I use difficult words.", "reverse": False},
            {"id": "O9", "text": "I spend time reflecting on things.", "reverse": False},
            {"id": "O10", "text": "I am full of ideas.", "reverse": False}
        ]
    }
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
    
    def get_assessment_items(self) -> List[Dict]:
        """Get all assessment items with localised display text (from strings.T).
        The id and reverse fields are sourced from T["big5_items"] which mirrors
        ASSESSMENT_ITEMS — only the 'text' value is translated.
        """
        all_items = []
        for trait, items in T["big5_items"].items():
            for item in items:
                all_items.append({**item, "trait": trait})

        # Shuffle items for assessment (optional)
        # random.shuffle(all_items)
        return all_items
    
    def calculate_scores(self, responses: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate Big5 scores from responses
        Responses should be on 1-5 scale (Strongly Disagree to Strongly Agree)
        """
        scores = {
            "openness": 0.0,
            "conscientiousness": 0.0,
            "extraversion": 0.0,
            "agreeableness": 0.0,
            "neuroticism": 0.0
        }
        
        for trait, items in self.ASSESSMENT_ITEMS.items():
            trait_sum = 0
            for item in items:
                item_id = item["id"]
                if item_id not in responses:
                    continue
                
                score = responses[item_id]
                
                # Reverse scoring if needed
                if item["reverse"]:
                    score = 6 - score  # Reverse 1-5 scale
                
                trait_sum += score
            
            # Convert to 0-100 scale
            # Max possible: 10 items * 5 points = 50
            # Min possible: 10 items * 1 point = 10
            scores[trait] = ((trait_sum - 10) / 40) * 100
        
        return scores
    
    def classify_gerlach_type(self, scores: Dict[str, float]) -> tuple[str, float]:
        """
        Classify into Gerlach (2018) personality types
        Returns (type, confidence)
        """
        # Gerlach type definitions (simplified)
        # Average: All traits near 50
        # Role Model: Low N, High E/O/A/C
        # Self-Centred: Low O/A/C
        # Reserved: Low N/O, Moderate others
        
        n = scores["neuroticism"]
        e = scores["extraversion"]
        o = scores["openness"]
        a = scores["agreeableness"]
        c = scores["conscientiousness"]
        
        # Calculate distances to each type
        distances = {}
        
        # Average: all near 50
        distances["average"] = sum(abs(v - 50) for v in scores.values()) / 5
        
        # Role Model: N<40, E>60, O>60, A>60, C>60
        role_model_score = 0
        if n < 40: role_model_score += 20
        if e > 60: role_model_score += 20
        if o > 60: role_model_score += 20
        if a > 60: role_model_score += 20
        if c > 60: role_model_score += 20
        distances["role_model"] = 100 - role_model_score
        
        # Self-Centred: O<40, A<40, C<40
        self_centred_score = 0
        if o < 40: self_centred_score += 33.3
        if a < 40: self_centred_score += 33.3
        if c < 40: self_centred_score += 33.3
        distances["self_centred"] = 100 - self_centred_score
        
        # Reserved: N<40, O<40
        reserved_score = 0
        if n < 40: reserved_score += 50
        if o < 40: reserved_score += 50
        distances["reserved"] = 100 - reserved_score
        
        # Find closest type
        best_type = min(distances, key=distances.get)
        confidence = 100 - distances[best_type]
        
        return best_type, confidence
    
    def conduct_assessment(
        self,
        user_id: str,
        session_id: str,
        responses: Dict[str, int],
        metadata: Dict = None
    ) -> Big5Assessment:
        """
        Conduct assessment and create record
        """
        assessment_id = f"assessment_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Calculate scores
        scores = self.calculate_scores(responses)
        
        # Classify Gerlach type
        gerlach_type, confidence = self.classify_gerlach_type(scores)
        
        # Create assessment record
        assessment = Big5Assessment(
            assessment_id=assessment_id,
            user_id=user_id,
            session_id=session_id,
            conducted_at=datetime.now().isoformat(),
            openness=scores["openness"],
            conscientiousness=scores["conscientiousness"],
            extraversion=scores["extraversion"],
            agreeableness=scores["agreeableness"],
            neuroticism=scores["neuroticism"],
            responses=responses,
            gerlach_type=gerlach_type,
            gerlach_confidence=confidence,
            metadata=metadata or {}
        )
        
        # Save assessment
        assessment.save(self.data_dir)
        
        self.logger.info(f"Assessment {assessment_id} completed for user {user_id}")
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[Big5Assessment]:
        """Retrieve assessment by ID"""
        try:
            return Big5Assessment.load(assessment_id, self.data_dir)
        except FileNotFoundError:
            return None
