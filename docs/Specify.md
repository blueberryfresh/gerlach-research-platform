# Specify

## Application Specification: Gerlach Personality Research Platform

### 1. Application Purpose
Build a web-based research platform that enables users to collaborate with LLM personalities to complete tasks, while capturing all interactions and generating analytical reports on user-LLM performance.

---

## 2. User Workflow

### 2.1 Session Initiation
1. User accesses web application via browser
2. User enters **Participant ID** (e.g., P001, P042)
3. User provides informed consent
4. System creates new session record

### 2.2 Task & LLM Selection
1. User selects one of two tasks:
   - **Noble Industries** (PDF document)
   - **Popcorn Brain** (PDF document)
2. User selects one of four LLM personalities:
   - **Average** (⚖️) - Balanced & Practical
   - **Role Model** (⭐) - Optimistic & Organized
   - **Self-Centred** (🎯) - Direct & Competitive
   - **Reserved** (🤫) - Calm & Conventional

### 2.3 Collaborative Dialogue
1. Task document is loaded and displayed to user
2. Chat interface opens with selected LLM personality
3. User and LLM engage in task-solving dialogue
4. All messages are captured with timestamps
5. User can end dialogue when task is complete

### 2.4 Task-Specific Data Collection

#### For Noble Industries Task:
- **Capture**: Candidate rankings (1st, 2nd, 3rd, etc.)
- **Capture**: Rationale for each ranking decision
- **Format**: Structured data (rank, candidate name, rationale text)

#### For Popcorn Brain Task:
- **Capture**: Four creative dimensions based on dialogue content:
  1. **Originality**: Uniqueness of ideas generated
     - Measurement: "I created unique ideas to solve a given problem"
  2. **Flexibility**: Alternative approaches presented
     - Measurement: "I presented alternative ideas to other group members' ideas"
  3. **Elaboration**: Detailed steps and synthesis
     - Measurement: "I created details to add to other members' ideas"
  4. **Fluency**: Quantity of ideas per unit time
     - Measurement: "I created many ideas to solve a given problem"
- **Format**: Ratings (1-7 scale) + extracted idea counts from dialogue

### 2.5 Session Completion
1. User completes post-task survey
2. System generates descriptive summary report
3. Report includes:
   - User ID
   - Task completed
   - LLM personality used
   - Dialogue transcript
   - Task-specific metrics
   - Performance analytics
4. User can download report (Markdown/HTML/PDF)

---

## 3. Data Models

### 3.1 User Session
```
{
  "session_id": "P001_20260224_143022_abc123",
  "user_id": "P001",
  "started_at": "2026-02-24T14:30:22Z",
  "ended_at": "2026-02-24T15:15:45Z",
  "task_name": "Noble Industries.pdf",
  "llm_personality": "role_model",
  "consent_given": true,
  "status": "completed"
}
```

### 3.2 Dialogue Record
```
{
  "dialogue_id": "dialogue_P001_xyz789",
  "session_id": "P001_20260224_143022_abc123",
  "messages": [
    {
      "message_id": "msg_001",
      "timestamp": "2026-02-24T14:32:10Z",
      "role": "user",
      "content": "Let's analyze the candidates..."
    },
    {
      "message_id": "msg_002",
      "timestamp": "2026-02-24T14:32:15Z",
      "role": "assistant",
      "content": "Great! Let's start by reviewing..."
    }
  ],
  "total_messages": 24,
  "duration_seconds": 2723
}
```

### 3.3 Noble Industries Task Data
```
{
  "task_response_id": "noble_P001_abc",
  "session_id": "P001_20260224_143022_abc123",
  "rankings": [
    {
      "rank": 1,
      "candidate": "Candidate A",
      "rationale": "Strong leadership experience and cultural fit..."
    },
    {
      "rank": 2,
      "candidate": "Candidate C",
      "rationale": "Excellent technical skills but limited management..."
    }
  ]
}
```

