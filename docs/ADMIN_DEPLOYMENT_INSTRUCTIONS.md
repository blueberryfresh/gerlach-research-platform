# Admin Download & Email Notification - Deployment Instructions

## 🎯 What Was Implemented

You now have a complete **admin data download system** with **automatic email notifications**:

### ✅ Features Implemented:

1. **Password-Protected Admin Dashboard**
   - Password: `[ask the PI — not documented here for security]`
   - Secure access to all participant data

2. **Data Download Options**:
   - Download all participant data as ZIP
   - Download individual participant data
   - Export to CSV for statistical analysis

3. **Automatic Email Notifications**:
   - Sent when participants complete the study
   - Recipients: `kchoi29@gmu.edu` and `il.im@yonsei.ac.kr`
   - Includes participant ID, session ID, completion time, this participant's Gerlach
     type/task/AI personality, and the current study-wide balance across all three

---

## 📂 New Files Created

```
Big5/
├── admin_download.py                    # Admin dashboard (main file)
├── utils/
│   └── email_notifier.py               # Email notification utility
├── agents/
│   └── supervisor_agent.py             # Updated with email integration
└── docs/
    ├── EMAIL_SETUP_GUIDE.md            # Step-by-step email setup
    └── ADMIN_DEPLOYMENT_INSTRUCTIONS.md # This file
```

---

## 🚀 Deployment Steps

### Step 1: Push Changes to GitHub

You need to push the new files to your GitHub repository so Streamlit Cloud can deploy them.

```bash
# Navigate to your project folder
cd C:\Users\blueb\Desktop\Big5

# Add all new files
git add admin_download.py
git add utils/email_notifier.py
git add agents/supervisor_agent.py
git add docs/EMAIL_SETUP_GUIDE.md
git add docs/ADMIN_DEPLOYMENT_INSTRUCTIONS.md

# Commit changes
git commit -m "Add admin download page and email notifications"

# Push to GitHub
git push origin main
```

### Step 2: Configure Email on Streamlit Cloud

Follow the detailed instructions in `docs/EMAIL_SETUP_GUIDE.md`:

1. **Create Gmail App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Generate app password for "Gerlach Research Platform"
   - Save the 16-character password

2. **Add to Streamlit Secrets**:
   - Go to https://share.streamlit.io/
   - Open your app settings
   - Click "Secrets"
   - Add these lines:

```toml
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "your-gmail@gmail.com"
SENDER_PASSWORD = "your-16-char-app-password"
```

3. **Save and Restart**:
   - Click "Save"
   - App will automatically restart

### Step 3: Add Admin Page to Main App

You need to make the admin page accessible from your main app.

**Option A: Add to Sidebar Navigation**

Edit `agent_research_app.py`:

```python
# At the top of the file, add import
import admin_download

# In your sidebar or main navigation, add:
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Admin Tools")

if st.sidebar.button("📊 Admin Download Center"):
    admin_download.admin_page()
```

**Option B: Create Multi-Page App**

1. Create a `pages/` folder in your project root
2. Copy `admin_download.py` to `pages/Admin_Download.py`
3. Streamlit will automatically add it to the sidebar

### Step 4: Test the System

1. **Test Admin Access**:
   - Go to your app URL
   - Navigate to Admin Download page
   - Enter password: `[ask the PI — not documented here for security]`
   - Verify you can see the dashboard

2. **Test Email Notifications**:
   - In Admin Dashboard, go to "Email Settings" tab
   - Enter test participant ID: `TEST_001`
   - Click "Send Test Email"
   - Check both email addresses for the notification

3. **Test Data Download**:
   - If you have test data, try downloading it as ZIP
   - Verify the ZIP contains the expected files

---

## 📥 How to Download Participant Data

### Method 1: Download All Data

1. Log in to admin dashboard (password: `[ask the PI — not documented here for security]`)
2. Go to "Download All Data" tab
3. Click "Create ZIP File"
4. Click "Download All Data (ZIP)"
5. Save the file: `gerlach_research_data_YYYYMMDD_HHMMSS.zip`

**ZIP Contents:**
```
gerlach_research_data_20260224_143022.zip
├── sessions/
│   └── P001_20260224_143022_abc123.json
├── assessments/
│   └── assessment_P001_xyz789.json
├── dialogues/
│   └── dialogue_P001_abc456.json
├── task_responses/
│   ├── noble/
│   │   └── noble_P001_def789.json
│   └── popcorn/
│       └── popcorn_P002_ghi012.json
├── surveys/
│   └── survey_P001_jkl345.json
└── reports/
    ├── report_P001_20260224_143022_abc123.md
    └── report_P001_20260224_143022_abc123.html
```

### Method 2: Download Individual Participant

1. Log in to admin dashboard
2. Go to "Download by Participant" tab
3. Find the participant in the list
4. Click "Download [Participant_ID] Data"
5. Save the participant-specific ZIP file

### Method 3: Export to CSV

1. Log in to admin dashboard
2. Go to "Export to CSV" tab
3. Click "Generate CSV"
4. Click "Download CSV"
5. Open in Excel, SPSS, R, or Python for analysis

**CSV Columns:**
- User ID, Session ID, Created At, Current Stage
- Big5 scores: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- Gerlach Type, Gerlach Confidence
- Task Name, LLM Personality
- Message Count, Dialogue Duration
- Survey Completed

---

## 📧 Email Notifications

### When Emails Are Sent

