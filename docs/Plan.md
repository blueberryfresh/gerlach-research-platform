# Plan

## Implementation Plan: Gerlach Personality Research Platform

### Overview
This plan outlines the technical architecture and implementation strategy for building a web-based research platform supporting 100 participants in user-LLM collaborative task-solving experiments.

---

## 1. Architecture

### 1.1 System Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ Registration│  │  Dialogue  │  │  Report Viewer   │  │
│  │   Screen   │  │ Interface  │  │                  │  │
│  └────────────┘  └────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│              Streamlit Application Server                │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Multi-Agent System                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │  │
│  │  │Supervisor│  │Assessment│  │   Dialogue   │   │  │
│  │  │  Agent   │  │  Agent   │  │    Agent     │   │  │
│  │  └──────────┘  └──────────┘  └──────────────┘   │  │
│  │  ┌──────────┐  ┌──────────┐                      │  │
│  │  │  Survey  │  │ Summary  │                      │  │
│  │  │  Agent   │  │  Agent   │                      │  │
│  │  └──────────┘  └──────────┘                      │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Gerlach Personality LLM Manager          │  │
│  │  (Average, Role Model, Self-Centred, Reserved)   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  External Services                       │
│  ┌──────────────┐         ┌──────────────────────────┐ │
│  │ Anthropic API│         │   Local File System      │ │
│  │ (Claude LLM) │         │   (JSON Database)        │ │
│  └──────────────┘         └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow
```
User Registration → Session Creation → Task Selection → 
Dialogue Recording → Task-Specific Data Capture → 
Survey Completion → Report Generation → Data Export
```

---

## 2. Technology Stack

### 2.1 Core Technologies
- **Frontend Framework**: Streamlit 1.30+
- **Backend Language**: Python 3.9+
- **LLM API**: Anthropic Claude API (anthropic SDK)
- **Database**: JSON file-based storage
- **PDF Processing**: PyPDF2 3.0+
- **Data Analysis**: pandas, numpy (for metrics calculation)

### 2.2 Development Tools
- **Version Control**: Git
- **Package Management**: pip + requirements.txt
- **Testing**: pytest
- **Code Quality**: pylint, black (formatter)

### 2.3 Deployment Options
- **Option A**: Local server (development/small-scale)
- **Option B**: Streamlit Cloud (recommended for 100 users)
- **Option C**: Docker container on cloud platform (AWS, GCP, Azure)

---

## 3. Database Design

### 3.1 File-Based Storage Structure
```
research_data/
├── sessions/
│   └── {user_id}_{timestamp}_{uuid}.json
├── assessments/
│   └── assessment_{user_id}_{uuid}.json
├── dialogues/
│   └── dialogue_{user_id}_{uuid}.json
├── task_responses/
│   ├── noble/
│   │   └── noble_{session_id}.json
│   └── popcorn/
│       └── popcorn_{session_id}.json
├── surveys/
│   └── survey_{user_id}_{uuid}.json
└── reports/
    ├── {report_id}.json
    ├── {report_id}.md
    └── {report_id}.html
```

### 3.2 Data Schemas (JSON)

#### Session Schema
```json
{
  "session_id": "string",
  "user_id": "string",
  "started_at": "ISO8601 datetime",
  "ended_at": "ISO8601 datetime | null",
  "current_stage": "enum(registration|assessment|task_selection|dialogue|survey|completed)",
  "completed_stages": ["string"],
  "big5_assessment_id": "string | null",
  "dialogue_records": ["string"],
  "task_responses": ["string"],
  "survey_id": "string | null",
  "report_id": "string | null",
  "metadata": {}
}
```

#### Dialogue Schema
```json
{
  "dialogue_id": "string",
  "session_id": "string",
  "user_id": "string",
  "task_name": "string",
  "llm_personality": "string",
  "started_at": "ISO8601 datetime",
  "ended_at": "ISO8601 datetime | null",
  "messages": [
    {
      "message_id": "string",
      "timestamp": "ISO8601 datetime",
      "role": "user | assistant",
      "content": "string",
      "metadata": {}
    }
  ],
  "total_messages": "integer",
  "user_message_count": "integer",
  "assistant_message_count": "integer",
  "duration_seconds": "float | null"
}
```

