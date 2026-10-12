# Gerlach Personality Research Platform - Technical Documentation

**For Research Collaborators and Co-Investigators**

**Version 1.0 | February 2026**

---

## Executive Summary

This document provides comprehensive technical information about the Gerlach Personality Research Platform for research collaborators. It covers system architecture, data collection methods, storage mechanisms, analysis capabilities, and operational procedures.

**Target Audience**: Co-investigators, research assistants, data analysts, IT administrators

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Collection](#data-collection)
4. [Data Storage](#data-storage)
5. [Data Analysis](#data-analysis)
6. [Deployment & Access](#deployment--access)
7. [Operational Procedures](#operational-procedures)
8. [Security & Privacy](#security--privacy)
9. [Troubleshooting](#troubleshooting)
10. [API & Integration](#api--integration)

---

## System Overview

### Purpose

The platform enables research on human-AI collaboration across different personality types using:
- Big Five personality assessment
- Gerlach (2018) personality classification
- Task-based collaboration with AI personalities
- Comprehensive data capture and analysis

### Key Features

**Participant-Facing:**
- 50-question Big Five personality assessment
- 2 research tasks (Noble Industries, Popcorn Brain)
- 4 AI personalities (Average, Role Model, Self-Centred, Reserved)
- Real-time dialogue with Claude AI
- Task-specific data capture
- 37-question post-experiment survey
- Automated report generation

**Researcher-Facing:**
- Multi-agent system architecture
- Automated data collection and storage
- JSON-based data persistence
- Comprehensive analytics
- Export capabilities (Markdown, HTML, JSON)

### Technology Stack

**Frontend:**
- Streamlit 1.54.0 (Python web framework)
- HTML/CSS for custom components

**Backend:**
- Python 3.9+
- Anthropic Claude API (claude-opus-4-20250514)
- Multi-agent architecture

**Hosting:**
- Streamlit Cloud (free tier)
- GitHub for version control

**Data Storage:**
- File-based JSON storage
- Hierarchical directory structure

---

## Architecture

### Multi-Agent System

The platform uses a **multi-agent architecture** with specialized agents for different tasks:

#### 1. Supervisor Agent
**File**: `agents/supervisor_agent.py`

**Responsibilities:**
- Coordinates overall workflow
- Manages session state transitions
- Tracks system statistics
- Validates workflow progression

**Key Methods:**
```python
create_session(user_id) -> UserSession
advance_stage(session_id, new_stage) -> bool
get_session(session_id) -> UserSession
get_system_stats() -> dict
```

#### 2. Big5 Assessment Agent
**File**: `agents/big5_assessment_agent.py`

**Responsibilities:**
- Conducts 50-question personality assessment
- Calculates Big Five trait scores
- Classifies Gerlach personality type
- Archives assessment results

**Key Methods:**
```python
conduct_assessment(session_id, responses) -> Big5Assessment
calculate_scores(responses) -> dict
classify_gerlach_type(scores) -> str
```

**Scoring Algorithm:**
- Openness: Questions 1-10
- Conscientiousness: Questions 11-20
- Extraversion: Questions 21-30
- Agreeableness: Questions 31-40
- Neuroticism: Questions 41-50

**Gerlach Classification:**
Based on trait combinations:
- **Average**: Balanced across all traits
- **Role Model**: High extraversion, agreeableness, conscientiousness; low neuroticism
- **Self-Centred**: Low agreeableness, high extraversion
- **Reserved**: Low extraversion, high neuroticism

#### 3. Dialogue Capture Agent
**File**: `agents/dialogue_capture_agent.py`

**Responsibilities:**
- Records user-AI conversations
- Manages dialogue sessions
- Tracks message timestamps
- Calculates dialogue duration
- Exports transcripts

**Key Methods:**
```python
start_dialogue(session_id, task_name, llm_personality) -> str
record_message(dialogue_id, role, content) -> None
end_dialogue(dialogue_id) -> DialogueRecord
export_transcript(dialogue_id, format) -> str
```

**Data Captured Per Message:**
- Message ID
- Timestamp (ISO 8601)
- Role (user/assistant)
- Content (full text)
- Message number in sequence

#### 4. Task Response Agent
**File**: `agents/task_response_agent.py`

**Responsibilities:**
- Captures task-specific responses
- Computes automated metrics (Popcorn Brain)
- Validates response data
- Archives task results

**Key Methods:**
```python
capture_noble_rankings(session_id, dialogue_id, rankings) -> str
capture_popcorn_assessment(session_id, dialogue_id, ratings, dialogue) -> str
compute_creative_metrics(dialogue) -> dict
```

**Automated Creativity Metrics:**

**Originality** (Unique Ideas):
- Markers: "could", "should", "what if", "maybe", "perhaps", "idea:", "suggestion:"
- Method: Extract sentences with markers, deduplicate by content
- Output: Count + examples

**Flexibility** (Alternatives):
- Markers: "alternatively", "another way", "instead", "or we could", "different approach"
- Method: Detect alternative markers in user messages
- Output: Count + context examples

**Elaboration** (Detail & Synthesis):
- Markers: "specifically", "in detail", "for example", "combining", "build on", "expand on"
- Method: Identify detail and synthesis markers
- Output: Count + examples

**Fluency** (Quantity):
- Markers: Same as originality + "let's", "we can", "we should"
- Method: Count all idea-related sentences
- Output: Total ideas + ideas per minute

#### 5. Survey Agent
**File**: `agents/survey_agent.py`

**Responsibilities:**
- Conducts 37-question post-experiment survey
- Captures Likert scale responses (1-7)
- Records open-ended text responses
- Aggregates survey data

**Key Methods:**
```python
conduct_survey(session_id, dialogue_id, responses) -> str
get_survey_questions() -> list
aggregate_survey_data() -> dict
```

**Survey Structure:**
- Questions 1-31: Likert scale (1-7)
- Questions 32-37: Open-ended text

#### 6. Summary Report Agent
**File**: `agents/summary_agent.py`

**Responsibilities:**
- Generates comprehensive user reports
- Creates visualizations
- Exports in multiple formats (Markdown, HTML)
- Calculates aggregate statistics

**Key Methods:**
```python
generate_report(user_id, session_id) -> UserReport
export_markdown(report_id) -> str
export_html(report_id) -> str
```

**Report Sections:**
1. Executive Summary
2. Big Five Personality Profile
3. Task-Solving Activity
4. Task-Specific Results
5. Post-Experiment Survey Results
6. Session Timeline

### Data Models

**File**: `agents/data_models.py`

**Core Models:**

```python
@dataclass
class UserSession:
    session_id: str
    user_id: str
    started_at: str
    ended_at: Optional[str]
    current_stage: WorkflowStage
    completed_stages: List[str]
    big5_assessment_id: Optional[str]
    dialogue_records: List[str]
    task_response_ids: List[str]
    survey_ids: List[str]
    report_id: Optional[str]

@dataclass
class Big5Assessment:
    assessment_id: str
    session_id: str
    conducted_at: str
    responses: Dict[int, int]
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    gerlach_type: str
    gerlach_confidence: float

@dataclass
class DialogueRecord:
    dialogue_id: str
    session_id: str
    task_name: str
    llm_personality: str
    started_at: str
    ended_at: Optional[str]
    messages: List[Message]
    total_messages: int
    duration_seconds: Optional[int]

@dataclass
class NobleIndustriesResponse:
    response_id: str
    session_id: str
    dialogue_id: str
    submitted_at: str
    rankings: List[CandidateRanking]
    total_candidates: int

@dataclass
class PopcornBrainResponse:
    response_id: str
    session_id: str
    dialogue_id: str
    submitted_at: str
    originality_rating: int
    flexibility_rating: int
    elaboration_rating: int
    fluency_rating: int
    originality: CreativeDimension
    flexibility: CreativeDimension
    elaboration: CreativeDimension
    fluency: CreativeDimension
    unique_ideas: int
    alternative_approaches: int
    detail_instances: int
    total_ideas: int
    ideas_per_minute: float

@dataclass
class PostExpSurvey:
    survey_id: str
    session_id: str
    dialogue_id: str
    submitted_at: str
    responses: Dict[int, Union[int, str]]
```

### Workflow Stages

```python
class WorkflowStage(Enum):
    REGISTRATION = "registration"
    BIG5_ASSESSMENT = "big5_assessment"
    TASK_SELECTION = "task_selection"
    TASK_DIALOGUE = "task_dialogue"
    TASK_RESPONSE = "task_response"
    POST_SURVEY = "post_survey"
    COMPLETED = "completed"
```

**Workflow Progression:**
```
REGISTRATION → BIG5_ASSESSMENT → TASK_SELECTION → 
TASK_DIALOGUE → TASK_RESPONSE → POST_SURVEY → COMPLETED
```

---

## Data Collection

### Collection Methods

#### 1. Personality Assessment
**Method**: Structured questionnaire  
**Format**: 50 questions, 5-point Likert scale  
**Duration**: 10-15 minutes  
**Data Points**: 50 responses + 5 trait scores + Gerlach type

#### 2. Task Dialogue
**Method**: Real-time chat interface  
**Format**: Text-based conversation  
**Duration**: 20-30 minutes  
**Data Points**: 
- All messages (user + AI)
- Timestamps
- Message sequence
- Total duration

#### 3. Task-Specific Responses

**Noble Industries:**
- 5 candidate rankings (1-5 scale)
- Rationale text for each candidate
- Ranking changes tracked

**Popcorn Brain:**
- 4 self-assessment ratings (1-7 scale)
- Automated metrics from dialogue:
  - Unique ideas count
  - Alternative approaches count
  - Detail instances count
  - Total ideas count
  - Ideas per minute

#### 4. Post-Experiment Survey
**Method**: Mixed-format questionnaire  
**Format**: 31 Likert scale + 6 open-ended  
**Duration**: 10-15 minutes  
**Data Points**: 37 responses

### Data Quality Measures

**Validation:**
- Required field checks
- Format validation (email, IDs)
- Range validation (1-5, 1-7 scales)
- Uniqueness checks (rankings)

**Completeness:**
- All questions must be answered
- Minimum dialogue length (suggested: 10 messages)
- Required rationale text

**Consistency:**
- Timestamp verification
- Sequence validation
- Cross-reference checks

---

## Data Storage

### Storage Architecture

**Type**: File-based JSON storage  
**Location**: `research_data/` directory  
**Format**: JSON with hierarchical structure

### Directory Structure

```
research_data/
├── sessions/
│   └── session_{user_id}_{uuid}.json
├── assessments/
│   └── assessment_{user_id}_{uuid}.json
├── dialogues/
│   └── dialogue_{user_id}_{uuid}.json
├── task_responses/
│   ├── noble/
│   │   └── noble_{user_id}_{uuid}.json
│   └── popcorn/
│       └── popcorn_{user_id}_{uuid}.json
├── surveys/
│   └── survey_{user_id}_{uuid}.json
└── reports/
    └── report_{user_id}_{uuid}.json
```

### File Formats

**Session File Example:**
```json
{
  "session_id": "session_P001_abc123",
  "user_id": "P001",
  "started_at": "2026-02-24T10:30:00",
  "ended_at": "2026-02-24T11:25:00",
  "current_stage": "completed",
  "completed_stages": [
    "registration",
    "big5_assessment",
    "task_selection",
    "task_dialogue",
    "task_response",
    "post_survey"
  ],
  "big5_assessment_id": "assessment_P001_def456",
  "dialogue_records": ["dialogue_P001_ghi789"],
  "task_response_ids": ["noble_P001_jkl012"],
  "survey_ids": ["survey_P001_mno345"],
  "report_id": "report_P001_pqr678"
}
```

**Dialogue File Example:**
```json
{
  "dialogue_id": "dialogue_P001_ghi789",
  "session_id": "session_P001_abc123",
  "task_name": "Noble Industries",
  "llm_personality": "role_model",
  "started_at": "2026-02-24T10:45:00",
  "ended_at": "2026-02-24T11:10:00",
  "messages": [
    {
      "role": "assistant",
      "content": "Hello! I'm excited to help...",
      "timestamp": "2026-02-24T10:45:05"
    },
    {
      "role": "user",
      "content": "Great! Let's start...",
      "timestamp": "2026-02-24T10:45:30"
    }
  ],
  "total_messages": 32,
  "duration_seconds": 1500
}
```

### Data Persistence

**Save Operations:**
- Automatic save after each stage completion
- Incremental saves during dialogue
- Atomic write operations (temp file + rename)

**Load Operations:**
- Lazy loading (load on demand)
- Caching for frequently accessed data
- Error handling for corrupted files

**Backup Strategy:**
- Manual download from Streamlit Cloud
- Recommended: Weekly backups during active collection
- Export to local storage or cloud (S3, Google Drive)

---

## Data Analysis

### Built-in Analytics

#### 1. Personality Analysis

**Trait Distributions:**
```python
def analyze_trait_distributions(assessments):
    return {
        'openness': calculate_distribution(assessments, 'openness'),
        'conscientiousness': calculate_distribution(assessments, 'conscientiousness'),
        'extraversion': calculate_distribution(assessments, 'extraversion'),
        'agreeableness': calculate_distribution(assessments, 'agreeableness'),
        'neuroticism': calculate_distribution(assessments, 'neuroticism')
    }
```

**Gerlach Type Frequencies:**
```python
def analyze_gerlach_types(assessments):
    return {
        'average': count_type(assessments, 'average'),
        'role_model': count_type(assessments, 'role_model'),
        'self_centred': count_type(assessments, 'self_centred'),
        'reserved': count_type(assessments, 'reserved')
    }
```

#### 2. Dialogue Analysis

**Metrics:**
- Average dialogue length (messages)
- Average dialogue duration (minutes)
- Message length distributions
- Turn-taking patterns
- Response times

**By Personality:**
- Dialogue metrics grouped by AI personality
- Dialogue metrics grouped by user Gerlach type
- Cross-tabulation analysis

#### 3. Task Performance Analysis

**Noble Industries:**
- Ranking consensus analysis
- Rationale length and quality
- Ranking changes during dialogue

**Popcorn Brain:**
- Self-assessment vs automated metrics correlation
- Creativity dimension distributions
- Ideas per minute by personality type

#### 4. Survey Analysis

**Quantitative:**
- Mean scores per question
- Standard deviations
- Correlations with personality traits
- Factor analysis (optional)

**Qualitative:**
- Thematic coding of open-ended responses
- Sentiment analysis (optional)
- Word frequency analysis

### Export Formats

**For Statistical Analysis:**
- CSV export of all data tables
- SPSS/R-compatible formats
- Long-form and wide-form data

**For Qualitative Analysis:**
- Dialogue transcripts (TXT, MD)
- Survey responses (CSV, JSON)
- Coded themes (CSV)

### Analysis Scripts

**Location**: Root directory

**Available Scripts:**
- `analyze_personality_data.py` - Trait analysis
- `analyze_dialogues.py` - Conversation metrics
- `analyze_creativity.py` - Popcorn Brain metrics
- `export_for_spss.py` - SPSS export
- `generate_visualizations.py` - Charts and graphs

---

## Deployment & Access

### Deployment Information

**Platform**: Streamlit Cloud  
**Tier**: Free  
**URLs**: English `https://gerlach-research.streamlit.app/` · Korean `https://blueberryfresh-research-ko.streamlit.app/` (both deployed from `main`; Korean uses the `APP_LANG=ko` secret)  
**GitHub**: `https://github.com/blueberryfresh/gerlach-research-platform`

### Access Levels

**Public Access:**
- Anyone with URL can access
- No authentication required
- Participant ID serves as identifier

**Researcher Access:**
- GitHub repository access
- Streamlit Cloud dashboard access
- Data download capabilities

### Global Availability

**Geographic Coverage**: Worldwide  
**Uptime**: 24/7 (with 7-day sleep on inactivity)  
**Latency**: Optimized for global access  
**Language**: English only

### Scaling Limits

**Free Tier Limits:**
- 1 GB RAM per app
- Shared CPU resources
- ~100 concurrent users
- 1 GB ephemeral storage

**Recommendations:**
- Monitor concurrent users
- Upgrade to Teams ($250/month) if needed
- Implement queue system for high traffic

---

## Operational Procedures

### Participant Management

#### 1. Creating Participant IDs

**Format**: Alphanumeric, unique  
**Examples**: `P001`, `P042`, `KOREA_001`, `PARTICIPANT_123`

**Best Practices:**
- Use consistent format
- Track assignments in spreadsheet
- Include cohort/group identifiers if needed

#### 2. Recruitment

**Materials Needed:**
- App URL
- Participant instructions (USER_GUIDE.md)
- Participant IDs
- Consent forms (if separate)
- Contact information

**Distribution Methods:**
- Email invitations
- Course management systems
- Research participant pools
- Social media (if applicable)

#### 3. Monitoring

**Daily Checks:**
- App status (running/sleeping)
- Error logs
- Completion rates
- Data integrity

**Weekly Tasks:**
- Download data backups
- Review participant progress
- Respond to support requests
- Update tracking spreadsheet

### Data Management

#### 1. Data Collection

**During Active Collection:**
- Monitor app daily
- Check for errors
- Respond to participant issues
- Track completion rates

**Data Backup:**
- Download weekly (minimum)
- Store in multiple locations
- Verify file integrity
- Document backup dates

#### 2. Data Download

**Method 1: Manual Download**
1. Access Streamlit Cloud dashboard
2. Go to app settings
3. Download research_data folder
4. Extract and organize locally

**Method 2: Automated Backup** (requires setup)
1. Configure cloud storage (S3, Google Drive)
2. Set up automated sync
3. Schedule daily/weekly backups

#### 3. Data Verification

**Checks:**
- File count matches participant count
- No corrupted JSON files
- All required fields present
- Timestamps are sequential
- Cross-references are valid

**Tools:**
```python
# Verify data integrity
python verify_data_integrity.py

# Generate data summary
python summarize_collected_data.py
```

### Quality Control

#### 1. Pilot Testing

**Before Full Launch:**
- Test with 5-10 pilot participants
- Complete full workflow for each task
- Test all AI personalities
- Verify data collection
- Check report generation

#### 2. Monitoring Metrics

**Track:**
- Completion rate (started vs completed)
- Drop-off points (which stage)
- Average session duration
- Error frequency
- API usage and costs

#### 3. Participant Support

**Response Protocol:**
- Respond within 24 hours
- Provide clear instructions
- Document common issues
- Update FAQ as needed

---

## Security & Privacy

### Data Protection

**Encryption:**
- HTTPS for all connections
- Encrypted secrets storage (API keys)
- Secure data transmission

**Access Control:**
- GitHub repository access control
- Streamlit Cloud authentication
- No public data exposure

**Anonymization:**
- Only Participant IDs stored
- No personal information collected
- No IP address logging (configurable)

### Compliance

**IRB Requirements:**
- Informed consent
- Data retention policies
- Participant rights
- Withdrawal procedures

**GDPR Considerations** (if applicable):
- Right to access
- Right to deletion
- Data portability
- Privacy by design

### Data Retention

**During Study:**
- Data stored on Streamlit Cloud
- Regular backups to local/cloud storage

**After Study:**
- Download all data
- Delete from Streamlit Cloud
- Archive per IRB protocol
- Retain for required period (typically 3-7 years)

---

## Troubleshooting

### Common Issues

#### 1. App Not Loading

**Symptoms**: Blank page, timeout errors  
**Causes**: 
- App sleeping (7-day inactivity)
- Deployment errors
- API key issues

**Solutions:**
- Wake app from dashboard
- Check deployment logs
- Verify API key in secrets
- Reboot app

#### 2. API Key Errors

**Symptoms**: "ANTHROPIC_API_KEY not found"  
**Causes**:
- Missing secret configuration
- Incorrect secret format
- API key expired/invalid

**Solutions:**
- Add key to Streamlit secrets
- Verify TOML format
- Check API key validity
- Reboot app after adding secret

#### 3. Data Not Saving

**Symptoms**: Participant data missing  
**Causes**:
- Storage permission issues
- File write errors
- App restart during save

**Solutions:**
- Check app logs
- Verify storage directory exists
- Test with pilot participant
- Contact Streamlit support

#### 4. Slow Performance

**Symptoms**: Long load times, timeouts  
**Causes**:
- High concurrent users
- Large data files
- API rate limits

**Solutions:**
- Monitor concurrent users
- Optimize data loading
- Implement caching
- Upgrade to Teams tier

### Support Resources

**Streamlit:**
- Documentation: https://docs.streamlit.io
- Community: https://discuss.streamlit.io
- Support: support@streamlit.io

**Anthropic:**
- Documentation: https://docs.anthropic.com
- API Status: https://status.anthropic.com
- Support: support@anthropic.com

---

## API & Integration

### Anthropic Claude API

**Model**: claude-opus-4-20250514  
**Endpoint**: Anthropic Messages API  
**Authentication**: API key in secrets

**Usage Tracking:**
```python
# Monitor API usage
import anthropic

client = anthropic.Anthropic(api_key=api_key)
# Usage is tracked per request
# Check Anthropic dashboard for totals
```

**Cost Estimation:**
- Input tokens: ~$15 per million
- Output tokens: ~$75 per million
- Average dialogue: ~10,000 tokens
- Cost per participant: ~$0.01-0.03

### Custom Extensions

**Adding New Tasks:**
1. Create task PDF in `Task/` folder
2. Add task-specific response model
3. Implement capture logic in `TaskResponseAgent`
4. Create UI component in `task_response_ui.py`
5. Update workflow routing

**Adding New Metrics:**
1. Define metric calculation function
2. Add to appropriate agent
3. Update data models
4. Include in reports

**Integration Points:**
- `agents/` - Add new agents
- `task_response_ui.py` - Add UI components
- `agent_research_app.py` - Update routing

---

## Appendices

### A. File Manifest

**Core Application:**
- `agent_research_app.py` - Main Streamlit app
- `task_response_ui.py` - Task UI components
- `gerlach_personality_llms.py` - AI personalities
- `requirements.txt` - Dependencies

**Agents:**
- `agents/__init__.py` - Package initialization
- `agents/data_models.py` - Data structures
- `agents/supervisor_agent.py` - Workflow coordinator
- `agents/big5_assessment_agent.py` - Personality assessment
- `agents/dialogue_capture_agent.py` - Conversation recording
- `agents/task_response_agent.py` - Task data capture
- `agents/survey_agent.py` - Survey management
- `agents/summary_agent.py` - Report generation
- `agents/task_response_models.py` - Task data models

**Documentation:**
- `docs/USER_GUIDE.md` - Participant instructions
- `docs/TECHNICAL_DOCUMENTATION_FOR_COLLABORATORS.md` - This document
- `docs/DEPLOYMENT_GUIDE_STREAMLIT_CLOUD.md` - Deployment instructions
- `docs/PARTICIPANT_INSTRUCTIONS.md` - Detailed participant guide

**Tasks:**
- `Task/Noble Industries.pdf` - Candidate evaluation task
- `Task/Popcorn Brain.pdf` - Creative brainstorming task

### B. Data Dictionary

**Available upon request** - Detailed field-by-field documentation of all data structures.

### C. Analysis Templates

**Available in repository:**
- R analysis scripts
- Python analysis notebooks
- SPSS syntax files
- Visualization templates

### D. Contact Information

**Principal Investigator:**
[Name, Email, Phone]

**Technical Support:**
[Name, Email]

**Data Analysis:**
[Name, Email]

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Feb 2026 | Initial release | Research Team |

---

## Acknowledgments

This platform was developed using:
- Streamlit (web framework)
- Anthropic Claude (AI capabilities)
- Python ecosystem (data processing)

---

*Gerlach Personality Research Platform*  
*Technical Documentation for Collaborators*  
*Version 1.0 | February 2026*