### 3.4 Popcorn Brain Task Data
```
{
  "task_response_id": "popcorn_P001_xyz",
  "session_id": "P001_20260224_143022_abc123",
  "creative_metrics": {
    "originality": {
      "rating": 6,
      "unique_ideas_count": 8,
      "examples": ["Idea 1 text", "Idea 2 text"]
    },
    "flexibility": {
      "rating": 5,
      "alternative_approaches": 4,
      "examples": ["Alternative 1", "Alternative 2"]
    },
    "elaboration": {
      "rating": 7,
      "detailed_plans": 3,
      "examples": ["Detailed plan 1", "Detailed plan 2"]
    },
    "fluency": {
      "rating": 6,
      "total_ideas": 12,
      "ideas_per_minute": 0.44
    }
  },
  "self_assessment": {
    "originality": 6,
    "flexibility": 5,
    "elaboration": 7,
    "fluency": 6
  }
}
```

---

## 4. Interface Specifications

### 4.1 Registration Screen
- **Input**: Text field for Participant ID
- **Input**: Checkbox for informed consent
- **Button**: "Begin Research Session"
- **Validation**: ID required, consent required

### 4.2 Task Selection Screen
- **Display**: Two task cards with descriptions
- **Input**: Radio buttons or cards for task selection
- **Input**: Dropdown or cards for LLM personality selection
- **Display**: Brief description of each personality type
- **Button**: "Start Task Dialogue"

### 4.3 Dialogue Interface
- **Display**: Task document (scrollable, read-only)
- **Display**: Chat history (user messages on right, LLM on left)
- **Input**: Text input area for user messages
- **Button**: "Send" message
- **Button**: "End Dialogue"
- **Display**: Message counter, time elapsed

### 4.4 Task-Specific Input Forms

#### Noble Industries:
- **Display**: List of candidates
- **Input**: Drag-and-drop ranking interface OR numbered dropdowns
- **Input**: Text area for rationale per candidate
- **Button**: "Submit Rankings"

#### Popcorn Brain:
- **Display**: Post-dialogue survey
- **Input**: 4 slider scales (1-7) for self-assessment:
  - "I created unique ideas to solve a given problem" (Originality)
  - "I presented alternative ideas" (Flexibility)
  - "I created details to add to ideas" (Elaboration)
  - "I created many ideas to solve a given problem" (Fluency)
- **Button**: "Submit Assessment"

### 4.5 Report Screen
- **Display**: Summary statistics (messages, duration, task)
- **Display**: Performance metrics (task-specific)
- **Display**: Full dialogue transcript
- **Button**: "Download Report (Markdown)"
- **Button**: "Download Report (HTML)"
- **Button**: "Download Report (PDF)" [optional]
- **Button**: "Start New Session"

---

## 5. Functional Requirements

### FR-1: User Registration
- System SHALL accept alphanumeric participant IDs
- System SHALL require informed consent before proceeding
- System SHALL create unique session ID per participant session

### FR-2: Task & LLM Selection
- System SHALL display both available tasks
- System SHALL display all four LLM personality types
- System SHALL load selected task document
- System SHALL initialize selected LLM personality

### FR-3: Dialogue Capture
- System SHALL record every user message with timestamp
- System SHALL record every LLM response with timestamp
- System SHALL persist messages in real-time (no data loss)
- System SHALL calculate dialogue duration

### FR-4: Noble Industries Task
- System SHALL capture candidate rankings
- System SHALL capture rationale for each ranking
- System SHALL validate all candidates are ranked
- System SHALL store rankings in structured format

### FR-5: Popcorn Brain Task
- System SHALL present 4 self-assessment questions
- System SHALL accept ratings on 1-7 scale
- System SHALL analyze dialogue for creative metrics
- System SHALL count unique ideas, alternatives, details, total ideas
- System SHALL calculate ideas per minute (fluency)

### FR-6: Report Generation
- System SHALL generate report automatically upon session completion
- System SHALL include: user ID, task, LLM type, dialogue, metrics
- System SHALL provide downloadable formats (Markdown, HTML)
- System SHALL archive reports for later retrieval

### FR-7: Data Storage
- System SHALL store all session data persistently
- System SHALL support up to 100 concurrent participants
- System SHALL prevent data corruption or loss
- System SHALL enable data export for analysis

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- LLM responses SHALL appear within 5 seconds (95th percentile)
- Page loads SHALL complete within 2 seconds
- System SHALL handle 100 concurrent users

### NFR-2: Usability
- Interface SHALL be intuitive (no training required)
- Interface SHALL be accessible (WCAG 2.1 AA)
- Interface SHALL work on desktop browsers (Chrome, Firefox, Safari, Edge)

