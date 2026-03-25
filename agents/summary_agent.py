"""
Summary Report Agent
Generates comprehensive user reports with analytics and visualizations
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import uuid
import logging
import json

from .data_models import UserReport, UserSession, Big5Assessment, DialogueRecord, PostExpSurvey


class SummaryReportAgent:
    """
    Agent responsible for generating comprehensive summary reports
    with descriptive analytics, tables, and visualizations
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
    
    def generate_report(
        self,
        user_id: str,
        session_id: str,
        metadata: Dict = None
    ) -> UserReport:
        """Generate comprehensive report for a user session"""
        report_id = f"report_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Load session data
        session = self._load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Load assessment
        assessment = None
        if session.big5_assessment_id:
            assessment = self._load_assessment(session.big5_assessment_id)
        
        # Load dialogues
        dialogues = self._load_dialogues(session.dialogue_records)
        
        # Load task responses
        task_responses = self._load_task_responses(session.task_response_ids)
        
        # Load surveys
        surveys = self._load_surveys(session_id)
        
        # Calculate statistics
        big5_scores = {}
        gerlach_type = None
        if assessment:
            big5_scores = {
                "openness": assessment.openness,
                "conscientiousness": assessment.conscientiousness,
                "extraversion": assessment.extraversion,
                "agreeableness": assessment.agreeableness,
                "neuroticism": assessment.neuroticism
            }
            gerlach_type = assessment.gerlach_type
        
        total_messages = sum(d.total_messages for d in dialogues)
        total_time = sum(d.duration_seconds or 0 for d in dialogues)
        tasks_completed = [d.task_name for d in dialogues]
        llm_personalities = list(set(d.llm_personality for d in dialogues))
        
        # Calculate average satisfaction
        avg_satisfaction = None
        avg_difficulty = None
        if surveys:
            satisfactions = [s.overall_satisfaction for s in surveys if s.overall_satisfaction]
            difficulties = [s.task_difficulty for s in surveys if s.task_difficulty]
            avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else None
            avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else None
        
        # Create report
        report = UserReport(
            report_id=report_id,
            user_id=user_id,
            session_id=session_id,
            generated_at=datetime.now().isoformat(),
            big5_scores=big5_scores,
            gerlach_type=gerlach_type,
            total_dialogues=len(dialogues),
            total_messages=total_messages,
            total_time_seconds=total_time,
            tasks_completed=tasks_completed,
            llm_personalities_used=llm_personalities,
            average_satisfaction=avg_satisfaction,
            average_task_difficulty=avg_difficulty,
            assessment_id=session.big5_assessment_id,
            dialogue_ids=session.dialogue_records,
            survey_ids=[s.survey_id for s in surveys],
            metadata=metadata or {}
        )
        
        # Generate markdown report
        report.markdown_report = self._generate_markdown_report(
            report, session, assessment, dialogues, task_responses, surveys
        )
        
        # Generate HTML report
        report.html_report = self._generate_html_report(
            report, session, assessment, dialogues, task_responses, surveys
        )
        
        # Save report
        report.save(self.data_dir)
        
        self.logger.info(f"Generated report {report_id} for session {session_id}")
        return report
    
    def _load_session(self, session_id: str) -> Optional[UserSession]:
        """Load session data"""
        try:
            return UserSession.load(session_id, self.data_dir)
        except FileNotFoundError:
            return None
    
    def _load_assessment(self, assessment_id: str) -> Optional[Big5Assessment]:
        """Load assessment data"""
        try:
            return Big5Assessment.load(assessment_id, self.data_dir)
        except FileNotFoundError:
            return None
    
    def _load_dialogues(self, dialogue_ids: List[str]) -> List[DialogueRecord]:
        """Load dialogue records"""
        dialogues = []
        for dialogue_id in dialogue_ids:
            try:
                dialogue = DialogueRecord.load(dialogue_id, self.data_dir)
                dialogues.append(dialogue)
            except FileNotFoundError:
                self.logger.warning(f"Dialogue {dialogue_id} not found")
        return dialogues
    
    def _load_task_responses(self, task_response_ids: List[str]) -> List:
        """Load task response records"""
        from .task_response_models import NobleIndustriesResponse, PopcornBrainResponse
        
        task_responses = []
        for task_response_id in task_response_ids:
            try:
                # Try Noble Industries first
                if task_response_id.startswith("noble_"):
                    response = NobleIndustriesResponse.load(task_response_id, self.data_dir)
                    task_responses.append(response)
                # Try Popcorn Brain
                elif task_response_id.startswith("popcorn_"):
                    response = PopcornBrainResponse.load(task_response_id, self.data_dir)
                    task_responses.append(response)
            except FileNotFoundError:
                self.logger.warning(f"Task response {task_response_id} not found")
        return task_responses
    
    def _load_surveys(self, session_id: str) -> List[PostExpSurvey]:
        """Load all surveys for session"""
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
                self.logger.error(f"Error loading survey: {e}")
        
        return surveys
    
    def _generate_markdown_report(
        self,
        report: UserReport,
        session: UserSession,
        assessment: Optional[Big5Assessment],
        dialogues: List[DialogueRecord],
        task_responses: List,
        surveys: List[PostExpSurvey]
    ) -> str:
        """Generate markdown format report"""
        md = f"# User Research Report\n\n"
        md += f"**Report ID:** {report.report_id}\n"
        md += f"**User ID:** {report.user_id}\n"
        md += f"**Session ID:** {report.session_id}\n"
        md += f"**Generated:** {datetime.fromisoformat(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        md += "---\n\n"
        
        # Executive Summary
        md += "## Executive Summary\n\n"
        md += f"This report summarizes the research participation of user {report.user_id}. "
        md += f"The user completed {report.total_dialogues} task-solving dialogue(s) "
        md += f"with a total of {report.total_messages} messages exchanged over "
        md += f"{report.total_time_seconds / 60:.1f} minutes.\n\n"
        
        # Big5 Personality Profile
        if assessment:
            md += "## Big Five Personality Profile\n\n"
            md += f"**Assessment Date:** {datetime.fromisoformat(assessment.conducted_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            md += "### Trait Scores (0-100 scale)\n\n"
            md += "| Trait | Score | Interpretation |\n"
            md += "|-------|-------|----------------|\n"
            
            for trait, score in report.big5_scores.items():
                interpretation = "High" if score > 60 else "Low" if score < 40 else "Average"
                md += f"| {trait.title()} | {score:.1f} | {interpretation} |\n"
            
            gerlach_label = report.gerlach_type.replace('_', ' ').title() if report.gerlach_type else "Not classified"
            md += f"\n**Gerlach Personality Type:** {gerlach_label}\n"
            conf = assessment.gerlach_confidence
            md += f"**Classification Confidence:** {f'{conf:.1f}%' if isinstance(conf, (int, float)) else 'N/A'}\n\n"
            
            # Personality visualization (text-based)
            md += "### Personality Profile Visualization\n\n"
            md += "```\n"
            for trait, score in report.big5_scores.items():
                bar_length = int(score / 5)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                md += f"{trait[:15]:15} [{bar}] {score:.1f}\n"
            md += "```\n\n"
        
        # Task-Solving Activity
        md += "## Task-Solving Activity\n\n"
        md += f"**Total Dialogues:** {report.total_dialogues}\n"
        md += f"**Total Messages:** {report.total_messages}\n"
        md += f"**Total Time:** {report.total_time_seconds / 60:.1f} minutes\n\n"
        
        if dialogues:
            md += "### Dialogue Summary\n\n"
            md += "| # | Task | LLM Personality | Messages | Duration (min) |\n"
            md += "|---|------|-----------------|----------|----------------|\n"
            
            for i, dialogue in enumerate(dialogues, 1):
                duration = (dialogue.duration_seconds or 0) / 60
                md += f"| {i} | {dialogue.task_name} | {dialogue.llm_personality.replace('_', ' ').title()} | "
                md += f"{dialogue.total_messages} | {duration:.1f} |\n"
            
            md += "\n"
        
        # LLM Personalities Used
        if report.llm_personalities_used:
            md += "### LLM Personalities Engaged\n\n"
            for personality in report.llm_personalities_used:
                md += f"- {personality.replace('_', ' ').title()}\n"
            md += "\n"
        
        # Task-Specific Results
        if task_responses:
            md += "## Task-Specific Results\n\n"
            
            for task_response in task_responses:
                # Check if Noble Industries
                if hasattr(task_response, 'rankings'):
                    md += "### Noble Industries - Candidate Rankings\n\n"
                    md += "| Rank | Candidate | Rationale |\n"
                    md += "|------|-----------|----------|\n"
                    
                    sorted_rankings = sorted(task_response.rankings, key=lambda r: r.rank)
                    for ranking in sorted_rankings:
                        rationale_short = ranking.rationale[:100] + "..." if len(ranking.rationale) > 100 else ranking.rationale
                        md += f"| {ranking.rank} | {ranking.candidate_name} | {rationale_short} |\n"
                    md += "\n"
                
                # Check if Popcorn Brain
                elif hasattr(task_response, 'originality_rating'):
                    md += "### Popcorn Brain — Creative Performance\n\n"

                    # Summary metrics table
                    md += "#### Automated Metrics vs Self-Assessment\n\n"
                    md += "| Dimension | Definition | Computed Count | Self-Rating (1–7) |\n"
                    md += "|-----------|------------|:--------------:|:-----------------:|\n"
                    if task_response.originality:
                        md += (f"| **Originality** | Unique ideas generated by participant "
                               f"| {task_response.originality.computed_count} "
                               f"| {task_response.originality_rating} |\n")
                    if task_response.flexibility:
                        md += (f"| **Flexibility** | Alternative approaches proposed "
                               f"| {task_response.flexibility.computed_count} "
                               f"| {task_response.flexibility_rating} |\n")
                    if task_response.elaboration:
                        md += (f"| **Elaboration** | Instances of adding detail or synthesis "
                               f"| {task_response.elaboration.computed_count} "
                               f"| {task_response.elaboration_rating} |\n")
                    if task_response.fluency:
                        md += (f"| **Fluency** | Total idea-bearing statements "
                               f"| {task_response.fluency.computed_count} "
                               f"| {task_response.fluency_rating} |\n")
                    md += f"\n**Ideas per Minute:** {task_response.ideas_per_minute:.2f}\n\n"

                    # Per-dimension evidence from dialogue
                    dims = [
                        ("Originality", task_response.originality,
                         "Sentences containing idea proposals (could, what if, perhaps, etc.)"),
                        ("Flexibility", task_response.flexibility,
                         "Sentences signalling alternative approaches (alternatively, instead, on the other hand, etc.)"),
                        ("Elaboration", task_response.elaboration,
                         "Sentences adding detail or synthesis (specifically, for example, building on, step by step, etc.)"),
                        ("Fluency", task_response.fluency,
                         "Idea-bearing sentences used to compute total count"),
                    ]
                    for dim_name, dim_obj, definition in dims:
                        if dim_obj and dim_obj.examples:
                            md += f"#### {dim_name} — Dialogue Evidence\n\n"
                            md += f"*{definition}*\n\n"
                            for ex in dim_obj.examples:
                                md += f"> {ex.strip()}\n\n"
                    md += "\n"
        
        # Survey Results
        if surveys:
            md += "## Post-Experiment Survey Results\n\n"
            md += f"**Surveys Completed:** {len(surveys)}\n\n"
            
            if report.average_satisfaction:
                md += f"**Average Overall Satisfaction:** {report.average_satisfaction:.2f} / 7\n"
            if report.average_task_difficulty:
                md += f"**Average Task Difficulty:** {report.average_task_difficulty:.2f} / 7\n"
            
            md += "\n### Individual Survey Responses\n\n"
            
            for i, survey in enumerate(surveys, 1):
                md += f"#### Survey {i}\n\n"
                md += f"**Dialogue:** {survey.dialogue_id}\n"
                
                if survey.task_difficulty:
                    md += f"- **Task Difficulty:** {survey.task_difficulty} / 7\n"
                if survey.llm_helpfulness:
                    md += f"- **LLM Helpfulness:** {survey.llm_helpfulness} / 7\n"
                if survey.overall_satisfaction:
                    md += f"- **Overall Satisfaction:** {survey.overall_satisfaction} / 7\n"
                
                if survey.what_worked_well:
                    md += f"\n**What Worked Well:**\n> {survey.what_worked_well}\n"
                
                if survey.what_could_improve:
                    md += f"\n**What Could Improve:**\n> {survey.what_could_improve}\n"
                
                if survey.additional_comments:
                    md += f"\n**Additional Comments:**\n> {survey.additional_comments}\n"
                
                md += "\n"
        
        # Session Timeline
        md += "## Session Timeline\n\n"
        md += f"**Started:** {datetime.fromisoformat(session.started_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
        if session.ended_at:
            md += f"**Ended:** {datetime.fromisoformat(session.ended_at).strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Randomized assignment (stored in session metadata)
        if session.metadata.get("assigned_task"):
            md += f"\n**Randomly Assigned Task:** {session.metadata['assigned_task']}\n"
            md += f"**Randomly Assigned Personality:** {session.metadata['assigned_personality'].replace('_', ' ').title()}\n"

        md += f"\n**Completed Stages:**\n"
        for stage in session.completed_stages:
            md += f"- {stage.replace('_', ' ').title()}\n"
        
        md += "\n---\n\n"
        md += f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return md
    
    def _generate_html_report(
        self,
        report: UserReport,
        session: UserSession,
        assessment: Optional[Big5Assessment],
        dialogues: List[DialogueRecord],
        task_responses: List,
        surveys: List[PostExpSurvey]
    ) -> str:
        """Generate HTML format report with charts"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>User Research Report - {report.user_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{ margin-top: 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        .trait-bar {{
            background-color: #e0e0e0;
            height: 30px;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .trait-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-weight: bold;
        }}
        .metric {{
            display: inline-block;
            background: #f0f0f0;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .quote {{
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>User Research Report</h1>
        <p><strong>User ID:</strong> {report.user_id}</p>
        <p><strong>Report ID:</strong> {report.report_id}</p>
        <p><strong>Generated:</strong> {datetime.fromisoformat(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        # Executive Summary
        html += f"""
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="metric-value">{report.total_dialogues}</div>
            <div class="metric-label">Dialogues</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report.total_messages}</div>
            <div class="metric-label">Messages</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report.total_time_seconds / 60:.1f}</div>
            <div class="metric-label">Minutes</div>
        </div>