#### Noble Industries Task Response Schema
```json
{
  "task_response_id": "string",
  "session_id": "string",
  "dialogue_id": "string",
  "task_type": "noble_industries",
  "submitted_at": "ISO8601 datetime",
  "rankings": [
    {
      "rank": "integer",
      "candidate_name": "string",
      "rationale": "string"
    }
  ],
  "metadata": {
    "ranking_changes": "integer",
    "time_to_complete": "float"
  }
}
```

#### Popcorn Brain Task Response Schema
```json
{
  "task_response_id": "string",
  "session_id": "string",
  "dialogue_id": "string",
  "task_type": "popcorn_brain",
  "submitted_at": "ISO8601 datetime",
  "self_assessment": {
    "originality": "integer (1-7)",
    "flexibility": "integer (1-7)",
    "elaboration": "integer (1-7)",
    "fluency": "integer (1-7)"
  },
  "computed_metrics": {
    "originality": {
      "unique_ideas_count": "integer",
      "novelty_score": "float",
      "examples": ["string"]
    },
    "flexibility": {
      "alternative_approaches_count": "integer",
      "topic_switches": "integer",
      "examples": ["string"]
    },
    "elaboration": {
      "detail_density": "float",
      "synthesis_instances": "integer",
      "examples": ["string"]
    },
    "fluency": {
      "total_ideas": "integer",
      "ideas_per_minute": "float",
      "idea_timestamps": ["ISO8601 datetime"]
    }
  }
}
```

---

## 4. Implementation Phases

### Phase 1: Foundation (COMPLETED ✅)
**Duration**: 1 week

**Deliverables**:
- ✅ Multi-agent system architecture
- ✅ Data models and schemas
- ✅ Supervisor Agent
- ✅ Big5 Assessment Agent
- ✅ Dialogue Capture Agent
- ✅ Survey Agent
- ✅ Summary Report Agent
- ✅ Basic Streamlit interface
- ✅ Unit tests

### Phase 2: Task-Specific Features (CURRENT)
**Duration**: 1 week

**Deliverables**:
- Noble Industries ranking interface
- Noble Industries data capture and storage
- Popcorn Brain self-assessment interface
- Popcorn Brain creative metrics computation
- Task-specific report sections
- Integration tests

### Phase 3: Enhanced Analytics
**Duration**: 1 week

**Deliverables**:
- Automated idea extraction from dialogues
- NLP-based creativity metrics
- Dialogue quality analysis
- Comparative analytics (across personalities/tasks)
- Enhanced visualizations in reports

### Phase 4: Testing & Refinement
**Duration**: 1 week

**Deliverables**:
- Pilot study with 10 participants
- Bug fixes and UX improvements
- Performance optimization
- Documentation updates
- Deployment preparation

### Phase 5: Deployment & Data Collection
**Duration**: 2-4 weeks

**Deliverables**:
- Production deployment
- Participant recruitment
- Data collection (100 participants)
- Monitoring and support
- Interim data backups

### Phase 6: Analysis & Reporting
**Duration**: 2 weeks

**Deliverables**:
- Bulk data export
- Statistical analysis
- Research findings report
- Publication-ready visualizations

---

## 5. Technical Implementation Details

### 5.1 Noble Industries Task Implementation

#### Ranking Interface
```python
# Streamlit component for drag-and-drop ranking
candidates = load_candidates_from_pdf("Noble Industries.pdf")

# Display candidates with ranking controls
for i, candidate in enumerate(candidates):
    col1, col2, col3 = st.columns([1, 4, 6])
    with col1:
        rank = st.number_input(f"Rank", min_value=1, max_value=len(candidates), key=f"rank_{i}")
    with col2:
        st.write(candidate['name'])
    with col3:
        rationale = st.text_area(f"Rationale", key=f"rationale_{i}")
```

#### Data Capture
```python
def capture_noble_rankings(session_id, dialogue_id, rankings):
    """Capture and validate Noble Industries rankings"""
    task_response = {
        "task_response_id": f"noble_{session_id}_{uuid4().hex[:8]}",
        "session_id": session_id,
        "dialogue_id": dialogue_id,
        "task_type": "noble_industries",
        "submitted_at": datetime.now().isoformat(),
        "rankings": rankings,
        "metadata": {
            "ranking_changes": calculate_ranking_changes(dialogue_id),
            "time_to_complete": calculate_completion_time(dialogue_id)
        }
    }
    save_task_response(task_response, "noble")
    return task_response
```

