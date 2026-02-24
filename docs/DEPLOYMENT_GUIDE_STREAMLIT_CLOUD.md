# Deployment Guide: Streamlit Cloud Production

## Step 4: Deploy to Production (Streamlit Cloud)

**Goal**: Deploy the Gerlach Personality Research Platform to Streamlit Cloud for 100 participants to access remotely.

---

## Why Streamlit Cloud?

### Advantages
✅ **Free tier** supports up to 100 concurrent users  
✅ **Zero server management** - fully managed hosting  
✅ **Automatic HTTPS** - secure by default  
✅ **GitHub integration** - deploy from repository  
✅ **Auto-reload** on code changes  
✅ **Environment variables** for secrets (API keys)  
✅ **Custom domains** available  
✅ **Built-in monitoring** and logs  

### Limitations
⚠️ **Resource limits**: 1GB RAM, shared CPU  
⚠️ **Sleep after inactivity**: Apps sleep after 7 days of no use  
⚠️ **Data persistence**: Use external storage for large datasets  

---

## Pre-Deployment Checklist

### 1. Code Preparation

- [x] ✅ All features implemented and tested locally
- [x] ✅ Requirements.txt up to date
- [ ] ⏳ Remove debug code and print statements
- [ ] ⏳ Set production-safe configurations
- [ ] ⏳ Add error handling for API failures
- [ ] ⏳ Optimize for performance

### 2. Data Strategy

**Current Setup**: Local file-based storage (`research_data/`)

**Production Options**:

**Option A: Keep File-Based (Simple)**
- ✅ No changes needed
- ✅ Works for 100 participants
- ⚠️ Data stored on Streamlit's ephemeral filesystem
- ⚠️ Need manual backups

**Option B: Cloud Storage (Recommended)**
- Use AWS S3, Google Cloud Storage, or Dropbox
- Persistent data storage
- Easy backups
- Requires code changes

**Recommendation**: Start with Option A, migrate to Option B if needed.

### 3. Environment Variables

Required secrets:
- `ANTHROPIC_API_KEY` - Your Claude API key

Optional:
- `DATA_BACKUP_URL` - Cloud storage endpoint
- `ADMIN_PASSWORD` - For admin access

### 4. Repository Setup

- [ ] Create GitHub repository (public or private)
- [ ] Push all code to repository
- [ ] Ensure `.gitignore` excludes sensitive data
- [ ] Add README with setup instructions

---

## Deployment Steps

### Step 1: Prepare GitHub Repository

#### 1.1 Create `.gitignore`

```bash
# Create .gitignore file
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# Research Data (DO NOT COMMIT PARTICIPANT DATA)
research_data/
*.json
*.csv

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# API Keys
.env
EOL
```

#### 1.2 Initialize Git Repository

```bash
cd c:\Users\blueb\Desktop\Big5

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Gerlach Research Platform"

# Create GitHub repo (via GitHub website or CLI)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/gerlach-research.git
git branch -M main
git push -u origin main
```

#### 1.3 Verify Repository Contents

Essential files for deployment:
```
gerlach-research/
├── agent_research_app.py          # Main application
├── task_response_ui.py             # Task interfaces
├── gerlach_personality_llms.py     # LLM personalities
├── requirements.txt                # Dependencies
├── agents/                         # Agent modules
│   ├── __init__.py
│   ├── data_models.py
│   ├── supervisor_agent.py
│   ├── big5_assessment_agent.py
│   ├── dialogue_capture_agent.py
│   ├── task_response_agent.py
│   ├── task_response_models.py
│   ├── survey_agent.py
│   └── summary_agent.py
├── Task/                           # Task PDFs
│   ├── Noble Industries.pdf
│   └── Popcorn Brain.pdf
├── docs/                           # Documentation
├── README.md
└── .gitignore
```

---

### Step 2: Create Streamlit Cloud Account

1. **Go to**: https://streamlit.io/cloud
2. **Sign up** with GitHub account
3. **Authorize** Streamlit to access your repositories
4. **Verify** email address

---