"""
        
        if report.average_satisfaction:
            html += f"""
        <div class="metric">
            <div class="metric-value">{report.average_satisfaction:.1f}/7</div>
            <div class="metric-label">Avg Satisfaction</div>
        </div>
"""
        
        html += "    </div>\n"
        
        # Big5 Profile
        if assessment:
            html += f"""
    <div class="section">
        <h2>Big Five Personality Profile</h2>
        <p><strong>Gerlach Type:</strong> {report.gerlach_type.replace('_', ' ').title() if report.gerlach_type else 'Not classified'}</p>
"""
            
            for trait, score in report.big5_scores.items():
                html += f"""
        <div>
            <strong>{trait.title()}:</strong> {score:.1f}
            <div class="trait-bar">
                <div class="trait-fill" style="width: {score}%">{score:.1f}</div>
            </div>
        </div>
"""
            
            html += "    </div>\n"
        
        # Dialogues
        if dialogues:
            html += """
    <div class="section">
        <h2>Task-Solving Dialogues</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Task</th>
                <th>LLM Personality</th>
                <th>Messages</th>
                <th>Duration (min)</th>
            </tr>
"""
            
            for i, dialogue in enumerate(dialogues, 1):
                duration = (dialogue.duration_seconds or 0) / 60
                html += f"""
            <tr>
                <td>{i}</td>
                <td>{dialogue.task_name}</td>
                <td>{dialogue.llm_personality.replace('_', ' ').title()}</td>
                <td>{dialogue.total_messages}</td>
                <td>{duration:.1f}</td>
            </tr>