### 5.2 Popcorn Brain Task Implementation

#### Self-Assessment Interface
```python
# Streamlit sliders for self-assessment
st.subheader("Creative Performance Self-Assessment")

originality = st.slider(
    "I created unique ideas to solve a given problem",
    min_value=1, max_value=7, value=4,
    help="1 = Strongly Disagree, 7 = Strongly Agree"
)

flexibility = st.slider(
    "I presented alternative ideas to other group members' ideas",
    min_value=1, max_value=7, value=4
)

elaboration = st.slider(
    "I created details to add to other members' ideas",
    min_value=1, max_value=7, value=4
)

fluency = st.slider(
    "I created many ideas to solve a given problem",
    min_value=1, max_value=7, value=4
)
```

#### Automated Metrics Computation
```python
def compute_popcorn_metrics(dialogue_id):
    """Compute creative metrics from dialogue"""
    dialogue = load_dialogue(dialogue_id)
    
    # Extract user messages
    user_messages = [m for m in dialogue['messages'] if m['role'] == 'user']
    
    # Compute metrics
    metrics = {
        "originality": {
            "unique_ideas_count": count_unique_ideas(user_messages),
            "novelty_score": calculate_novelty(user_messages),
            "examples": extract_unique_ideas(user_messages)
        },
        "flexibility": {
            "alternative_approaches_count": count_alternatives(user_messages),
            "topic_switches": count_topic_switches(user_messages),
            "examples": extract_alternatives(user_messages)
        },
        "elaboration": {
            "detail_density": calculate_detail_density(user_messages),
            "synthesis_instances": count_synthesis(user_messages),
            "examples": extract_elaborations(user_messages)
        },
        "fluency": {
            "total_ideas": count_total_ideas(user_messages),
            "ideas_per_minute": calculate_ideas_per_minute(dialogue),
            "idea_timestamps": extract_idea_timestamps(user_messages)
        }
    }
    
    return metrics
```

#### Idea Extraction (NLP-based)
```python
def count_unique_ideas(messages):
    """Count unique ideas using keyword extraction and clustering"""
    # Simple implementation: count sentences with idea markers
    idea_markers = ['could', 'should', 'what if', 'maybe', 'perhaps', 'idea:', 'suggestion:']
    unique_ideas = set()
    
    for message in messages:
        sentences = message['content'].split('.')
        for sentence in sentences:
            if any(marker in sentence.lower() for marker in idea_markers):
                # Simple deduplication by content similarity
                unique_ideas.add(sentence.strip())
    
    return len(unique_ideas)

def count_alternatives(messages):
    """Count alternative approaches presented"""
    alternative_markers = ['alternatively', 'another way', 'instead', 'or we could', 'different approach']
    count = 0
    
    for message in messages:
        count += sum(1 for marker in alternative_markers if marker in message['content'].lower())
    
    return count
```

### 5.3 Report Generation Enhancement

```python
def generate_task_specific_report(session_id, task_type):
    """Generate task-specific report section"""
    if task_type == "noble_industries":
        return generate_noble_report(session_id)
    elif task_type == "popcorn_brain":
        return generate_popcorn_report(session_id)

def generate_popcorn_report(session_id):
    """Generate Popcorn Brain task report"""
    task_response = load_task_response(session_id, "popcorn")
    
    report = f"""
## Popcorn Brain Task: Creative Performance

### Self-Assessment Ratings (1-7 scale)
- **Originality**: {task_response['self_assessment']['originality']}/7
- **Flexibility**: {task_response['self_assessment']['flexibility']}/7
- **Elaboration**: {task_response['self_assessment']['elaboration']}/7
- **Fluency**: {task_response['self_assessment']['fluency']}/7

### Computed Metrics from Dialogue
- **Unique Ideas Generated**: {task_response['computed_metrics']['originality']['unique_ideas_count']}
- **Alternative Approaches**: {task_response['computed_metrics']['flexibility']['alternative_approaches_count']}
- **Detail Density**: {task_response['computed_metrics']['elaboration']['detail_density']:.2f} words/idea
- **Total Ideas**: {task_response['computed_metrics']['fluency']['total_ideas']}
- **Ideas per Minute**: {task_response['computed_metrics']['fluency']['ideas_per_minute']:.2f}

### Creative Dimension Analysis
[Visualization: Bar chart comparing self-assessment vs computed metrics]
"""
    return report
```

