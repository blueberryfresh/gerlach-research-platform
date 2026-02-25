# Admin Download Guide - Simplified

## Overview
This guide explains how to use the **Admin Download Center** to retrieve participant data from your Gerlach Research Platform.

**No email setup required** - Simply log in periodically to download data manually.

---

## 🔐 Accessing the Admin Dashboard

### Password
**`Big5llmstudy`**

### How to Access
1. Go to your Streamlit app URL
2. Navigate to the **Admin Download Center** page
3. Enter the password
4. Click "Login"

---

## 📥 Three Ways to Download Data

### 1. Download All Data (ZIP)

**Best for:** Regular backups, end-of-study data collection

**Steps:**
1. Go to "Download All Data" tab
2. See total participant count
3. Click "📦 Create ZIP File"
4. Click "⬇️ Download All Data (ZIP)"
5. Save file: `gerlach_research_data_YYYYMMDD_HHMMSS.zip`

**ZIP Contains:**
```
gerlach_research_data_20260224_143022.zip
├── sessions/          (all session metadata)
├── assessments/       (all Big5 assessments)
├── dialogues/         (all conversation transcripts)
├── task_responses/    (all rankings/creativity data)
│   ├── noble/
│   └── popcorn/
├── surveys/           (all survey responses)
└── reports/           (all generated reports - .md and .html)
```

---

### 2. Download Individual Participant

**Best for:** Checking specific participant data, troubleshooting

**Steps:**
1. Go to "Download by Participant" tab
2. Browse the list of participants
3. Expand a participant's section to see details:
   - Session ID
   - Created timestamp
   - Current stage
4. Click "📦 Download [Participant_ID] Data"
5. Click "⬇️ Download [Participant_ID] Data (ZIP)"
6. Save file: `participant_P001_YYYYMMDD_HHMMSS.zip`

**Contains:** All data files for that specific participant

---

### 3. Export to CSV

**Best for:** Statistical analysis in Excel, SPSS, R, Python

**Steps:**
1. Go to "Export to CSV" tab
2. Click "📊 Generate CSV"
3. Click "⬇️ Download CSV"
4. Save file: `gerlach_research_data_YYYYMMDD_HHMMSS.csv`

**CSV Columns:**
- User ID, Session ID, Created At, Current Stage
- Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- Gerlach Type, Gerlach Confidence
- Task Name, LLM Personality
- Message Count, Dialogue Duration
- Survey Completed

**Use in:**
- **Excel:** Open directly for viewing/basic analysis
- **SPSS:** Import as CSV for statistical tests
- **R:** `read.csv("filename.csv")`
- **Python:** `pd.read_csv("filename.csv")`

---

## 📊 Understanding the Data Files

### Session Files (`sessions/`)
**File:** `P001_20260224_143022_abc123.json`

**Contains:**
- Participant ID
- Session ID
- Timestamps (started, ended)
- Current workflow stage
- Task and LLM personality selections
- Links to all other data files (assessment_id, dialogue_id, etc.)

### Assessment Files (`assessments/`)
**File:** `assessment_P001_xyz789.json`

**Contains:**
- All 50 IPIP-50 item responses (1-5 scale)
- Big5 trait scores (0-100 scale)
- Gerlach personality type
- Confidence score

### Dialogue Files (`dialogues/`)
**File:** `dialogue_P001_abc456.json`

**Contains:**
- Complete conversation transcript
- Each message with timestamp and role (user/assistant)
- Total message count
- Dialogue duration in seconds

### Task Response Files (`task_responses/`)

**Noble Industries:** `noble/noble_P001_def789.json`
- Rankings for all 5 candidates (1-5)
- Rationale for each ranking

**Popcorn Brain:** `popcorn/popcorn_P001_ghi012.json`
- Self-assessment ratings (1-7 scale) for 4 dimensions
- Computed creativity metrics from dialogue

### Survey Files (`surveys/`)
**File:** `survey_P001_jkl345.json`

**Contains:**
- 31 Likert scale responses (1-7)
- 6 open-ended text responses

### Report Files (`reports/`)
**Files:** 
- `report_P001_20260224_143022_abc123.md` (Markdown)
- `report_P001_20260224_143022_abc123.html` (HTML)

**Contains:**
- Complete summary of all participant data
- Big5 profile
- Dialogue transcript
- Task-specific results
- Survey responses

---

## 🗓️ Recommended Download Schedule

### During Data Collection

**Daily (if active participants):**
- Check participant count in admin dashboard
- No download needed unless you want to review specific data

**Weekly:**
- Download all data as backup
- Store in secure location (encrypted drive, cloud storage)

**After Each Participant:**
- Review their HTML report for quality check
- Verify data completeness

### End of Study

**Final Download:**
1. Download all data (ZIP)
2. Export to CSV for analysis
3. Backup to multiple locations
4. Verify all expected participants are present

---

## 🔍 Data Quality Checks

### What to Check

**1. Participant Count**
- Verify expected number of participants
- Check for any missing participant IDs

**2. Workflow Completion**
- In CSV export, check "Current Stage" column
- All should show "COMPLETED" for finished participants

**3. Data Completeness**
- Each participant should have:
  - ✅ Session file
  - ✅ Assessment file
  - ✅ Dialogue file
  - ✅ Task response file
  - ✅ Survey file
  - ✅ Report files (MD + HTML)