"""
            
            html += """
        </table>
    </div>
"""
        
        # Task-Specific Results
        if task_responses:
            html += """
    <div class="section">
        <h2>Task-Specific Results</h2>
"""
            for task_response in task_responses:
                if hasattr(task_response, 'rankings'):
                    html += "<h3>Noble Industries — Candidate Rankings</h3>\n"
                    html += """
        <table>
            <tr><th>Rank</th><th>Candidate</th><th>Rationale</th></tr>
"""
                    for ranking in sorted(task_response.rankings, key=lambda r: r.rank):
                        rationale = ranking.rationale.replace('<', '&lt;').replace('>', '&gt;')
                        html += f"            <tr><td>{ranking.rank}</td><td>{ranking.candidate_name}</td><td>{rationale}</td></tr>\n"
                    html += "        </table>\n"

                elif hasattr(task_response, 'originality_rating'):
                    html += "<h3>Popcorn Brain — Creative Performance</h3>\n"
                    html += """
        <table>
            <tr><th>Dimension</th><th>Definition</th><th>Computed Count</th><th>Self-Rating (1–7)</th></tr>
"""
                    dims = [
                        ("Originality", "Unique ideas generated",
                         getattr(task_response.originality, 'computed_count', 0),
                         task_response.originality_rating),
                        ("Flexibility", "Alternative approaches proposed",
                         getattr(task_response.flexibility, 'computed_count', 0),
                         task_response.flexibility_rating),
                        ("Elaboration", "Detail/synthesis instances",
                         getattr(task_response.elaboration, 'computed_count', 0),
                         task_response.elaboration_rating),
                        ("Fluency", "Total idea-bearing statements",
                         getattr(task_response.fluency, 'computed_count', 0),
                         task_response.fluency_rating),
                    ]
                    for name, defn, count, rating in dims:
                        html += f"            <tr><td><strong>{name}</strong></td><td>{defn}</td><td>{count}</td><td>{rating}</td></tr>\n"
                    html += "        </table>\n"
                    html += f"        <p><strong>Ideas per Minute:</strong> {task_response.ideas_per_minute:.2f}</p>\n"

                    # Evidence per dimension
                    dim_objs = [
                        ("Originality", task_response.originality,
                         "Idea-proposal sentences (could, what if, perhaps, etc.)"),
                        ("Flexibility", task_response.flexibility,
                         "Alternative-approach sentences (alternatively, instead, etc.)"),
                        ("Elaboration", task_response.elaboration,
                         "Detail/synthesis sentences (specifically, for example, build on, etc.)"),
                        ("Fluency", task_response.fluency,
                         "Idea-bearing sentences counted for fluency"),
                    ]
                    for dim_name, dim_obj, definition in dim_objs:
                        if dim_obj and dim_obj.examples:
                            html += f"        <h4>{dim_name} — Dialogue Evidence</h4>\n"
                            html += f"        <p><em>{definition}</em></p>\n"
                            for ex in dim_obj.examples:
                                html += f'        <div class="quote">{ex.strip()}</div>\n'

            html += "    </div>\n"

        # Surveys
        if surveys:
            html += """
    <div class="section">
        <h2>Post-Experiment Survey Feedback</h2>
"""
            
            for i, survey in enumerate(surveys, 1):
                html += f"<h3>Survey {i}</h3>\n"
                
                if survey.what_worked_well:
                    html += f'<div class="quote"><strong>What Worked Well:</strong><br>{survey.what_worked_well}</div>\n'
                
                if survey.what_could_improve:
                    html += f'<div class="quote"><strong>What Could Improve:</strong><br>{survey.what_could_improve}</div>\n'
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        
        return html
    
    def get_report(self, report_id: str) -> Optional[UserReport]:
        """Retrieve report by ID"""
        try:
            return UserReport.load(report_id, self.data_dir)
        except FileNotFoundError:
            return None