---

## 6. Deployment Strategy

### 6.1 Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"

# Run application
streamlit run agent_research_app.py --server.port 8505
```

### 6.2 Streamlit Cloud Deployment
1. Push code to GitHub repository
2. Connect Streamlit Cloud to repository
3. Add secrets (ANTHROPIC_API_KEY) in dashboard
4. Deploy with auto-reload on commits
5. Custom domain (optional): research.yourlab.edu

### 6.3 Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8505
CMD ["streamlit", "run", "agent_research_app.py", "--server.port=8505"]
```

### 6.4 Data Backup Strategy
- **Frequency**: Hourly incremental, daily full backup
- **Storage**: Cloud storage (S3, Google Drive, Dropbox)
- **Retention**: Keep all data for duration of study + 5 years
- **Encryption**: AES-256 encryption for backups

---

## 7. Performance Optimization

### 7.1 Caching Strategy
```python
@st.cache_resource
def init_agents():
    """Cache agent initialization"""
    return {
        'supervisor': SupervisorAgent(DATA_DIR),
        'assessment': Big5AssessmentAgent(DATA_DIR),
        # ... other agents
    }

@st.cache_data(ttl=3600)
def load_task_document(task_name):
    """Cache task documents for 1 hour"""
    return load_pdf(TASK_FOLDER / task_name)
```

### 7.2 Database Optimization
- Index session files by user_id
- Compress old dialogue records
- Implement lazy loading for large reports
- Use connection pooling for concurrent access

### 7.3 LLM API Optimization
- Implement request queuing for rate limits
- Cache common responses (not applicable for research)
- Use streaming responses for better UX
- Implement retry logic with exponential backoff

---

## 8. Security & Privacy

### 8.1 Data Protection
- **Anonymization**: No PII collected, only participant IDs
- **Encryption**: HTTPS for all communications
- **Access Control**: Password-protected admin interface
- **Audit Logging**: Track all data access

### 8.2 API Key Management
```python
# Environment variable (recommended)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Streamlit secrets (for cloud deployment)
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
```

### 8.3 IRB Compliance
- Informed consent collection
- Data retention policy
- Participant withdrawal mechanism
- Secure data storage and transmission

---

## 9. Monitoring & Logging

### 9.1 Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Session {session_id} created for user {user_id}")
```

### 9.2 Metrics to Track
- Active sessions count
- Completion rate by stage
- Average dialogue duration
- LLM API response times
- Error rates and types
- User dropout points

### 9.3 Alerting
- Email alerts for system errors
- Daily summary reports
- Low disk space warnings
- API quota warnings

---

## 10. Testing Strategy

### 10.1 Unit Tests
```python
def test_session_creation():
    supervisor = SupervisorAgent(TEST_DATA_DIR)
    session = supervisor.create_user_session("TEST001")
    assert session.user_id == "TEST001"
    assert session.current_stage == WorkflowStage.REGISTRATION

def test_popcorn_metrics_computation():
    metrics = compute_popcorn_metrics(test_dialogue_id)
    assert metrics['fluency']['total_ideas'] > 0
    assert 0 <= metrics['fluency']['ideas_per_minute'] <= 10
```

### 10.2 Integration Tests
```python
def test_end_to_end_workflow():
    # Create session
    session = create_session("TEST001")
    
    # Complete assessment
    assessment = complete_assessment(session.session_id, test_responses)
    
    # Start dialogue
    dialogue = start_dialogue(session.session_id, "Popcorn Brain.pdf", "average")
    
    # Record messages
    record_messages(dialogue.dialogue_id, test_messages)
    
    # Submit task response
    task_response = submit_popcorn_assessment(session.session_id, test_self_assessment)
    
    # Generate report
    report = generate_report(session.session_id)
    
    assert report.total_dialogues == 1
    assert report.report_id is not None
```

### 10.3 Load Testing
```python
# Simulate 100 concurrent users
from locust import HttpUser, task, between