### Step 3: Deploy Application

#### 3.1 Create New App

1. Click **"New app"** button
2. Select your repository: `YOUR_USERNAME/gerlach-research`
3. Select branch: `main`
4. Set main file path: `agent_research_app.py`
5. Click **"Deploy!"**

#### 3.2 Configure Advanced Settings

**App URL**: Choose a custom subdomain
- Example: `gerlach-research.streamlit.app`
- Or custom domain: `research.yourlab.edu`

**Python Version**: 3.9 or higher

**Secrets**: Add environment variables

---

### Step 4: Configure Secrets

In Streamlit Cloud dashboard:

1. Go to **App settings** → **Secrets**
2. Add your secrets in TOML format:

```toml
# .streamlit/secrets.toml format

ANTHROPIC_API_KEY = "sk-ant-api03-..."

# Optional: Admin password
ADMIN_PASSWORD = "your-secure-password"

# Optional: Data backup settings
[backup]
enabled = true
provider = "s3"
bucket = "gerlach-research-data"
```

#### Update Code to Use Secrets

```python
# In agent_research_app.py
import os
import streamlit as st

# Get API key from secrets or environment
if 'ANTHROPIC_API_KEY' in st.secrets:
    os.environ['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
elif 'ANTHROPIC_API_KEY' not in os.environ:
    st.error("⚠️ ANTHROPIC_API_KEY not configured. Please contact administrator.")
    st.stop()
```

---

### Step 5: Test Deployment

#### 5.1 Access Your App

URL: `https://gerlach-research.streamlit.app`

#### 5.2 Test Checklist

- [ ] App loads without errors
- [ ] Registration works
- [ ] Big5 assessment displays all 50 questions
- [ ] Task selection shows both tasks
- [ ] Dialogue interface connects to Claude API
- [ ] Task response forms work (Noble Industries, Popcorn Brain)
- [ ] Survey displays all 37 questions
- [ ] Report generation works
- [ ] Data saves correctly
- [ ] No sensitive data exposed

#### 5.3 Performance Testing

Test with multiple concurrent users:
- Open 5-10 browser tabs
- Start sessions simultaneously
- Monitor response times
- Check for errors in logs

---

### Step 6: Configure Custom Domain (Optional)

#### 6.1 Purchase Domain
- Example: `research.yourlab.edu`
- Or subdomain of existing domain

#### 6.2 DNS Configuration

Add CNAME record:
```
research.yourlab.edu → gerlach-research.streamlit.app
```

#### 6.3 Update Streamlit Settings

In Streamlit Cloud dashboard:
1. Go to **Settings** → **General**
2. Add custom domain
3. Wait for SSL certificate provisioning (automatic)

---

## Production Configuration

### Update `agent_research_app.py` for Production

```python
import streamlit as st
import os
from pathlib import Path

# Production configuration
IS_PRODUCTION = os.getenv('STREAMLIT_SHARING_MODE') == 'true'

if IS_PRODUCTION:
    # Production settings
    st.set_page_config(
        page_title="Gerlach Research Platform",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'mailto:research@yourlab.edu',
            'Report a bug': 'mailto:support@yourlab.edu',
            'About': 'Gerlach Personality Research Platform v1.0'
        }
    )
    
    # Use environment-based data directory
    DATA_DIR = Path("/tmp/research_data")  # Streamlit Cloud temp storage
    
    # Enable error tracking
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    # Local development settings
    DATA_DIR = Path(__file__).parent / "research_data"
```

### Add Health Check Endpoint

```python
# Add to agent_research_app.py

def health_check():
    """Health check for monitoring"""
    try:
        # Check if agents initialize
        agents = init_agents()
        
        # Check if LLM is accessible
        if not agents['llm_ready']:
            return False, "LLM not ready"
        
        # Check data directory
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        return True, "All systems operational"
    except Exception as e:
        return False, str(e)

# Display in sidebar for admins
if st.sidebar.checkbox("Show System Status", value=False):
    status, message = health_check()
    if status:
        st.sidebar.success(f"✅ {message}")
    else:
        st.sidebar.error(f"❌ {message}")
```