Triggered from `render_re_consent()` in `agent_research_app.py`, immediately after the
session's stage is advanced to `COMPLETED` (right after the participant answers the
re-consent question following the post-experiment survey). A failure to send never
blocks the participant's flow — it's wrapped in a try/except.

### Email Content

**Subject:** "Participant Completed Study: [Participant_ID]"

**Body includes:**
- Participant ID, Session ID, completion timestamp
- This participant's Gerlach personality type, assigned task, and assigned AI personality
- Whether data consent was withdrawn at the re-consent step (if applicable)
- **Current study balance**: participants per Gerlach type, a Gerlach type × task
  table, and a Gerlach type × AI personality table — computed fresh from
  `research_data/` at the moment this participant completed
- Instructions to download data, and a list of available data

### Recipients

Both investigators receive notifications:
- kchoi29@gmu.edu
- il.im@yonsei.ac.kr

### To Change Recipients

Edit `utils/email_notifier.py`:

```python
INVESTIGATOR_EMAILS = ["new-email1@example.com", "new-email2@example.com"]
```

Then commit and push to GitHub. (Note: this constant lives only in
`utils/email_notifier.py` — `admin_download.py` does not define it.)

---

## 🔒 Security

### Admin Password

- **Password:** `[ask the PI — not documented here for security]`
- **Stored in:** Streamlit secrets (`ADMIN_PASSWORD`) or the `ADMIN_PASSWORD` environment variable — not hardcoded in `admin_download.py`
- **To change:** Edit the file, commit, and push to GitHub

### Email Credentials

- **Stored in:** Streamlit Cloud Secrets (encrypted)
- **Never in code:** Credentials are never committed to GitHub
- **Access:** Only you can view/edit secrets in Streamlit dashboard

### Data Privacy

Email notifications contain:
- ✅ Participant ID (anonymous)
- ✅ Session ID (anonymous)
- ❌ NO personal information
- ❌ NO assessment results
- ❌ NO dialogue content

Actual data must be downloaded through the secure admin dashboard.

---

## 📊 Data Analysis Workflow

### Recommended Workflow:

1. **Receive Email Notification**
   - Email arrives when participant completes study
   - Note the Participant ID

2. **Download Data**
   - Log in to admin dashboard
   - Download individual participant ZIP or wait to download all data

3. **Review Summary Report**
   - Open the HTML report for quick overview
   - Check Big5 profile, dialogue summary, task results

4. **Export for Analysis**
   - Use CSV export for quantitative analysis
   - Use JSON files for detailed qualitative analysis

5. **Backup Data**
   - Regularly download all data as backup
   - Store in secure location (encrypted drive, cloud storage)

---

## 🛠️ Troubleshooting

### Admin Page Not Accessible

**Problem:** Can't find admin page in app

**Solution:**
- Make sure you added navigation to `agent_research_app.py`
- Or use multi-page app structure with `pages/` folder
- Check that `admin_download.py` is in the correct location

### Email Not Sending

**Problem:** No emails received after participant completion

**Solution:**
1. Check Streamlit Cloud Secrets are configured
2. Verify Gmail App Password is correct (16 characters, no spaces)
3. Test email using "Email Settings" tab in admin dashboard
4. Check Streamlit logs for error messages

### Download Button Not Working

**Problem:** ZIP download fails or button doesn't respond

**Solution:**
1. Check that `research_data/` folder exists
2. Verify participant data files are present
3. Check browser console for JavaScript errors
4. Try refreshing the page

### CSV Export Empty

**Problem:** CSV file has headers but no data

**Solution:**
1. Verify that session files exist in `research_data/sessions/`
2. Check that JSON files are valid (not corrupted)
3. Review Streamlit logs for parsing errors

---

## 📋 Maintenance

### Regular Tasks

**Weekly:**
- Download all data as backup
- Verify email notifications are working
- Check for any error logs in Streamlit dashboard

**Monthly:**
- Review data storage usage
- Clean up old test data if needed
- Update documentation if workflow changes

**As Needed:**
- Change admin password if compromised
- Update recipient email addresses
- Modify email notification template

---

## 📞 Support

### For Email Issues:
- See `docs/EMAIL_SETUP_GUIDE.md`
- Check Gmail App Password settings
- Verify Streamlit Secrets configuration

### For Download Issues:
- Check Streamlit Cloud logs
- Verify file permissions
- Test with small data sets first

### For General Questions:
- Review this documentation
- Check Streamlit Cloud dashboard
- Contact technical support if needed

---

## ✅ Deployment Checklist

Before going live with participants:

- [ ] Push all new files to GitHub
- [ ] Configure email secrets on Streamlit Cloud
- [ ] Add admin page to main app navigation
- [ ] Test admin login with password
- [ ] Send test email notification
- [ ] Download test data as ZIP
- [ ] Export test data to CSV
- [ ] Verify both investigators receive emails
- [ ] Document admin password securely
- [ ] Create backup schedule

---

## 🎉 Summary

You now have a complete data management system:

1. **Automatic Email Notifications** - Know immediately when participants complete
2. **Secure Admin Dashboard** - Password-protected access to all data
3. **Flexible Download Options** - ZIP, individual, or CSV formats
4. **Complete Data Package** - All assessment, dialogue, task, and survey data
5. **Easy Analysis** - CSV export for statistical software

**Next Steps:**
1. Deploy to Streamlit Cloud (push to GitHub)
2. Configure email settings
3. Test the system
4. Start collecting data!

For detailed email setup, see: `docs/EMAIL_SETUP_GUIDE.md`
