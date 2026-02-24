# Constitution

## Project Overview
**Gerlach Personality Research Platform** - A web-based research application for studying user-LLM collaboration across different personality types and tasks.

## Core Requirements

### 1. Application Type
- **Platform**: Web-based application
- **Deployment**: Static web app with backend API
- **Access**: Browser-based, no installation required
- **Scalability**: Support up to 100 concurrent participants

### 2. Essential Features
1. **User Registration**: Participant ID entry and consent
2. **Task Selection**: Choose from predefined tasks (Noble Industries, Popcorn Brain)
3. **LLM Selection**: Choose from 4 Gerlach personality types (Average, Role Model, Self-Centred, Reserved)
4. **Dialogue Interface**: Real-time chat between user and LLM
5. **Data Capture**: Record all user-LLM interactions with timestamps
6. **Data Storage**: Persistent database for ~100 participants
7. **Report Generation**: Automated descriptive summary reports per session

### 3. Data Requirements

#### Must Capture Per Session:
- User ID
- Selected task
- Selected LLM personality type
- Complete dialogue transcript (all messages with timestamps)
- Task-specific metrics:
  - **Noble Industries**: Rankings and rationales
  - **Popcorn Brain**: Creative dimensions (Originality, Flexibility, Elaboration, Fluency)

#### Must Store:
- User sessions (participant ID, timestamps, task, LLM type)
- Dialogue records (complete conversation history)
- Task responses (rankings, rationales, creative metrics)
- Generated reports (summary analytics)

### 4. Technical Constraints
- Must be web-accessible
- Must support ~100 participants
- Must persist data reliably
- Must generate downloadable reports
- Must integrate with LLM API (Anthropic Claude)

### 5. Non-Functional Requirements
- **Privacy**: Anonymized participant data
- **Reliability**: No data loss during sessions
- **Usability**: Intuitive interface requiring no training
- **Performance**: Real-time LLM responses (<5 seconds)
- **Availability**: Accessible 24/7 during research period

### 6. Out of Scope
- Mobile native applications
- Real-time collaboration between multiple users
- Video/audio communication
- Advanced analytics dashboard (beyond basic reports)
- User authentication beyond participant ID

## Success Criteria
1. ✅ 100 participants can complete sessions without technical issues
2. ✅ All dialogue data is captured and stored accurately
3. ✅ Task-specific metrics are collected and analyzed
4. ✅ Reports are generated automatically and downloadable
5. ✅ System maintains data integrity throughout research period

## Constraints
- **Budget**: Use existing infrastructure (Streamlit + local/cloud hosting)
- **Timeline**: Rapid deployment for research study
- **Resources**: Single developer, existing LLM API access
- **Compliance**: IRB-approved data collection protocols
