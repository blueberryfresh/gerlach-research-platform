# Administrator User Guide
## Gerlach Research Platform - Complete Admin Manual

**Version:** 1.0  
**Last Updated:** February 2026  
**For:** Research Administrators & Principal Investigators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Accessing the Admin Dashboard](#accessing-the-admin-dashboard)
4. [Dashboard Overview](#dashboard-overview)
5. [Downloading Participant Data](#downloading-participant-data)
6. [Data File Structure](#data-file-structure)
7. [Data Analysis Workflow](#data-analysis-workflow)
8. [Monitoring Study Progress](#monitoring-study-progress)
9. [Data Management Best Practices](#data-management-best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Security & Privacy](#security-and-privacy)
12. [Appendix](#appendix)

---

## Introduction

### Purpose of This Guide

This manual provides comprehensive instructions for administrators managing the Gerlach Research Platform. It covers all aspects of data collection, download, management, and analysis for your personality research study.

### What is the Gerlach Research Platform?

The Gerlach Research Platform is a web-based research tool that:
- Administers Big Five personality assessments (IPIP-50)
- Facilitates task-based dialogues with AI personalities
- Collects task-specific response data
- Administers post-experiment surveys
- Generates comprehensive participant reports

### Who Should Use This Guide?

- **Principal Investigators** - Overall study management
- **Research Coordinators** - Day-to-day operations
- **Data Analysts** - Data extraction and analysis
- **Technical Administrators** - System maintenance

### System Requirements

**For Administrators:**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Admin password access

**For Participants:**
- Any device with web browser
- Internet connection
- No software installation required

---

## Getting Started

### Your Research Platform URL

Your Gerlach Research Platform is hosted at:
```
https://[your-app-name].streamlit.app
```

**To find your exact URL:**
1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Locate your `gerlach-research-platform` app
4. Copy the URL from the app details

### Admin Credentials

**Password:** `Big5llmstudy`

**Security Note:** This password protects all participant data. Keep it confidential and share only with authorized research team members.

### First-Time Setup Checklist

Before collecting data:

- [ ] Verify app is accessible at your URL
- [ ] Test participant registration flow
- [ ] Complete a full test session yourself
- [ ] Access admin dashboard successfully
- [ ] Verify test data appears in downloads
- [ ] Delete test data before live collection
- [ ] Document your app URL for participants
- [ ] Prepare participant recruitment materials

---

## Accessing the Admin Dashboard

### Step-by-Step Access Instructions

#### Method 1: Via Sidebar Navigation (Recommended)

1. **Open your research platform URL** in a web browser
2. **Look at the left sidebar** (may need to click hamburger menu ☰ on mobile)
3. **Scroll to the bottom** of the sidebar
4. **Find "🔧 Admin Tools"** section
5. **Click "📊 Admin Download Center"** button
6. **Enter password:** `Big5llmstudy`
7. **Click "Login"**

#### Method 2: Direct Access (If Configured)

If you've set up multi-page navigation:
1. Open your research platform URL
2. Click "Admin Download" in the sidebar page list
3. Enter password when prompted

### Login Screen

When you access the admin page, you'll see:

```
🔒 Admin Access
Enter password to access data download page

Password: [••••••••••••]
         [Login]
```

**Important:** 
- Password is case-sensitive
- No username required
- Session persists until you click "Logout"

### Logging Out

Always log out when finished:
1. Scroll to top of admin dashboard
2. Click **"🔓 Logout"** button
3. You'll be returned to the login screen

**Security Best Practice:** Always log out on shared computers.

---

## Dashboard Overview

### Main Interface

After logging in, you'll see the **Admin Data Download Center** with three main tabs:

```
📊 Admin Data Download Center
Download participant data and manage research data exports

[🔓 Logout]

─────────────────────────────────────────────

[📥 Download All Data] [👤 Download by Participant] [📊 Export to CSV]
```

### Tab 1: Download All Data

**Purpose:** Download complete dataset for all participants

**Features:**
- Total participant count display
- One-click ZIP file creation
- Includes all data types (sessions, assessments, dialogues, tasks, surveys, reports)

**Best For:**
- Weekly backups
- End-of-study data collection
- Complete dataset archiving

### Tab 2: Download by Participant

**Purpose:** Download data for individual participants

**Features:**
- List of all participants with details
- Expandable sections per participant
- Individual ZIP downloads
- Session information preview

**Best For:**
- Reviewing specific participant data
- Quality control checks
- Troubleshooting individual cases
- Selective data extraction

### Tab 3: Export to CSV

**Purpose:** Export data in spreadsheet format for analysis

**Features:**
- Aggregated data across all participants
- Key metrics in columns
- Ready for statistical software
- Includes Big5 scores, dialogue stats, survey completion

**Best For:**
- Quantitative analysis
- Statistical testing
- Data visualization
- Quick overview of all participants

---

## Downloading Participant Data

### Option 1: Download All Data (Complete Dataset)

#### When to Use
- **Weekly backups** during data collection
- **Final download** at study completion
- **Complete archiving** for long-term storage

#### Step-by-Step Instructions

1. **Navigate to "Download All Data" tab**
2. **Review participant count**
   - Verify expected number of participants
   - Note: Count includes all sessions, even incomplete ones
3. **Click "📦 Create ZIP File"**
   - System will compile all data
   - May take 10-30 seconds depending on data volume
4. **Click "⬇️ Download All Data (ZIP)"** when button appears
5. **Save the file**
   - Filename format: `gerlach_research_data_YYYYMMDD_HHMMSS.zip`
   - Example: `gerlach_research_data_20260224_153045.zip`
6. **Verify download**
   - Check file size (should be >0 KB)
   - Try opening the ZIP to confirm it's not corrupted

#### What's Included

The ZIP file contains:

```
gerlach_research_data_20260224_153045.zip
│
├── sessions/
│   ├── P001_20260224_143022_abc123.json
│   ├── P002_20260224_150315_def456.json
│   └── ...
│
├── assessments/
│   ├── assessment_P001_xyz789.json
│   ├── assessment_P002_uvw012.json
│   └── ...
│
├── dialogues/
│   ├── dialogue_P001_abc456.json
│   ├── dialogue_P002_def789.json
│   └── ...
│
├── task_responses/
│   ├── noble/
│   │   ├── noble_P001_ghi012.json
│   │   └── ...
│   └── popcorn/
│       ├── popcorn_P002_jkl345.json
│       └── ...
│
├── surveys/
│   ├── survey_P001_mno678.json
│   ├── survey_P002_pqr901.json
│   └── ...
│
└── reports/
    ├── report_P001_20260224_143022_abc123.md
    ├── report_P001_20260224_143022_abc123.html
    ├── report_P002_20260224_150315_def456.md
    ├── report_P002_20260224_150315_def456.html
    └── ...
```

#### File Naming Convention

All files follow consistent naming:
- **Sessions:** `[UserID]_[Date]_[Time]_[UniqueID].json`
- **Assessments:** `assessment_[UserID]_[UniqueID].json`
- **Dialogues:** `dialogue_[UserID]_[UniqueID].json`
- **Task Responses:** `[TaskType]_[UserID]_[UniqueID].json`
- **Surveys:** `survey_[UserID]_[UniqueID].json`
- **Reports:** `report_[SessionID].md` or `.html`

---

### Option 2: Download Individual Participant

#### When to Use
- **Quality control** - Review specific participant's data
- **Troubleshooting** - Investigate issues with individual sessions
- **Selective extraction** - Need data for specific participants only
- **Ongoing monitoring** - Check recent participant completions

#### Step-by-Step Instructions

1. **Navigate to "Download by Participant" tab**
2. **Review participant list**
   - Shows all participants with basic info
   - Format: `👤 [User_ID] - [Current_Stage]`
3. **Click on a participant** to expand their section
4. **Review participant details:**
   - Session ID
   - Created timestamp
   - Current workflow stage
5. **Click "📦 Download [Participant_ID] Data"**
6. **Click "⬇️ Download [Participant_ID] Data (ZIP)"** when button appears
7. **Save the file**
   - Filename format: `participant_[UserID]_YYYYMMDD_HHMMSS.zip`
   - Example: `participant_P001_20260224_153045.zip`

#### Participant Information Display

Each participant entry shows:

```
👤 P001 - COMPLETED
  Session ID: P001_20260224_143022_abc123
  Created: 2026-02-24T14:30:22
  Current Stage: COMPLETED
  
  [📦 Download P001 Data]
```

#### Understanding Workflow Stages

Participants can be in various stages:

| Stage | Meaning | Data Available |
|-------|---------|----------------|
| **REGISTRATION** | Just started | Session only |
| **BIG5_ASSESSMENT** | Taking assessment | Session only |
| **TASK_SELECTION** | Choosing task | Session + Assessment |
| **TASK_DIALOGUE** | In conversation | Session + Assessment + Dialogue |
| **TASK_RESPONSE** | Submitting task response | Session + Assessment + Dialogue |
| **POST_SURVEY** | Taking survey | Session + Assessment + Dialogue + Task Response |
| **COMPLETED** | Finished | All data + Report |

**Note:** Only download data from participants at **COMPLETED** stage for complete datasets.

---

### Option 3: Export to CSV

#### When to Use
- **Statistical analysis** in Excel, SPSS, R, or Python
- **Quick overview** of all participants
- **Data visualization** preparation
- **Preliminary analysis** before detailed review

#### Step-by-Step Instructions

1. **Navigate to "Export to CSV" tab**
2. **Click "📊 Generate CSV"**
   - System compiles data from all participants
   - Takes 5-15 seconds
3. **Click "⬇️ Download CSV"** when button appears
4. **Save the file**
   - Filename format: `gerlach_research_data_YYYYMMDD_HHMMSS.csv`
   - Example: `gerlach_research_data_20260224_153045.csv`

#### CSV Column Structure

The CSV includes the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| **User ID** | Participant identifier | P001 |
| **Session ID** | Unique session identifier | P001_20260224_143022_abc123 |
| **Created At** | Session start timestamp | 2026-02-24T14:30:22 |
| **Current Stage** | Workflow completion status | COMPLETED |
| **Openness** | Big5 score (0-100) | 72.5 |
| **Conscientiousness** | Big5 score (0-100) | 65.0 |
| **Extraversion** | Big5 score (0-100) | 80.0 |
| **Agreeableness** | Big5 score (0-100) | 70.0 |
| **Neuroticism** | Big5 score (0-100) | 35.0 |
| **Gerlach Type** | Personality classification | role_model |
| **Gerlach Confidence** | Classification confidence | 85.5 |
| **Task Name** | Selected task | Noble Industries.pdf |
| **LLM Personality** | AI personality used | average |
| **Message Count** | Total dialogue messages | 24 |
| **Dialogue Duration** | Time in seconds | 1523 |
| **Survey Completed** | Survey status | Yes |

#### Using CSV in Analysis Software

**Excel:**
```
1. Open Excel
2. File → Open
3. Select CSV file
4. Data will auto-populate in columns
```

**SPSS:**
```
1. File → Import Data → CSV
2. Select file
3. Configure import settings
4. Click OK
```

**R:**
```r
# Load data
data <- read.csv("gerlach_research_data_20260224_153045.csv")

# View structure
str(data)

# Summary statistics
summary(data)

# Example analysis
cor(data[,c("Openness", "Conscientiousness", "Extraversion", 
            "Agreeableness", "Neuroticism")])
```

**Python (pandas):**
```python
import pandas as pd

# Load data
df = pd.read_csv("gerlach_research_data_20260224_153045.csv")

# View first rows
print(df.head())

# Descriptive statistics
print(df.describe())

# Example analysis
print(df.groupby('Gerlach Type')['Openness'].mean())
```

---

## Data File Structure

### Understanding JSON Files

All raw data is stored in JSON (JavaScript Object Notation) format. JSON is:
- Human-readable text format
- Structured with key-value pairs
- Easy to parse programmatically
- Standard for data exchange

### Session Files

**Location:** `sessions/`  
**Filename:** `[UserID]_[Date]_[Time]_[UniqueID].json`

**Purpose:** Master record linking all data for a participant

**Example Content:**
```json
{
  "user_id": "P001",
  "session_id": "P001_20260224_143022_abc123",
  "started_at": "2026-02-24T14:30:22",
  "ended_at": "2026-02-24T15:45:30",
  "current_stage": "COMPLETED",
  "completed_stages": [
    "REGISTRATION",
    "BIG5_ASSESSMENT",
    "TASK_SELECTION",
    "TASK_DIALOGUE",
    "TASK_RESPONSE",
    "POST_SURVEY"
  ],
  "big5_assessment_id": "assessment_P001_xyz789",
  "dialogue_records": ["dialogue_P001_abc456"],
  "task_response_id": "noble_P001_ghi012",
  "survey_id": "survey_P001_mno678",
  "report_id": "report_P001_20260224_143022_abc123",
  "metadata": {
    "consent_given": true,
    "start_time": "2026-02-24T14:30:22"
  }
}
```

**Key Fields:**
- `session_id` - Unique identifier for this session
- `current_stage` - Where participant is in workflow
- `*_id` fields - Links to other data files
- `completed_stages` - Array of finished stages

### Assessment Files

**Location:** `assessments/`  
**Filename:** `assessment_[UserID]_[UniqueID].json`

**Purpose:** Big Five personality assessment results

**Example Content:**
```json
{
  "assessment_id": "assessment_P001_xyz789",
  "user_id": "P001",
  "session_id": "P001_20260224_143022_abc123",
  "conducted_at": "2026-02-24T14:35:10",
  "openness": 72.5,
  "conscientiousness": 65.0,
  "extraversion": 80.0,
  "agreeableness": 70.0,
  "neuroticism": 35.0,
  "gerlach_type": "role_model",
  "gerlach_confidence": 85.5,
  "responses": {
    "E1": 5,
    "E2": 2,
    "E3": 5,
    ...
    "O10": 4
  },
  "metadata": {}
}
```

**Key Fields:**
- Big5 trait scores (0-100 scale)
- `gerlach_type` - Personality classification
- `responses` - All 50 item responses (1-5 scale)

**Gerlach Types:**
- `average` - Balanced across traits
- `role_model` - Low N, High E/O/A/C
- `self_centred` - Low O/A/C
- `reserved` - Low N/O

### Dialogue Files

**Location:** `dialogues/`  
**Filename:** `dialogue_[UserID]_[UniqueID].json`

**Purpose:** Complete conversation transcript

**Example Content:**
```json
{
  "dialogue_id": "dialogue_P001_abc456",
  "user_id": "P001",
  "session_id": "P001_20260224_143022_abc123",
  "task_name": "Noble Industries.pdf",
  "llm_personality": "average",
  "started_at": "2026-02-24T14:40:00",
  "ended_at": "2026-02-24T15:05:23",
  "duration_seconds": 1523,
  "total_messages": 24,
  "messages": [
    {
      "message_id": "msg_001",
      "timestamp": "2026-02-24T14:40:05",
      "role": "assistant",
      "content": "Hello! I'm here to help you with this task..."
    },
    {
      "message_id": "msg_002",
      "timestamp": "2026-02-24T14:40:32",
      "role": "user",
      "content": "Let's start by reviewing the candidates..."
    },
    ...
  ]
}
```

**Key Fields:**
- `messages` - Array of all conversation turns
- `role` - Either "user" or "assistant"
- `duration_seconds` - Total conversation time
- `total_messages` - Count of exchanges

### Task Response Files

**Location:** `task_responses/noble/` or `task_responses/popcorn/`  
**Filename:** `[TaskType]_[UserID]_[UniqueID].json`

**Purpose:** Task-specific participant responses

#### Noble Industries Task

**Example Content:**
```json
{
  "task_response_id": "noble_P001_ghi012",
  "user_id": "P001",
  "session_id": "P001_20260224_143022_abc123",
  "dialogue_id": "dialogue_P001_abc456",
  "task_name": "Noble Industries",
  "submitted_at": "2026-02-24T15:06:15",
  "rankings": [
    {
      "rank": 1,
      "candidate": "Candidate A",
      "rationale": "Strong leadership experience and proven track record..."
    },
    {
      "rank": 2,
      "candidate": "Candidate B",
      "rationale": "Excellent technical skills but limited management..."
    },
    ...
  ]
}
```

#### Popcorn Brain Task

**Example Content:**
```json
{
  "task_response_id": "popcorn_P002_jkl345",
  "user_id": "P002",
  "session_id": "P002_20260224_150315_def456",
  "dialogue_id": "dialogue_P002_def789",
  "task_name": "Popcorn Brain",
  "submitted_at": "2026-02-24T15:25:40",
  "self_assessment": {
    "originality": 6,
    "flexibility": 5,
    "elaboration": 7,
    "fluency": 6
  },
  "computed_metrics": {
    "unique_ideas_count": 12,
    "alternative_approaches_count": 4,
    "detail_instances": 18,
    "ideas_per_minute": 0.47
  }
}
```

**Key Fields:**
- Noble: `rankings` with rationales
- Popcorn: `self_assessment` (1-7 scale) + `computed_metrics`

### Survey Files

**Location:** `surveys/`  
**Filename:** `survey_[UserID]_[UniqueID].json`

**Purpose:** Post-experiment survey responses

**Example Content:**
```json
{
  "survey_id": "survey_P001_mno678",
  "user_id": "P001",
  "session_id": "P001_20260224_143022_abc123",
  "dialogue_id": "dialogue_P001_abc456",
  "submitted_at": "2026-02-24T15:40:20",
  "likert_responses": {
    "q1_llm_helpful": 6,
    "q2_llm_understanding": 7,
    "q3_task_difficulty": 4,
    ...
    "q31_overall_satisfaction": 6
  },
  "open_responses": {
    "q32_liked_most": "The AI was very responsive and helped me think through...",
    "q33_challenges": "Initially unclear about the task requirements...",
    "q34_llm_influence": "The AI helped me consider perspectives I hadn't...",
    "q35_use_again": "Yes, it was helpful for brainstorming...",
    "q36_suggestions": "Maybe add more examples upfront...",
    "q37_additional": "Overall great experience!"
  }
}
```

**Key Fields:**
- `likert_responses` - 31 questions on 1-7 scale
- `open_responses` - 6 text responses

### Report Files

**Location:** `reports/`  
**Filename:** `report_[SessionID].md` or `.html`

**Purpose:** Human-readable comprehensive summary

**Formats:**
- **Markdown (.md)** - Plain text, easy to read/edit
- **HTML (.html)** - Formatted, viewable in browser

**Content Includes:**
- Participant summary
- Big5 personality profile
- Complete dialogue transcript
- Task-specific results
- Survey responses
- Performance analytics

---

## Data Analysis Workflow

### Recommended Analysis Pipeline

#### Phase 1: Data Collection & Backup

**During Active Data Collection:**

1. **Weekly Downloads**
   - Download all data every Friday
   - Save with date-stamped filename
   - Store in secure backup location

2. **Quality Checks**
   - Review participant count
   - Check for incomplete sessions
   - Verify data completeness

3. **Backup Strategy**
   - Keep 3 copies (local, external drive, cloud)
   - Organize by week/date
   - Document any issues

#### Phase 2: Data Preparation

**After Data Collection Completes:**

1. **Final Download**
   ```
   - Download all data (ZIP)
   - Export to CSV
   - Verify all expected participants present
   ```

2. **Data Cleaning**
   ```
   - Remove test sessions
   - Identify incomplete sessions
   - Check for duplicates
   - Verify data integrity
   ```

3. **Data Organization**
   ```
   Create folder structure:
   
   Final_Dataset/
   ├── raw_data/
   │   └── gerlach_research_data_final.zip
   ├── csv_export/
   │   └── gerlach_research_data_final.csv
   ├── processed/
   │   └── (cleaned datasets)
   └── analysis/
       └── (analysis scripts and results)
   ```

#### Phase 3: Descriptive Analysis

**Using CSV Export:**

1. **Load Data**
   - Import CSV into your preferred software
   - Verify all columns present
   - Check data types

2. **Descriptive Statistics**
   ```
   Calculate for Big5 traits:
   - Mean, SD, Min, Max
   - Distribution (histograms)
   - Correlations between traits
   ```

3. **Group Comparisons**
   ```
   Compare by:
   - Gerlach personality type
   - Task type (Noble vs Popcorn)
   - LLM personality used
   ```

4. **Dialogue Metrics**
   ```
   Analyze:
   - Message count distribution
   - Dialogue duration
   - Patterns by personality type
   ```

#### Phase 4: Advanced Analysis

**Using JSON Files:**

1. **Dialogue Content Analysis**
   ```python
   # Example: Extract all user messages
   import json
   
   with open('dialogue_P001_abc456.json') as f:
       dialogue = json.load(f)
   
   user_messages = [
       msg['content'] 
       for msg in dialogue['messages'] 
       if msg['role'] == 'user'
   ]
   ```

2. **Task-Specific Analysis**
   ```python
   # Noble Industries: Analyze ranking patterns
   # Popcorn Brain: Compare self vs computed creativity
   ```

3. **Survey Text Analysis**
   ```python
   # Qualitative coding of open-ended responses
   # Sentiment analysis
   # Theme extraction
   ```

#### Phase 5: Statistical Testing

**Example Research Questions:**

1. **Personality & Task Performance**
   ```
   Q: Do Big5 traits predict task performance?
   Analysis: Regression analysis
   DV: Task performance metrics
   IV: Big5 scores
   ```

2. **LLM Personality Effects**
   ```
   Q: Does LLM personality affect user satisfaction?
   Analysis: ANOVA
   DV: Survey satisfaction scores
   IV: LLM personality type (4 levels)
   ```

3. **Gerlach Type Differences**
   ```
   Q: Do Gerlach types differ in dialogue patterns?
   Analysis: MANOVA
   DV: Message count, duration, creativity metrics
   IV: Gerlach type (4 levels)
   ```

### Sample Analysis Scripts

#### R Example: Basic Descriptive Statistics

```r
# Load data
library(tidyverse)
data <- read_csv("gerlach_research_data_final.csv")

# Descriptive statistics for Big5
big5_traits <- c("Openness", "Conscientiousness", "Extraversion", 
                 "Agreeableness", "Neuroticism")

data %>%
  select(all_of(big5_traits)) %>%
  summary()

# Correlation matrix
cor_matrix <- cor(data[, big5_traits], use = "complete.obs")
print(cor_matrix)

# Visualize distributions
data %>%
  pivot_longer(cols = all_of(big5_traits), 
               names_to = "Trait", 
               values_to = "Score") %>%
  ggplot(aes(x = Score, fill = Trait)) +
  geom_histogram(bins = 20) +
  facet_wrap(~Trait) +
  theme_minimal() +
  labs(title = "Big5 Trait Distributions")

# Compare by Gerlach type
data %>%
  group_by(`Gerlach Type`) %>%
  summarise(across(all_of(big5_traits), mean, na.rm = TRUE))
```

#### Python Example: Advanced Analysis

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load data
df = pd.read_csv("gerlach_research_data_final.csv")

# Descriptive statistics
print(df.describe())

# Big5 correlations
big5_cols = ['Openness', 'Conscientiousness', 'Extraversion', 
             'Agreeableness', 'Neuroticism']
correlation_matrix = df[big5_cols].corr()

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Big5 Trait Correlations')
plt.tight_layout()
plt.savefig('big5_correlations.png')

# Compare dialogue metrics by Gerlach type
gerlach_groups = df.groupby('Gerlach Type')['Message Count'].describe()
print(gerlach_groups)

# ANOVA: LLM personality effect on satisfaction
# (Assuming satisfaction is in survey data)
groups = [df[df['LLM Personality'] == p]['Survey Completed'] 
          for p in df['LLM Personality'].unique()]
f_stat, p_value = stats.f_oneway(*groups)
print(f"F-statistic: {f_stat}, p-value: {p_value}")
```

---

## Monitoring Study Progress

### Real-Time Monitoring

#### Checking Participant Count

1. Log in to admin dashboard
2. Go to "Download All Data" tab
3. View **"Total Participants"** metric at top

**Interpretation:**
- Shows all sessions (complete and incomplete)
- Compare to expected recruitment target
- Monitor daily/weekly progress

#### Reviewing Recent Participants

1. Go to "Download by Participant" tab
2. Scroll through participant list
3. Check "Current Stage" for each

**What to Look For:**
- Participants stuck at early stages (may need follow-up)
- Recent completions (COMPLETED status)
- Unusual patterns (very short sessions)

### Weekly Progress Reports

**Create a simple tracking spreadsheet:**

| Week | Date | Total Participants | Completed | In Progress | Notes |
|------|------|-------------------|-----------|-------------|-------|
| 1 | 2/24 | 5 | 3 | 2 | Good start |
| 2 | 3/3 | 12 | 10 | 2 | On track |
| 3 | 3/10 | 20 | 18 | 2 | Target met |

**Steps:**
1. Download CSV export weekly
2. Count participants by status
3. Document in tracking sheet
4. Note any issues or patterns

### Identifying Issues

#### Incomplete Sessions

**Problem:** Participants not finishing

**How to Identify:**
- Check "Current Stage" in participant list
- Look for sessions stuck at early stages
- Review session timestamps (old incomplete sessions)

**Possible Causes:**
- Technical issues
- Participant dropout
- Unclear instructions
- Time constraints

**Actions:**
- Review participant feedback
- Check for error patterns
- Consider follow-up with participants
- Adjust recruitment if needed

#### Data Quality Concerns

**Red Flags:**
- Very short dialogue durations (<5 minutes)
- Minimal message counts (<10 messages)
- Identical responses across participants
- Missing data in completed sessions

**Quality Check Process:**
1. Download individual participant data
2. Review dialogue transcript
3. Check task responses for completeness
4. Verify survey responses are thoughtful

### Recruitment Tracking

**Monitor:**
- Recruitment rate (participants per week)
- Completion rate (completed / started)
- Dropout points (where participants stop)
- Time to completion (average session duration)

**Adjust Strategy:**
- If low recruitment: Increase outreach
- If high dropout: Simplify process
- If quality issues: Improve instructions
- If technical problems: Check system logs

---

## Data Management Best Practices

### Backup Strategy

#### The 3-2-1 Rule

**3** copies of your data  
**2** different storage media  
**1** off-site backup

**Example Implementation:**

1. **Primary Copy:** Streamlit Cloud (automatic)
2. **Local Backup:** Weekly download to encrypted external drive
3. **Cloud Backup:** Monthly upload to Google Drive/Dropbox

#### Backup Schedule

**During Active Data Collection:**

| Frequency | Action | Storage |
|-----------|--------|---------|
| **Daily** | Check participant count | N/A |
| **Weekly** | Download all data (ZIP) | External drive |
| **Monthly** | Upload to cloud storage | Google Drive |
| **End of study** | Final complete download | Multiple locations |

**Backup Checklist:**
- [ ] Download all data as ZIP
- [ ] Export to CSV
- [ ] Verify files open correctly
- [ ] Save with date-stamped filename
- [ ] Store in multiple locations
- [ ] Test restore process periodically

### File Organization

#### Recommended Folder Structure

```
Gerlach_Research_Project/
│
├── 01_Documentation/
│   ├── IRB_Approval.pdf
│   ├── Study_Protocol.pdf
│   ├── Administrator_Guide.pdf
│   └── Participant_Instructions.pdf
│
├── 02_Data_Collection/
│   ├── Week_01/
│   │   └── gerlach_research_data_20260224.zip
│   ├── Week_02/
│   │   └── gerlach_research_data_20260303.zip
│   └── Week_03/
│       └── gerlach_research_data_20260310.zip
│
├── 03_Final_Dataset/
│   ├── raw_data/
│   │   ├── gerlach_research_data_final.zip
│   │   └── gerlach_research_data_final.csv
│   ├── processed_data/
│   │   └── cleaned_dataset.csv
│   └── codebook.xlsx
│
├── 04_Analysis/
│   ├── scripts/
│   │   ├── descriptive_stats.R
│   │   └── main_analysis.py
│   ├── results/
│   │   ├── tables/
│   │   └── figures/
│   └── reports/
│       └── preliminary_findings.docx
│
└── 05_Publications/
    ├── manuscript_draft.docx
    └── supplementary_materials/
```

#### File Naming Conventions

**Use consistent, descriptive names:**

✅ **Good:**
- `gerlach_data_20260224_backup.zip`
- `big5_descriptives_final.csv`
- `dialogue_analysis_v2.R`

❌ **Bad:**
- `data.zip`
- `backup_new.csv`
- `analysis_final_FINAL_v3.R`

**Best Practices:**
- Include dates (YYYYMMDD format)
- Use underscores, not spaces
- Be descriptive but concise
- Version control for scripts (v1, v2, etc.)

### Data Security

#### Encryption

**For Sensitive Data:**
- Encrypt external drives (BitLocker, FileVault)
- Use encrypted cloud storage
- Password-protect ZIP files if sharing

**How to Password-Protect ZIP:**

**Windows:**
```
1. Right-click ZIP file
2. Select "7-Zip" → "Add to archive"
3. Enter password in "Encryption" section
4. Choose AES-256 encryption
5. Click OK
```

**Mac:**
```
1. Open Terminal
2. Type: zip -er protected.zip original.zip
3. Enter password when prompted
```

#### Access Control

**Who Should Have Access:**
- Principal Investigator (full access)
- Research Coordinators (download access)
- Data Analysts (processed data only)
- Students/RAs (supervised access)

**Admin Password Management:**
- Share only with authorized personnel
- Change if compromised
- Document who has access
- Revoke access when team members leave

#### Data Retention

**Follow Institutional Guidelines:**
- Typically 5-7 years after publication
- Check IRB requirements
- Document retention schedule
- Plan for secure deletion after retention period

### Version Control

#### For Analysis Scripts

**Use Git for Code:**
```bash
# Initialize repository
git init

# Track changes
git add analysis_script.R
git commit -m "Added descriptive statistics"

# Create versions
git tag v1.0
```

#### For Data Files

**Document Changes:**
- Keep changelog file
- Note any data cleaning steps
- Record exclusions/modifications
- Maintain original raw data

**Example Changelog:**
```
Data Changelog - Gerlach Research Project

2026-02-24: Initial data collection started
2026-03-10: Removed 2 test sessions (P_TEST_001, P_TEST_002)
2026-03-15: Identified 1 incomplete session (P015) - excluded from analysis
2026-03-20: Final dataset locked for analysis (N=48)
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: Cannot Access Admin Dashboard

**Symptoms:**
- Login button not responding
- Password not accepted
- Page not loading

**Solutions:**

1. **Verify URL**
   - Ensure you're at the correct app URL
   - Check for typos in address

2. **Check Password**
   - Password: `Big5llmstudy` (case-sensitive)
   - No spaces before/after
   - Try copying and pasting

3. **Clear Browser Cache**
   ```
   Chrome: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
   Firefox: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
   Safari: Cmd+Option+E
   ```

4. **Try Different Browser**
   - Test in Chrome, Firefox, or Edge
   - Disable browser extensions

5. **Check Internet Connection**
   - Verify you're online
   - Try accessing other websites

#### Issue 2: Download Button Not Working

**Symptoms:**
- Click download but nothing happens
- ZIP file not created
- Error message appears

**Solutions:**

1. **Wait for Processing**
   - Large datasets take time (10-30 seconds)
   - Look for "Creating ZIP file..." message
   - Don't click multiple times

2. **Check Browser Settings**
   - Allow pop-ups from your app domain
   - Check download folder permissions
   - Disable download blockers

3. **Try Smaller Download**
   - Download individual participant instead of all
   - Export CSV instead of ZIP

4. **Refresh Page**
   - Reload the admin dashboard
   - Log out and log back in

5. **Check Available Disk Space**
   - Ensure enough space on your computer
   - Clear temporary files if needed

#### Issue 3: ZIP File Won't Open

**Symptoms:**
- "Archive is corrupted" error
- Can't extract files
- Empty ZIP file

**Solutions:**

1. **Re-download File**
   - Delete corrupted file
   - Download again from admin dashboard

2. **Try Different Extraction Tool**
   - Windows: 7-Zip, WinRAR
   - Mac: The Unarchiver, Keka
   - Built-in tools may have issues

3. **Check File Size**
   - If 0 KB, download failed
   - Should be >1 KB minimum

4. **Verify Download Completed**
   - Don't interrupt download
   - Wait for "Download complete" confirmation

#### Issue 4: CSV Opens with Garbled Text

**Symptoms:**
- Special characters display incorrectly
- Columns misaligned
- Data looks corrupted

**Solutions:**

1. **Set Correct Encoding**
   - Open with UTF-8 encoding
   - In Excel: Data → From Text/CSV → UTF-8

2. **Use Proper Import**
   ```
   Excel:
   1. Data → From Text/CSV
   2. Select file
   3. Choose "UTF-8" encoding
   4. Click "Load"
   ```

3. **Try Different Software**
   - Google Sheets (auto-detects encoding)
   - LibreOffice Calc
   - Text editor (Notepad++, VS Code)

#### Issue 5: Missing Participant Data

**Symptoms:**
- Expected participant not in list
- Participant count lower than expected
- Data files missing

**Solutions:**

1. **Check Workflow Stage**
   - Participant may not have completed registration
   - Data only saved after each stage completion

2. **Verify Participant ID**
   - Check for typos in ID
   - Search for similar IDs

3. **Check Session Status**
   - Look in "Download by Participant" tab
   - May be listed under different stage

4. **Review Streamlit Logs**
   - Access Streamlit Cloud dashboard
   - Check for error messages
   - Look for failed saves

5. **Contact Technical Support**
   - If data truly missing
   - Provide participant ID and timestamp

#### Issue 6: Slow Performance

**Symptoms:**
- Admin dashboard loads slowly
- Download takes very long
- Page freezes

**Solutions:**

1. **Check Data Volume**
   - Large datasets (>100 participants) take longer
   - Consider downloading in batches

2. **Optimize Browser**
   - Close unnecessary tabs
   - Clear cache and cookies
   - Update browser to latest version

3. **Check Internet Speed**
   - Test connection speed
   - Use wired connection if possible
   - Avoid peak usage times

4. **Download During Off-Hours**
   - Late evening or early morning
   - Less server load

### Getting Help

#### Self-Help Resources

1. **This Manual**
   - Search for your specific issue
   - Review relevant sections

2. **Streamlit Documentation**
   - https://docs.streamlit.io/
   - Community forum

3. **GitHub Repository**
   - Check for known issues
   - Review code documentation

#### Contacting Support

**Before Contacting:**
- [ ] Reviewed troubleshooting section
- [ ] Tried basic solutions (refresh, different browser)
- [ ] Documented the issue (screenshots, error messages)
- [ ] Noted when issue started

**Information to Provide:**
- Your app URL
- Browser and version
- Operating system
- Exact error message
- Steps to reproduce issue
- Screenshots if applicable

**Support Channels:**
- Technical administrator
- Principal investigator
- Streamlit support (for platform issues)

---

## Security and Privacy

### Data Protection Measures

#### What Data is Collected

**Participant Data:**
- ✅ Participant ID (anonymous)
- ✅ Session timestamps
- ✅ Big5 assessment responses
- ✅ Dialogue transcripts
- ✅ Task responses
- ✅ Survey responses

**NOT Collected:**
- ❌ Names
- ❌ Email addresses
- ❌ IP addresses
- ❌ Location data
- ❌ Device information
- ❌ Any personal identifying information

#### Anonymization

**Participant IDs:**
- Use anonymous codes (P001, KOREA_042, etc.)
- No connection to personal information
- Assigned by researcher, not system

**Data Linking:**
- All data linked by participant ID only
- No external identifiers stored
- Session IDs are random (UUID-based)

#### Access Control

**Admin Dashboard:**
- Password-protected
- Single password for all admins
- No user accounts or tracking
- Session-based authentication

**Data Storage:**
- Stored on Streamlit Cloud servers
- Encrypted in transit (HTTPS)
- Access only through admin dashboard
- No public access to data files

#### Compliance

**IRB Requirements:**
- Ensure data collection approved
- Follow institutional guidelines
- Maintain consent records separately
- Report any data breaches

**GDPR Considerations (if applicable):**
- Participants have right to data deletion
- Provide data export on request
- Document data retention policy
- Maintain data processing records

### Best Practices for Administrators

#### Do's

✅ **Change password if compromised**
✅ **Log out after each session**
✅ **Use secure internet connections**
✅ **Encrypt backups**
✅ **Limit access to authorized personnel**
✅ **Keep software updated**
✅ **Document data handling procedures**
✅ **Regular security audits**

#### Don'ts

❌ **Share password publicly**
❌ **Access on public computers without logging out**
❌ **Store unencrypted data on USB drives**
❌ **Email raw data files**
❌ **Share data with unauthorized persons**
❌ **Leave admin dashboard open unattended**
❌ **Use weak passwords for backups**

### Data Breach Response

**If Data Breach Suspected:**

1. **Immediate Actions**
   - Change admin password
   - Log out all sessions
   - Document the incident

2. **Assessment**
   - Determine what data was accessed
   - Identify how breach occurred
   - Assess impact on participants

3. **Notification**
   - Inform IRB immediately
   - Follow institutional breach protocol
   - Notify participants if required

4. **Remediation**
   - Fix security vulnerability
   - Implement additional safeguards
   - Review and update security procedures

5. **Documentation**
   - Complete incident report
   - Document all actions taken
   - Update security policies

---

## Appendix

### A. Quick Reference Guide

#### Admin Access
- **URL:** Your Streamlit app URL
- **Password:** `Big5llmstudy`
- **Location:** Sidebar → Admin Tools → Admin Download Center

#### Download Options
| Option | Best For | File Format |
|--------|----------|-------------|
| Download All Data | Complete backups | ZIP |
| Download by Participant | Individual review | ZIP |
| Export to CSV | Statistical analysis | CSV |

#### File Locations in ZIP
- Sessions: `sessions/`
- Assessments: `assessments/`
- Dialogues: `dialogues/`
- Task Responses: `task_responses/noble/` or `/popcorn/`
- Surveys: `surveys/`
- Reports: `reports/`

### B. Workflow Stages Reference

| Stage | Code | Description |
|-------|------|-------------|
| Registration | `REGISTRATION` | Initial signup |
| Assessment | `BIG5_ASSESSMENT` | Taking personality test |
| Task Selection | `TASK_SELECTION` | Choosing task & LLM |
| Dialogue | `TASK_DIALOGUE` | Conversing with AI |
| Task Response | `TASK_RESPONSE` | Submitting task answers |
| Survey | `POST_SURVEY` | Post-experiment survey |
| Completed | `COMPLETED` | All stages finished |

### C. Big5 Traits Reference

| Trait | Low Score Indicates | High Score Indicates |
|-------|---------------------|----------------------|
| **Openness** | Conventional, practical | Creative, curious |
| **Conscientiousness** | Spontaneous, flexible | Organized, disciplined |
| **Extraversion** | Reserved, quiet | Outgoing, energetic |
| **Agreeableness** | Competitive, skeptical | Cooperative, trusting |
| **Neuroticism** | Calm, stable | Anxious, emotional |

### D. Gerlach Types Reference

| Type | Characteristics | Big5 Pattern |
|------|----------------|--------------|
| **Average** | Balanced across all traits | All traits near 50 |
| **Role Model** | Stable, organized, outgoing | Low N, High E/O/A/C |
| **Self-Centred** | Competitive, less agreeable | Low O/A/C |
| **Reserved** | Calm, conventional, introverted | Low N/O |

### E. LLM Personalities Reference

| Personality | Emoji | Characteristics |
|-------------|-------|-----------------|
| **Average** | ⚖️ | Balanced & Practical |
| **Role Model** | ⭐ | Optimistic & Organized |
| **Self-Centred** | 🎯 | Direct & Competitive |
| **Reserved** | 🤫 | Calm & Conventional |

### F. CSV Column Reference

| Column Name | Data Type | Range/Values | Description |
|-------------|-----------|--------------|-------------|
| User ID | String | - | Participant identifier |
| Session ID | String | - | Unique session ID |
| Created At | DateTime | ISO 8601 | Session start time |
| Current Stage | String | Workflow stages | Completion status |
| Openness | Float | 0-100 | Big5 trait score |
| Conscientiousness | Float | 0-100 | Big5 trait score |
| Extraversion | Float | 0-100 | Big5 trait score |
| Agreeableness | Float | 0-100 | Big5 trait score |
| Neuroticism | Float | 0-100 | Big5 trait score |
| Gerlach Type | String | 4 types | Personality classification |
| Gerlach Confidence | Float | 0-100 | Classification confidence |
| Task Name | String | - | Selected task file |
| LLM Personality | String | 4 types | AI personality used |
| Message Count | Integer | ≥0 | Total dialogue messages |
| Dialogue Duration | Integer | Seconds | Conversation length |
| Survey Completed | String | Yes/No | Survey status |

### G. Keyboard Shortcuts

**Browser:**
- `Ctrl/Cmd + R` - Refresh page
- `Ctrl/Cmd + Shift + R` - Hard refresh (clear cache)
- `Ctrl/Cmd + F` - Find on page
- `Ctrl/Cmd + +/-` - Zoom in/out

**Admin Dashboard:**
- Click sidebar button to access
- Use tabs to navigate sections
- Download buttons appear after processing

### H. Contact Information

**For Technical Issues:**
- System Administrator: [Contact info]
- Streamlit Support: https://discuss.streamlit.io/

**For Research Questions:**
- Principal Investigator: [Contact info]
- Research Coordinator: [Contact info]

**For IRB/Ethics:**
- Institutional Review Board: [Contact info]

### I. Glossary

**API Key** - Authentication credential for Anthropic Claude AI service

**Big5** - Five-factor model of personality (OCEAN)

**CSV** - Comma-Separated Values, spreadsheet file format

**Dialogue** - Conversation between participant and AI

**Gerlach Types** - Four personality classifications from Gerlach et al. (2018)

**IPIP-50** - International Personality Item Pool, 50-item Big5 inventory

**JSON** - JavaScript Object Notation, data storage format

**LLM** - Large Language Model (AI system)

**Session** - Single participant's complete study experience

**Streamlit** - Web application framework hosting the platform

**UUID** - Universally Unique Identifier, random ID generation

**Workflow Stage** - Current step in the research process

**ZIP** - Compressed archive file format

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-24 | Initial release | System |

---

## Feedback & Improvements

This manual is a living document. If you:
- Find errors or unclear sections
- Have suggestions for improvements
- Discover new issues or solutions
- Need additional topics covered

Please document your feedback and share with the research team for future updates.

---

**End of Administrator User Guide**

For additional support, refer to the technical documentation or contact your system administrator.