class ResearchParticipant(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def complete_session(self):
        # Create session
        self.client.post("/api/sessions", json={"user_id": f"TEST{self.user_id}"})
        
        # Complete workflow
        # ... simulate user actions
```

---

## 11. Data Analysis Pipeline

### 11.1 Export Scripts
```python
def export_all_data():
    """Export all research data for analysis"""
    sessions = load_all_sessions()
    dialogues = load_all_dialogues()
    task_responses = load_all_task_responses()
    
    # Create pandas DataFrames
    df_sessions = pd.DataFrame([s.to_dict() for s in sessions])
    df_dialogues = pd.DataFrame([d.to_dict() for d in dialogues])
    df_tasks = pd.DataFrame([t.to_dict() for t in task_responses])
    
    # Export to CSV
    df_sessions.to_csv('exports/sessions.csv', index=False)
    df_dialogues.to_csv('exports/dialogues.csv', index=False)
    df_tasks.to_csv('exports/task_responses.csv', index=False)
```

### 11.2 Statistical Analysis
```python
def analyze_popcorn_brain_results():
    """Analyze Popcorn Brain task results"""
    responses = load_all_popcorn_responses()
    
    # Group by LLM personality
    by_personality = group_by(responses, 'llm_personality')
    
    # Compute statistics
    stats = {}
    for personality, data in by_personality.items():
        stats[personality] = {
            'mean_originality': np.mean([d['self_assessment']['originality'] for d in data]),
            'mean_fluency': np.mean([d['computed_metrics']['fluency']['ideas_per_minute'] for d in data]),
            # ... other metrics
        }
    
    return stats
```

---

## 12. Maintenance & Support

### 12.1 Regular Maintenance
- **Daily**: Check logs for errors, monitor active sessions
- **Weekly**: Backup data, review completion rates
- **Monthly**: Update dependencies, security patches

### 12.2 Participant Support
- **FAQ Document**: Common issues and solutions
- **Email Support**: research-support@yourlab.edu
- **Response Time**: <24 hours for technical issues

### 12.3 Post-Study Activities
- Data archival
- Code repository cleanup
- Documentation finalization
- Publication of anonymized dataset (optional)

---

## 13. Budget & Resources

### 13.1 Infrastructure Costs
- **Streamlit Cloud**: Free tier (sufficient for 100 users)
- **Anthropic API**: ~$0.01-0.03 per dialogue (estimate $50-150 total)
- **Cloud Storage**: <$5/month
- **Domain (optional)**: $12/year

**Total Estimated Cost**: $200-300 for entire study

### 13.2 Time Estimates
- **Development**: 4 weeks (1 developer)
- **Testing**: 1 week
- **Data Collection**: 2-4 weeks
- **Analysis**: 2 weeks

**Total Timeline**: 9-11 weeks

---

## 14. Risk Management

### 14.1 Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| LLM API downtime | Medium | High | Implement retry logic, queue system |
| Data loss | Low | Critical | Automated backups, redundant storage |
| Performance issues | Medium | Medium | Load testing, caching, optimization |
| Security breach | Low | High | Encryption, access control, auditing |

### 14.2 Research Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Low participation | Medium | High | Incentives, user-friendly interface |
| Data quality issues | Medium | Medium | Validation, pilot testing |
| Technical difficulties | High | Medium | Support system, documentation |

---

## 15. Success Criteria

### 15.1 Technical Success
- ✅ 100 participants complete sessions
- ✅ <1% data loss rate
- ✅ <5% error rate
- ✅ <5 second LLM response time (95th percentile)

### 15.2 Research Success
- ✅ All task-specific metrics captured
- ✅ High-quality dialogue data
- ✅ Actionable insights from reports
- ✅ Publishable findings

---

## 16. Next Steps

1. ✅ Complete Phase 1 (Foundation) - DONE
2. 🔄 Implement Phase 2 (Task-Specific Features) - IN PROGRESS
3. ⏳ Conduct pilot study (10 participants)
4. ⏳ Refine based on pilot feedback
5. ⏳ Deploy to production
6. ⏳ Recruit 100 participants
7. ⏳ Collect data
8. ⏳ Analyze results
9. ⏳ Publish findings
