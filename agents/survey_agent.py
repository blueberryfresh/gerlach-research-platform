"""
Post-Experiment Survey Agent
Conducts post-task surveys and archives responses
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import uuid
import logging

from .data_models import PostExpSurvey
from strings import T


class PostExpSurveyAgent:
    """
    Agent responsible for conducting post-experiment surveys
    after users complete task-solving dialogues
    """
    
    # LLM-Human Collaboration Post Session Questionnaire (rev5 — 32 questions; q2, q27-q30 dropped)
    # Likert scale questions (1-7): 1=Strongly Disagree, 7=Strongly Agree
    SURVEY_QUESTIONS = {
        "q1": {
            "question": "I am confident that our work (output) is done correctly.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q3": {
            "question": "I believe that our output has effectively solved the given task.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q4": {
            "question": "I enjoyed the LLM-Human collaboration more than doing it alone.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q5": {
            "question": "In the LLM-Human collaboration, the LLM and I disagreed frequently in reaching a solution.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q6": {
            "question": "In the LLM-Human collaboration, I believe that I had an easier time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q7": {
            "question": "In the LLM-Human collaboration, I believe that we had a much longer time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q8": {
            "question": "In the LLM-Human collaboration, I did not like the LLM's suggestion or view, but I compromised to do (or follow) the LLM's way.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q9": {
            "question": "In the LLM-Human collaboration, the feeling of trusting the LLM grew stronger as the session went on.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q10": {
            "question": "The LLM showed things that I did not know about.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q11": {
            "question": "The LLM showed compassion towards me.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q12": {
            "question": "The LLM showed no emotion and only dealt with facts.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q13": {
            "question": "In the LLM-Human collaboration, I really enjoyed my LLM partner's partnership (willing to work as a team, open-minded, etc.).",
            "type": "likert",
            "scale": (1, 7)
        },
        "q14": {
            "question": "In the LLM-Human collaboration, my partner insisted on doing things his way and/or did not collaborate.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q15": {
            "question": "In the LLM-Human collaboration, I was NOT able to fully exercise my knowledge and skills.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q16": {
            "question": "In the LLM-Human collaboration, I believe that I am a compatible partner to the LLM.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q17": {
            "question": "In the LLM-Human collaboration, it was my politeness and etiquette that got me through the collaboration sessions, NOT my true self (personality).",
            "type": "likert",
            "scale": (1, 7)
        },
        "q18": {
            "question": "In the LLM-Human collaboration, I believe that I have a compatible personality with the LLM.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q19": {
            "question": "In the LLM-Human collaboration, I did NOT reveal my true self or personality during the whole session.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q20": {
            "question": "In the LLM-Human collaboration, the LLM was thoughtful and forgiving with my mistakes.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q21": {
            "question": "In the LLM-Human collaboration, there were times when I was withdrawn (or maybe upset) because of disagreements with the partner.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q22": {
            "question": "I think the LLM-Human collaboration is a form of cheating as it takes away from one's ability to truly learn on his or her own.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q23": {
            "question": "I don't think I can achieve higher productivity next time if I am paired with the LLM again.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q24": {
            "question": "In the LLM-Human collaboration, the LLM described his or her point very well and I was able to fully understand.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q25": {
            "question": "In the LLM-Human collaboration, the LLM did not express nor communicate much (too quiet), which made the collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q26": {
            "question": "In the LLM-Human collaboration, the LLM's message delivery was unclear, which made the collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q31": {
            "question": "In the LLM-Human collaboration, I think the partner's gender can be an issue.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q32": {
            "question": "Briefly describe any conflicts or negative impacts from the LLM that you experienced during the collaboration, which you think influenced or affected the collaboration session and its productivity.",
            "type": "text",
            "placeholder": "Describe any conflicts or negative impacts..."
        },
        "q33": {
            "question": "Describe any positive impacts from the LLM that you experienced during the collaboration, which you think influenced or contributed to the collaboration productivity.",
            "type": "text",
            "placeholder": "Describe positive impacts..."
        },
        "q34": {
            "question": "Discuss the compatibility (personality, communication, or other aspects) between you and the LLM. If it was good, why? If not, why not? Do you think you can achieve high productivity with the LLM again?",
            "type": "text",
            "placeholder": "Discuss compatibility..."
        },
        "q35": {
            "question": "Besides the LLM's ability to contribute to the task, how did the LLM's personality play a role in your collaboration with the LLM? Was the personality compatible or not? Describe.",
            "type": "text",
            "placeholder": "Describe the LLM's personality role..."
        },
        "q36": {
            "question": "Besides the LLM's ability to contribute to the task, how did the LLM's communication skills play a role in your collaboration? Did the level of communication skill that the LLM exhibited bring a positive (or negative) feeling and impact to your collaboration with the LLM? Describe.",
            "type": "text",
            "placeholder": "Describe the LLM's communication skill impact..."
        },
        "q38": {
            "question": "What is your gender?",
            "type": "text",
            "placeholder": "e.g., Male, Female, Non-binary, Prefer not to say..."
        },
        "q39": {
            "question": "What is your major?",
            "type": "text",
            "placeholder": "e.g., Computer Science, Psychology, Business..."
        },
    }
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
    
    def get_survey_questions(self) -> Dict:
        """Get all survey questions (localised via strings.T)"""
        return T["survey_questions"]
    
    def conduct_survey(
        self,
        user_id: str,
        session_id: str,
        dialogue_id: str,
        responses: Dict[str, any],
        metadata: Dict = None
    ) -> PostExpSurvey:
        """
        Conduct post-experiment survey and create record
        """
        survey_id = f"survey_{user_id}_{uuid.uuid4().hex[:8]}"

        # Build labeled_responses: maps each q-key to its question text and the participant's answer
        labeled_responses = {}
        for q_key, response_value in responses.items():
            q_info = T["survey_questions"].get(q_key, {})
            labeled_responses[q_key] = {
                "question": q_info.get("question", q_key),
                "type": q_info.get("type", "unknown"),
                "response": response_value
            }

        # Create survey record
        survey = PostExpSurvey(
            survey_id=survey_id,
            user_id=user_id,
            session_id=session_id,
            dialogue_id=dialogue_id,
            conducted_at=datetime.now().isoformat(),
            responses=responses,
            labeled_responses=labeled_responses,
            metadata=metadata or {}
        )
        
        # Save survey
        survey.save(self.data_dir)
        
        self.logger.info(f"Survey {survey_id} completed for dialogue {dialogue_id}")
        return survey
    
    def get_survey(self, survey_id: str) -> Optional[PostExpSurvey]:
        """Retrieve survey by ID"""
        try:
            return PostExpSurvey.load(survey_id, self.data_dir)
        except FileNotFoundError:
            return None
    
    def get_session_surveys(self, session_id: str) -> List[PostExpSurvey]:
        """Get all surveys for a session"""
        surveys = []
        surveys_dir = self.data_dir / "surveys"
        
        if not surveys_dir.exists():
            return surveys
        
        for survey_file in surveys_dir.glob("*.json"):
            try:
                survey = PostExpSurvey.load(survey_file.stem, self.data_dir)
                if survey.session_id == session_id:
                    surveys.append(survey)
            except Exception as e:
                self.logger.error(f"Error loading survey {survey_file}: {e}")
        
        return sorted(surveys, key=lambda s: s.conducted_at)
    
    def get_survey_statistics(self, survey_id: str) -> Dict:
        """Get statistics for a specific survey"""
        survey = self.get_survey(survey_id)
        if not survey:
            return {"error": "Survey not found"}
        
        return {
            "survey_id": survey_id,
            "dialogue_id": survey.dialogue_id,
            "task_difficulty": survey.task_difficulty,
            "llm_helpfulness": survey.llm_helpfulness,
            "overall_satisfaction": survey.overall_satisfaction,
            "has_qualitative_feedback": bool(
                survey.what_worked_well or 
                survey.what_could_improve or 
                survey.additional_comments
            ),
            "conducted_at": survey.conducted_at
        }
    
    def aggregate_surveys(self, session_id: str) -> Dict:
        """Aggregate survey results for a session"""
        surveys = self.get_session_surveys(session_id)
        
        if not surveys:
            return {"error": "No surveys found for session"}
        
        # Calculate averages
        difficulties = [s.task_difficulty for s in surveys if s.task_difficulty is not None]
        helpfulness = [s.llm_helpfulness for s in surveys if s.llm_helpfulness is not None]
        satisfaction = [s.overall_satisfaction for s in surveys if s.overall_satisfaction is not None]
        
        return {
            "total_surveys": len(surveys),
            "avg_task_difficulty": sum(difficulties) / len(difficulties) if difficulties else None,
            "avg_llm_helpfulness": sum(helpfulness) / len(helpfulness) if helpfulness else None,
            "avg_overall_satisfaction": sum(satisfaction) / len(satisfaction) if satisfaction else None,
            "min_satisfaction": min(satisfaction) if satisfaction else None,
            "max_satisfaction": max(satisfaction) if satisfaction else None
        }
