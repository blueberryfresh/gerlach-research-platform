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


class PostExpSurveyAgent:
    """
    Agent responsible for conducting post-experiment surveys
    after users complete task-solving dialogues
    """
    
    # LLM-Human Collaboration Post Session Questionnaire (37 questions)
    # Likert scale questions (1-7): 1=Strongly Disagree, 7=Strongly Agree
    SURVEY_QUESTIONS = {
        "q1": {
            "question": "I am confident that our work (output) is done correctly.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q2": {
            "question": "I believe that our work is readable and understandable for others.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q3": {
            "question": "I believe that our output has effectively answered the given problem.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q4": {
            "question": "I enjoyed the LLM-Human collaboration more than doing it alone.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q5": {
            "question": "In LLM-Human collaboration, LLM and I disagreed frequently in reaching a solution.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q6": {
            "question": "In LLM-Human collaboration, I believe that I had an easier time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q7": {
            "question": "In LLM-Human collaboration I believe that we had much longer time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q8": {
            "question": "In LLM-Human collaboration, I did not like LLM's suggestion or view, but I compromised to do (or follow) LLM's way.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q9": {
            "question": "In LLM-Human collaboration, the feeling of trusting LLM grew stronger as the session went on.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q10": {
            "question": "LLM showed things that I did not know about.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q11": {
            "question": "LLM showed compassion towards me.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q12": {
            "question": "LLM showed no emotion and only dealt facts.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q13": {
            "question": "In LLM-Human collaboration, I really enjoyed my partner's partnership (willing to work as a team, open mind, etc).",
            "type": "likert",
            "scale": (1, 7)
        },
        "q14": {
            "question": "In LLM-Human collaboration, my partner insisted on doing things his way and/or did not collaborate.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q15": {
            "question": "In LLM-Human collaboration, I was NOT able to fully exercise my knowledgeable skill.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q16": {
            "question": "In LLM-Human collaboration, I believe that I'm a compatible partner to LLM.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q17": {
            "question": "In LLM-Human collaboration, it was my politeness and etiquette that got through the LLM-Human collaboration sessions, NOT my true self (personality).",
            "type": "likert",
            "scale": (1, 7)
        },
        "q18": {
            "question": "In LLM-Human collaboration, I believe that I have a compatible personality to LLM.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q19": {
            "question": "In LLM-Human collaboration, I did NOT reveal my true self, personality during the whole session.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q20": {
            "question": "In LLM-Human collaboration, LLM was thoughtful and forgiving with my mistakes.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q21": {
            "question": "In LLM-Human collaboration, there were times when I was withdrawn (or maybe upset) because of the disagreements from the partner.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q22": {
            "question": "I think LLM-Human collaboration is a form of cheating as LLM-Human collaboration takes away from one to truly learn on his or her own.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q23": {
            "question": "I don't think I can achieve a higher productivity next time if I'm paired with LLM again.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q24": {
            "question": "In LLM-Human collaboration, LLM described his or her point very well and I was able to fully understand.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q25": {
            "question": "In LLM-Human collaboration, LLM did not express nor communicated much (too quiet) which made LLM-Human collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q26": {
            "question": "In LLM-Human collaboration, LLM's message delivery was unclear which made LLM-Human collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q27": {
            "question": "In LLM-Human collaboration, LLM's active communication to me allowed me to be more active in expressing my views as well.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q28": {
            "question": "In LLM-Human collaboration, LLM's voice tone was loud and clear which helped our communication.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q29": {
            "question": "In LLM-Human collaboration, the gender of LLM's voice did not influence my LLM-Human collaboration experience at all.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q30": {
            "question": "In LLM-Human collaboration, the fact that my partner was male voice (or female voice), it allowed me to focus more on the problems.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q31": {
            "question": "In LLM-Human collaboration, I think the partner's gender can be an issue.",
            "type": "likert",
            "scale": (1, 7)
        },
        "q32": {
            "question": "Briefly describe any conflicts or negative impacts from LLM that you have experienced during the collaboration which you think it influenced or caused the collaboration session and its productivity.",
            "type": "text",
            "placeholder": "Describe any conflicts or negative impacts..."
        },
        "q33": {
            "question": "Describe any positive impacts from LLM that you have experienced during the collaboration which you think it influenced or caused the collaboration productivity.",
            "type": "text",
            "placeholder": "Describe positive impacts..."
        },
        "q34": {
            "question": "Discuss the compatibility (personality, communication or others) of you and LLM. If good, why? If not, why not? Do you think you can achieve a high productivity with LLM again?",
            "type": "text",
            "placeholder": "Discuss compatibility..."
        },
        "q35": {
            "question": "Besides LLM's ability to contribute to the task, how did the LLM's personality played a role in your and LLM's collaboration? Was the personality compatible or NOT? Describe.",
            "type": "text",
            "placeholder": "Describe LLM's personality role..."
        },
        "q36": {
            "question": "Besides LLM's ability to contribute to the task, how did the LLM's communication skill played a role in your and LLM's collaboration? The level of communication skill that LLM exhibited, did that bring on a positive (or negative) feeling and impact to your collaboration with LLM? Describe.",
            "type": "text",
            "placeholder": "Describe LLM's communication skill impact..."
        },
        "q37": {
            "question": "Besides LLM's ability to contribute to the task, how did the voice of gender played a role in your and LLM's collaboration? LLM's voice being male or female, did it influence your collaboration with your partner? If the voice was opposite sex, would it made any difference to the collaboration and its output?",
            "type": "text",
            "placeholder": "Describe gender/voice impact..."
        }
    }
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
    
    def get_survey_questions(self) -> Dict:
        """Get all survey questions"""
        return self.SURVEY_QUESTIONS
    
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
        
        # Extract specific ratings
        task_difficulty = responses.get("task_difficulty")
        llm_helpfulness = responses.get("llm_helpfulness")
        overall_satisfaction = responses.get("overall_satisfaction")
        
        # Extract open-ended responses
        what_worked_well = responses.get("what_worked_well")
        what_could_improve = responses.get("what_could_improve")
        additional_comments = responses.get("additional_comments")
        
        # Create survey record
        survey = PostExpSurvey(
            survey_id=survey_id,
            user_id=user_id,
            session_id=session_id,
            dialogue_id=dialogue_id,
            conducted_at=datetime.now().isoformat(),
            responses=responses,
            task_difficulty=task_difficulty,
            llm_helpfulness=llm_helpfulness,
            overall_satisfaction=overall_satisfaction,
            what_worked_well=what_worked_well,
            what_could_improve=what_could_improve,
            additional_comments=additional_comments,
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
