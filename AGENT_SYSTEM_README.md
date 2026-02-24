# Multi-Agent Research System

## Overview

This is a comprehensive multi-agent system for conducting personality research with the Gerlach (2018) personality types. The system orchestrates a complete research workflow from participant registration through final report generation.

## System Architecture

### 5 Core Agents

1. **Supervisor Agent** (`supervisor_agent.py`)
   - Coordinates the entire research workflow
   - Manages session state and stage transitions
   - Ensures proper workflow progression
   - Tracks system-wide statistics

2. **Big5 Assessment Agent** (`big5_assessment_agent.py`)
   - Conducts IPIP-50 Big Five personality assessment
   - Calculates trait scores (0-100 scale)
   - Classifies participants into Gerlach personality types
   - Archives assessment results

3. **Dialogue Capture Agent** (`dialogue_capture_agent.py`)
   - Records all user-LLM interactions in real-time
   - Captures timestamps, message content, and metadata
   - Calculates dialogue statistics
   - Exports transcripts in multiple formats

4. **Post-Experiment Survey Agent** (`survey_agent.py`)
   - Conducts post-task surveys
   - Collects quantitative ratings (1-7 scale)
   - Gathers qualitative feedback
   - Aggregates survey results

5. **Summary Report Agent** (`summary_agent.py`)
   - Generates comprehensive user reports
   - Creates visualizations and analytics
   - Produces both Markdown and HTML reports
   - Includes personality profiles, dialogue statistics, and survey insights

## Research Workflow

```
1. Registration
   ↓
2. Big5 Assessment (IPIP-50)
   ↓
3. Task Selection (choose task + LLM personality)
   ↓
4. Task Dialogue (user ↔ LLM collaboration)
   ↓
5. Post-Experiment Survey
   ↓
6. Report Generation & Session Complete
```

Participants can complete multiple task dialogues before finishing.

## Data Storage

All data is stored in `research_data/` directory:

```
research_data/
├── sessions/          # User session records
├── assessments/       # Big5 assessment results
├── dialogues/         # Complete dialogue transcripts
├── surveys/           # Post-experiment survey responses
└── reports/           # Generated reports (JSON, MD, HTML)
```

## Getting Started

### Prerequisites

```bash
pip install streamlit anthropic PyPDF2
```

### Environment Setup

Set your Anthropic API key:

```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows Command Prompt
set ANTHROPIC_API_KEY=your-api-key-here

# Mac/Linux
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Running the Application

**Option 1: Use the launcher script**
```bash
start_agent_research.bat
```

**Option 2: Run directly**
```bash
streamlit run agent_research_app.py --server.port 8505
```

The application will be available at: `http://localhost:8505`

## Features

### For Participants

- **Guided Workflow**: Step-by-step progression through research stages
- **Personality Assessment**: Complete IPIP-50 Big Five inventory
- **Task Collaboration**: Work with AI personalities on real tasks
- **Feedback Collection**: Provide structured and open-ended feedback
- **Comprehensive Reports**: Receive detailed reports with visualizations

### For Researchers

- **Automated Data Collection**: All interactions automatically captured
- **Structured Data**: Consistent JSON format for all data types
- **Real-time Monitoring**: Track sessions and statistics
- **Export Capabilities**: Download reports in multiple formats
- **Analytics**: Built-in descriptive statistics and visualizations

## Data Models

### UserSession
- Tracks overall participant session
- Manages workflow stage progression
- Links to all related data (assessment, dialogues, surveys)

### Big5Assessment
- 50-item IPIP inventory responses
- Calculated Big5 trait scores
- Gerlach personality type classification

### DialogueRecord
- Complete message history
- Timestamps for each message
- Dialogue statistics (duration, message counts)

### PostExpSurvey
- Quantitative ratings (task difficulty, satisfaction, etc.)
- Qualitative feedback (what worked, improvements)
- Linked to specific dialogue

### UserReport
- Comprehensive summary of all activities
- Big5 profile visualization
- Dialogue statistics
- Survey insights
- Markdown and HTML formats

## Agent Communication

Agents communicate through the Supervisor Agent, which maintains the workflow state and coordinates transitions:

```
User Interface (Streamlit)
         ↓
  Supervisor Agent
    ↙    ↓    ↘
Assessment  Dialogue  Survey
  Agent     Agent     Agent
         ↓
   Summary Agent
```

## API Reference

### Supervisor Agent

```python
supervisor = SupervisorAgent(data_dir)

# Create session
session = supervisor.create_user_session(user_id, metadata)

# Advance workflow
supervisor.advance_stage(session_id, WorkflowStage.BIG5_ASSESSMENT)

# Get status
status = supervisor.get_workflow_status(session_id)
```

### Big5 Assessment Agent

```python
assessment_agent = Big5AssessmentAgent(data_dir)

# Get assessment items
items = assessment_agent.get_assessment_items()

# Conduct assessment
assessment = assessment_agent.conduct_assessment(
    user_id, session_id, responses
)
```

### Dialogue Capture Agent

```python
dialogue_agent = DialogueCaptureAgent(data_dir)

# Start dialogue
dialogue = dialogue_agent.start_dialogue(
    user_id, session_id, task_name, llm_personality
)

# Record message
dialogue_agent.record_message(dialogue_id, role, content)

# End dialogue
dialogue_agent.end_dialogue(dialogue_id)
```

### Survey Agent

```python
survey_agent = PostExpSurveyAgent(data_dir)

# Get questions
questions = survey_agent.get_survey_questions()

# Conduct survey
survey = survey_agent.conduct_survey(
    user_id, session_id, dialogue_id, responses
)
```

### Summary Agent

```python
summary_agent = SummaryReportAgent(data_dir)

# Generate report
report = summary_agent.generate_report(user_id, session_id)
```

## Customization

### Adding Custom Survey Questions

Edit `agents/survey_agent.py` and modify `SURVEY_QUESTIONS`:

```python
SURVEY_QUESTIONS = {
    "your_question_id": {
        "question": "Your question text?",
        "type": "scale",  # or "text"
        "scale": (1, 7),
        "labels": {1: "Low", 7: "High"}
    }
}
```

### Adding Custom Tasks

Place task files in the `Task/` folder:
- Supported formats: `.pdf`, `.txt`, `.md`
- Files are automatically detected and listed

### Modifying Workflow Stages

Edit `agents/data_models.py` to add/modify `WorkflowStage` enum:

```python
class WorkflowStage(Enum):
    REGISTRATION = "registration"
    YOUR_STAGE = "your_stage"
    # ...
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Set the environment variable before starting the app
- Restart your terminal after setting the variable

### "Session not found"
- Check that `research_data/sessions/` directory exists
- Verify session ID is correct

### "LLM Manager initialization failed"
- Ensure `gerlach_personality_llms.py` is in the same directory
- Check that the API key is valid

## Data Privacy

- All participant data is stored locally
- Session IDs are generated with UUIDs for anonymization
- No data is sent to external servers except LLM API calls
- Researchers should follow IRB protocols for data handling

## Citation

If you use this system in your research, please cite:

```
Gerlach, M., Farb, B., Revelle, W., & Nunes Amaral, L. A. (2018).
A robust data-driven approach identifies four personality types across four large data sets.
Nature Human Behaviour, 2(10), 735-742.
```

## License

This research platform is provided for academic and research purposes.

## Support

For issues or questions, please check the documentation or contact the research team.