### NFR-3: Reliability
- System SHALL have 99% uptime during research period
- System SHALL auto-save dialogue every 10 seconds
- System SHALL recover from network interruptions

### NFR-4: Security & Privacy
- Participant IDs SHALL be anonymized (no PII)
- Data SHALL be encrypted at rest
- API keys SHALL be stored securely (environment variables)
- Reports SHALL only be accessible to authorized researchers

### NFR-5: Maintainability
- Code SHALL be documented
- System SHALL have automated tests
- Database schema SHALL be versioned

---

## 7. Technical Specifications

### 7.1 Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.9+
- **LLM API**: Anthropic Claude (via `anthropic` Python SDK)
- **Database**: JSON file storage OR SQLite (for 100 users)
- **Hosting**: Local server OR cloud platform (Streamlit Cloud, Heroku, AWS)

### 7.2 LLM Integration
- **Model**: Claude 3 (Sonnet or Opus)
- **API**: Anthropic Messages API
- **System Prompts**: Custom prompts for each Gerlach personality
- **Context**: Task document prepended to conversation

### 7.3 Data Storage Structure
```
research_data/
├── sessions/          # Session metadata
├── dialogues/         # Complete transcripts
├── task_responses/    # Noble Industries rankings, Popcorn Brain metrics
├── reports/           # Generated reports
└── exports/           # Bulk data exports
```

### 7.4 API Endpoints (if using REST API)
- `POST /api/sessions` - Create new session
- `POST /api/dialogues/{dialogue_id}/messages` - Add message
- `GET /api/dialogues/{dialogue_id}` - Get dialogue
- `POST /api/tasks/noble/rankings` - Submit Noble Industries rankings
- `POST /api/tasks/popcorn/assessment` - Submit Popcorn Brain assessment
- `GET /api/reports/{session_id}` - Get report
- `GET /api/reports/{session_id}/download` - Download report

---

## 8. Measurement & Analytics

### 8.1 Noble Industries Metrics
- **Primary**: Ranking order (1st, 2nd, 3rd, etc.)
- **Qualitative**: Rationale quality (word count, coherence)
- **Process**: Number of ranking changes during dialogue
- **Collaboration**: LLM influence on final rankings

### 8.2 Popcorn Brain Metrics
- **Originality**: 
  - Self-rating (1-7)
  - Unique idea count (extracted from dialogue)
  - Novelty score (manual coding or NLP)
  
- **Flexibility**:
  - Self-rating (1-7)
  - Alternative approach count
  - Topic switching frequency
  
- **Elaboration**:
  - Self-rating (1-7)
  - Detail density (words per idea)
  - Synthesis instances
  
- **Fluency**:
  - Self-rating (1-7)
  - Total idea count
  - Ideas per minute

### 8.3 Dialogue Metrics (Both Tasks)
- Total messages exchanged
- User message count vs LLM message count
- Average message length (user vs LLM)
- Dialogue duration
- Response time distribution

---

## 9. Validation & Testing

### 9.1 Unit Tests
- Session creation and management
- Dialogue recording and retrieval
- Task-specific data capture
- Report generation

### 9.2 Integration Tests
- End-to-end workflow (registration → dialogue → report)
- LLM API integration
- Database persistence

### 9.3 User Acceptance Testing
- Pilot with 5-10 participants
- Verify data capture accuracy
- Validate report quality
- Test with all 4 LLM personalities × 2 tasks = 8 scenarios

---

## 10. Deliverables

1. ✅ **Web Application**: Fully functional Streamlit app
2. ✅ **Multi-Agent System**: 5 coordinating agents
3. ✅ **Database**: Persistent storage for 100 participants
4. ✅ **Reports**: Automated generation (Markdown, HTML)
5. ✅ **Documentation**: User guide, technical documentation
6. ✅ **Test Suite**: Automated tests for core functionality
7. ✅ **Deployment Guide**: Instructions for hosting
8. ✅ **Data Export**: Scripts for bulk data analysis

---

## 11. Success Metrics

- **Completion Rate**: >95% of participants complete sessions without errors
- **Data Integrity**: 100% of dialogues captured without loss
- **Usability**: <5% of participants require technical support
- **Performance**: <5 second LLM response time (95th percentile)
- **Reliability**: Zero data loss incidents during research period