---

## Data Backup Strategy

### Automated Backups

#### Option 1: Manual Download (Simple)

Add admin interface to download all data:

```python
# Add to agent_research_app.py

if st.sidebar.text_input("Admin Password", type="password") == st.secrets.get("ADMIN_PASSWORD"):
    st.sidebar.markdown("### 🔐 Admin Controls")
    
    if st.sidebar.button("Download All Data"):
        import zipfile
        import io
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(DATA_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, DATA_DIR)
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        st.sidebar.download_button(
            label="📥 Download Backup ZIP",
            data=zip_buffer,
            file_name=f"research_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
```

#### Option 2: Cloud Storage (Recommended)

Use AWS S3, Google Cloud Storage, or Dropbox:

```python
# Example with boto3 (AWS S3)
import boto3
from datetime import datetime

def backup_to_s3():
    """Backup research data to S3"""
    s3 = boto3.client('s3',
        aws_access_key_id=st.secrets['AWS_ACCESS_KEY'],
        aws_secret_access_key=st.secrets['AWS_SECRET_KEY']
    )
    
    bucket = st.secrets['S3_BUCKET']
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"backups/{datetime.now().strftime('%Y%m%d')}/{os.path.relpath(local_path, DATA_DIR)}"
            
            s3.upload_file(local_path, bucket, s3_path)
    
    return True

# Schedule daily backups
if IS_PRODUCTION:
    # Run backup every 24 hours
    import schedule
    schedule.every().day.at("02:00").do(backup_to_s3)
```

---

## Monitoring & Maintenance

### Streamlit Cloud Monitoring

**Built-in Metrics**:
- App uptime
- Request count
- Error rate
- Response times

**Access Logs**:
1. Go to Streamlit Cloud dashboard
2. Select your app
3. Click **"Logs"** tab
4. View real-time logs

### Custom Monitoring

Add usage tracking:

```python
# Track session starts
def log_session_start(user_id):
    """Log session start for analytics"""
    log_data = {
        'event': 'session_start',
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'app_version': '1.0'
    }
    
    # Write to log file or send to analytics service
    logging.info(f"Session started: {log_data}")

# Track completion rates
def log_stage_completion(user_id, stage):
    """Log workflow stage completion"""
    log_data = {
        'event': 'stage_complete',
        'user_id': user_id,
        'stage': stage,
        'timestamp': datetime.now().isoformat()
    }
    
    logging.info(f"Stage completed: {log_data}")
```

### Error Tracking

Integrate with Sentry (optional):

```python
import sentry_sdk
from sentry_sdk.integrations.streamlit import StreamlitIntegration

if IS_PRODUCTION:
    sentry_sdk.init(
        dsn=st.secrets.get('SENTRY_DSN'),
        integrations=[StreamlitIntegration()],
        traces_sample_rate=0.1
    )
```

---

## Scaling Considerations

### Current Limits (Free Tier)
- **RAM**: 1GB
- **CPU**: Shared
- **Concurrent users**: ~100
- **Storage**: Ephemeral (temporary)

### If You Need More

**Streamlit Cloud Teams** ($250/month):
- 3GB RAM
- Dedicated resources
- Priority support
- Custom authentication

**Self-Hosted Alternative**:
- Deploy to AWS/GCP/Azure
- Full control over resources
- More complex setup
- Higher cost

---

## Participant Access

### Sharing the App

**Public URL**: `https://gerlach-research.streamlit.app`

**Recruitment Email Template**:

```
Subject: Invitation to Participate in Gerlach Personality Research Study

Dear Participant,

You are invited to participate in our research study on human-LLM collaboration 
and personality types.

To participate:
1. Visit: https://gerlach-research.streamlit.app
2. Enter your participant ID: [PROVIDED_ID]
3. Complete the consent form
4. Follow the on-screen instructions

The study takes approximately 45-60 minutes to complete.

If you experience any technical issues, please contact:
research-support@yourlab.edu

Thank you for your participation!

Research Team
```