**4. Dialogue Quality**
- Review message counts (should be reasonable, not too short)
- Check dialogue duration (should align with task complexity)

---

## 💾 Data Storage Best Practices

### Backup Strategy

**3-2-1 Rule:**
- **3** copies of your data
- **2** different storage media
- **1** off-site backup

**Example:**
1. Original on Streamlit Cloud (automatic)
2. Weekly download to local encrypted drive
3. Monthly backup to cloud storage (Google Drive, Dropbox)

### File Organization

```
Research_Data_Backups/
├── 2026-02-24_Week1/
│   └── gerlach_research_data_20260224_143022.zip
├── 2026-03-03_Week2/
│   └── gerlach_research_data_20260303_143022.zip
├── 2026-03-10_Week3/
│   └── gerlach_research_data_20260310_143022.zip
└── Final_Dataset/
    ├── gerlach_research_data_final.zip
    └── gerlach_research_data_final.csv
```

### Security

- **Encrypt backups** if storing on cloud or external drives
- **Password protect** ZIP files if sharing with collaborators
- **Limit access** to only authorized researchers
- **Delete test data** before final analysis

---

## 📊 Data Analysis Workflow

### Step 1: Download Data
- Use "Download All Data" for complete dataset
- Use "Export to CSV" for quick analysis

### Step 2: Extract and Organize
- Unzip the downloaded file
- Organize by participant or data type

### Step 3: Load into Analysis Software

**Excel:**
```
File → Open → Select CSV file
```

**R:**
```r
data <- read.csv("gerlach_research_data_20260224_143022.csv")
summary(data)
```

**Python:**
```python
import pandas as pd
data = pd.read_csv("gerlach_research_data_20260224_143022.csv")
data.head()
```

**SPSS:**
```
File → Import Data → CSV → Select file
```

### Step 4: Analyze
- Big5 correlations with task performance
- Gerlach type differences in dialogue patterns
- LLM personality effects on user satisfaction
- Task-specific analyses (rankings, creativity metrics)

---

## 🛠️ Troubleshooting

### Can't Log In to Admin Dashboard

**Problem:** Password not working

**Solution:**
- Verify password: `Big5llmstudy` (case-sensitive)
- Clear browser cache and try again
- Try a different browser

### No Participants Showing

**Problem:** Participant list is empty

**Solution:**
- Verify that participants have actually started the study
- Check that `research_data/sessions/` folder exists on Streamlit Cloud
- Review Streamlit logs for errors

### Download Button Not Working

**Problem:** ZIP download fails

**Solution:**
- Check browser console for errors
- Try a different browser
- Verify data files exist in `research_data/` folder
- Check Streamlit Cloud storage limits

### CSV Export Empty

**Problem:** CSV has headers but no data

**Solution:**
- Verify session files exist
- Check JSON file format (may be corrupted)
- Review Streamlit logs for parsing errors

### ZIP File Won't Open

**Problem:** Downloaded ZIP is corrupted

**Solution:**
- Re-download the file
- Try a different ZIP extraction tool
- Check available disk space

---

## 🔒 Security & Privacy

### What's Stored

**Anonymous Data Only:**
- ✅ Participant IDs (e.g., P001, KOREA_042)
- ✅ Session IDs
- ✅ Timestamps
- ✅ Assessment responses
- ✅ Dialogue transcripts
- ✅ Task responses
- ✅ Survey responses

**NOT Stored:**
- ❌ Names
- ❌ Email addresses
- ❌ IP addresses
- ❌ Any personal identifying information

### Access Control

- **Admin password** protects all data downloads
- **Streamlit Cloud** encrypts data in transit
- **Only you** can access Streamlit Cloud dashboard
- **Change password** if compromised (edit `admin_download.py`)

---

## 📋 Quick Reference

### Admin Password
```
Big5llmstudy
```

### File Formats
- **ZIP:** Complete data package
- **CSV:** Spreadsheet for analysis
- **JSON:** Raw data files
- **MD/HTML:** Human-readable reports

### Download Frequency
- **During study:** Weekly backups
- **After completion:** Final download + CSV export

### Data Locations
- **Live data:** Streamlit Cloud (`research_data/` folder)
- **Backups:** Your local/cloud storage
- **Analysis:** Copy to analysis software

---

## ✅ Checklist for Each Download Session

- [ ] Log in to admin dashboard
- [ ] Check total participant count
- [ ] Review any new participants
- [ ] Download all data as ZIP
- [ ] Save with descriptive filename (include date)
- [ ] Store in backup location
- [ ] Verify ZIP opens correctly
- [ ] Check for data completeness
- [ ] Log out of admin dashboard

---

## 📞 Support

### For Technical Issues:
- Check Streamlit Cloud dashboard logs
- Verify data folder structure
- Review this guide's troubleshooting section

### For Data Questions:
- Review individual participant HTML reports
- Check CSV export for overview
- Examine JSON files for detailed data

---

## Summary

**You have a simple, secure system for downloading participant data:**

1. **Log in** with password: `Big5llmstudy`
2. **Choose download method:**
   - All data (ZIP) - for backups
   - Individual participant - for review
   - CSV export - for analysis
3. **Download regularly** (weekly recommended)
4. **Backup securely** (encrypted storage)
5. **Analyze** in your preferred software

**No email setup needed - just log in when you want to check or download data!**
