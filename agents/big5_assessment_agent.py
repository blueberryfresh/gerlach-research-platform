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
import strings


class Big5AssessmentAgent:
    """
    Agent responsible for conducting Big5 personality assessments
    Uses standard Big5 questionnaire (BFI-44 or IPIP-50)
    """

    # IPIP-50 — English
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

    # IPIP-50 — Korean (한국어)
    ASSESSMENT_ITEMS_KO = {
        "extraversion": [
            {"id": "E1",  "text": "나는 파티의 분위기를 이끈다.",                          "reverse": False},
            {"id": "E2",  "text": "나는 말을 많이 하지 않는다.",                           "reverse": True},
            {"id": "E3",  "text": "나는 사람들과 함께 있으면 편안함을 느낀다.",             "reverse": False},
            {"id": "E4",  "text": "나는 뒤에서 조용히 있는 편이다.",                       "reverse": True},
            {"id": "E5",  "text": "나는 대화를 먼저 시작한다.",                            "reverse": False},
            {"id": "E6",  "text": "나는 할 말이 별로 없다.",                               "reverse": True},
            {"id": "E7",  "text": "나는 파티에서 많은 다양한 사람들과 이야기를 나눈다.",    "reverse": False},
            {"id": "E8",  "text": "나는 주목받는 것을 좋아하지 않는다.",                   "reverse": True},
            {"id": "E9",  "text": "나는 관심의 중심이 되는 것이 괜찮다.",                  "reverse": False},
            {"id": "E10", "text": "나는 낯선 사람들과 함께 있으면 조용히 있는 편이다.",    "reverse": True},
        ],
        "agreeableness": [
            {"id": "A1",  "text": "나는 다른 사람들에 대한 관심이 별로 없다.",             "reverse": True},
            {"id": "A2",  "text": "나는 사람들에 대한 관심이 많다.",                       "reverse": False},
            {"id": "A3",  "text": "나는 사람들을 모욕한다.",                               "reverse": True},
            {"id": "A4",  "text": "나는 다른 사람들의 감정에 공감한다.",                   "reverse": False},
            {"id": "A5",  "text": "나는 다른 사람들의 문제에 관심이 없다.",                "reverse": True},
            {"id": "A6",  "text": "나는 마음이 따뜻하다.",                                 "reverse": False},
            {"id": "A7",  "text": "나는 다른 사람들에게 별로 관심이 없다.",                "reverse": True},
            {"id": "A8",  "text": "나는 다른 사람들을 위해 시간을 낸다.",                  "reverse": False},
            {"id": "A9",  "text": "나는 다른 사람들의 감정을 느낀다.",                     "reverse": False},
            {"id": "A10", "text": "나는 사람들이 편안함을 느끼게 만든다.",                 "reverse": False},
        ],
        "conscientiousness": [
            {"id": "C1",  "text": "나는 항상 준비되어 있다.",                              "reverse": False},
            {"id": "C2",  "text": "나는 물건들을 여기저기 두고 다닌다.",                   "reverse": True},
            {"id": "C3",  "text": "나는 세부 사항에 주의를 기울인다.",                     "reverse": False},
            {"id": "C4",  "text": "나는 일을 엉망으로 만드는 편이다.",                     "reverse": True},
            {"id": "C5",  "text": "나는 집안일을 즉시 처리한다.",                          "reverse": False},
            {"id": "C6",  "text": "나는 물건을 제자리에 돌려놓는 것을 자주 잊는다.",       "reverse": True},
            {"id": "C7",  "text": "나는 질서를 좋아한다.",                                 "reverse": False},
            {"id": "C8",  "text": "나는 의무를 회피한다.",                                 "reverse": True},
            {"id": "C9",  "text": "나는 일정을 따른다.",                                   "reverse": False},
            {"id": "C10", "text": "나는 일에서 꼼꼼하다.",                                 "reverse": False},
        ],
        "neuroticism": [
            {"id": "N1",  "text": "나는 쉽게 스트레스를 받는다.",                          "reverse": False},
            {"id": "N2",  "text": "나는 대부분의 시간에 편안하다.",                        "reverse": True},
            {"id": "N3",  "text": "나는 여러 가지 것들에 대해 걱정한다.",                  "reverse": False},
            {"id": "N4",  "text": "나는 우울함을 거의 느끼지 않는다.",                     "reverse": True},
            {"id": "N5",  "text": "나는 쉽게 동요된다.",                                   "reverse": False},
            {"id": "N6",  "text": "나는 쉽게 화가 난다.",                                  "reverse": False},
            {"id": "N7",  "text": "나는 기분이 자주 바뀐다.",                              "reverse": False},
            {"id": "N8",  "text": "나는 감정 기복이 심하다.",                              "reverse": False},
            {"id": "N9",  "text": "나는 쉽게 짜증을 낸다.",                                "reverse": False},
            {"id": "N10", "text": "나는 자주 우울함을 느낀다.",                            "reverse": False},
        ],
        "openness": [
            {"id": "O1",  "text": "나는 어휘력이 풍부하다.",                               "reverse": False},
            {"id": "O2",  "text": "나는 추상적인 개념을 이해하는 데 어려움을 겪는다.",     "reverse": True},
            {"id": "O3",  "text": "나는 상상력이 풍부하다.",                               "reverse": False},
            {"id": "O4",  "text": "나는 추상적인 개념에 관심이 없다.",                     "reverse": True},
            {"id": "O5",  "text": "나는 훌륭한 아이디어를 가지고 있다.",                   "reverse": False},
            {"id": "O6",  "text": "나는 상상력이 좋지 않다.",                              "reverse": True},
            {"id": "O7",  "text": "나는 사물을 빠르게 이해한다.",                          "reverse": False},
            {"id": "O8",  "text": "나는 어려운 단어를 사용한다.",                          "reverse": False},
            {"id": "O9",  "text": "나는 사물에 대해 깊이 생각하는 데 시간을 보낸다.",        "reverse": False},
            {"id": "O10", "text": "나는 아이디어가 넘친다.",                               "reverse": False},
        ],
    }

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
    
    def get_assessment_items(self) -> List[Dict]:
        """Get all assessment items — Korean branch always returns Korean items."""
        all_items = []
        for trait, items in self.ASSESSMENT_ITEMS_KO.items():
            for item in items:
                all_items.append({**item, "trait": trait})
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