### Access Control (Optional)

Add password protection:

```python
# Simple password gate
def check_access():
    """Require access code to use app"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔬 Gerlach Research Platform")
        st.markdown("Please enter your access code to continue.")
        
        access_code = st.text_input("Access Code", type="password")
        
        if st.button("Submit"):
            if access_code == st.secrets.get('ACCESS_CODE'):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid access code")
        
        st.stop()

# Call at app start
check_access()
```

---

## Troubleshooting

### Common Issues

**Issue**: App won't start
- **Check**: Logs for error messages
- **Fix**: Verify requirements.txt has all dependencies
- **Fix**: Check for syntax errors in code

**Issue**: API key not working
- **Check**: Secrets configuration in Streamlit Cloud
- **Fix**: Verify key is correct and active
- **Fix**: Check API quota limits

**Issue**: Data not saving
- **Check**: DATA_DIR permissions
- **Fix**: Ensure directory creation in code
- **Fix**: Check disk space limits

**Issue**: Slow performance
- **Check**: Number of concurrent users
- **Fix**: Optimize database queries
- **Fix**: Add caching with `@st.cache_data`
- **Fix**: Reduce API calls

**Issue**: App sleeps after inactivity
- **Solution**: Wake up by visiting URL
- **Prevention**: Upgrade to Teams plan
- **Workaround**: Set up ping service

---

## Post-Deployment Checklist

### Week 1
- [ ] Monitor logs daily
- [ ] Test with pilot participants (5-10)
- [ ] Collect feedback on usability
- [ ] Fix any critical bugs
- [ ] Verify data is saving correctly
- [ ] Set up daily backups

### Week 2-4
- [ ] Monitor completion rates
- [ ] Track drop-off points
- [ ] Respond to participant questions
- [ ] Backup data weekly
- [ ] Monitor API usage and costs

### After Data Collection
- [ ] Download all participant data
- [ ] Create final backup
- [ ] Verify data integrity
- [ ] Export for analysis
- [ ] Archive deployment

---

## Cost Estimate

### Streamlit Cloud (Free Tier)
- **Hosting**: $0/month
- **Custom domain**: $0 (if using .streamlit.app)

### Anthropic API
- **Claude API**: ~$0.01-0.03 per dialogue
- **100 participants**: ~$50-150 total
- **Buffer**: Add 50% for retries/errors = $75-225

### Optional Services
- **Custom domain**: $12/year
- **Cloud storage (S3)**: ~$5/month
- **Monitoring (Sentry)**: Free tier available

**Total Estimated Cost**: $100-300 for entire study

---

## Success Metrics

Track these metrics post-deployment:

- ✅ **Uptime**: >99%
- ✅ **Completion rate**: >90%
- ✅ **Average session time**: 45-60 minutes
- ✅ **Error rate**: <1%
- ✅ **API response time**: <5 seconds
- ✅ **Data integrity**: 100% (no lost sessions)

---

## Quick Start Commands

```bash
# 1. Prepare repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/gerlach-research.git
git push -u origin main

# 2. Deploy to Streamlit Cloud
# (Use web interface at streamlit.io/cloud)

# 3. Configure secrets
# (Add ANTHROPIC_API_KEY in Streamlit Cloud dashboard)

# 4. Test deployment
# Visit: https://YOUR-APP.streamlit.app

# 5. Monitor
# Check logs in Streamlit Cloud dashboard
```

---

## Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-cloud
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: https://github.com/streamlit/streamlit/issues
- **Anthropic Docs**: https://docs.anthropic.com

---

## Summary

Deploying to Streamlit Cloud is straightforward:

1. ✅ Push code to GitHub
2. ✅ Connect Streamlit Cloud to repository
3. ✅ Configure secrets (API key)
4. ✅ Deploy with one click
5. ✅ Monitor and maintain

**Estimated Time**: 2-4 hours for initial deployment  
**Difficulty**: Low to Medium  
**Cost**: $100-300 total for 100 participants

Your research platform is ready for production! 🚀
