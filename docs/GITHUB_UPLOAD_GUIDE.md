# GitHub Upload Guide - Step-by-Step

## Upload Your Research Platform to GitHub

This guide will walk you through uploading your Gerlach Research Platform to GitHub so you can deploy it to Streamlit Cloud.

---

## Prerequisites

✅ You have a GitHub account  
✅ You have Git installed on your computer  
✅ Your code is in: `C:\Users\blueb\Desktop\Big5`

---

## Step 1: Check if Git is Installed

### 1.1 Open PowerShell or Command Prompt

Press `Windows Key + R`, type `powershell`, press Enter

### 1.2 Check Git Version

```powershell
git --version
```

**Expected Output:**
```
git version 2.40.0.windows.1
```

**If you see an error:**
- Git is not installed
- Download from: https://git-scm.com/download/win
- Install with default settings
- Restart PowerShell after installation

---

## Step 2: Configure Git (First Time Only)

If this is your first time using Git, set your identity:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Example:**
```powershell
git config --global user.name "John Smith"
git config --global user.email "john.smith@university.edu"
```

**Verify:**
```powershell
git config --global user.name
git config --global user.email
```

---

## Step 3: Create .gitignore File

This prevents sensitive data from being uploaded to GitHub.

### 3.1 Navigate to Your Project

```powershell
cd C:\Users\blueb\Desktop\Big5
```

### 3.2 Create .gitignore

```powershell
notepad .gitignore
```

Click "Yes" when asked to create a new file.

### 3.3 Add This Content to .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Streamlit
.streamlit/secrets.toml

# Research Data - DO NOT UPLOAD PARTICIPANT DATA
research_data/
*.json
*.csv
data_backup/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# API Keys and Secrets
.env
secrets.toml
*.key

# Temporary files
*.tmp
~$*

# Word temporary files
~$*.docx
```

**Save and close** (Ctrl+S, then close Notepad)

---

## Step 4: Initialize Git Repository

### 4.1 Initialize Git

```powershell
git init
```

**Expected Output:**
```
Initialized empty Git repository in C:/Users/blueb/Desktop/Big5/.git/
```

### 4.2 Check Status

```powershell
git status
```

You'll see a list of all files that will be tracked.

**Important:** Make sure `research_data/` is NOT listed (should be ignored)

---

## Step 5: Stage Files for Commit

### 5.1 Add All Files

```powershell
git add .
```

The `.` means "add all files" (except those in .gitignore)

### 5.2 Verify What's Staged

```powershell
git status
```

**You should see:**
- ✅ All Python files (.py)
- ✅ requirements.txt
- ✅ Task PDFs
- ✅ Documentation files
- ❌ NOT research_data/
- ❌ NOT __pycache__/

**If research_data/ appears:**
```powershell
git rm -r --cached research_data/
```

---

## Step 6: Create First Commit

### 6.1 Commit Your Code

```powershell
git commit -m "Initial commit - Gerlach Research Platform"
```

**Expected Output:**
```
[main (root-commit) abc1234] Initial commit - Gerlach Research Platform
 XX files changed, XXXX insertions(+)
 create mode 100644 agent_research_app.py
 create mode 100644 requirements.txt
 ...
```

---

## Step 7: Create GitHub Repository

### 7.1 Go to GitHub

Open your browser and go to: https://github.com

### 7.2 Sign In

Log in with your GitHub account

### 7.3 Create New Repository

1. Click the **"+"** icon (top right)
2. Select **"New repository"**

### 7.4 Repository Settings

**Repository name:** `gerlach-research-platform`  
(or any name you prefer - use lowercase and hyphens)

**Description:** `Multi-agent research platform for studying human-LLM collaboration with Gerlach personality types`

**Visibility:**
- ✅ **Private** (recommended - keeps your research private)
- ⚪ Public (only if you want it publicly visible)

**Initialize repository:**
- ❌ Do NOT check "Add a README file"
- ❌ Do NOT add .gitignore
- ❌ Do NOT choose a license

(We already have these files locally)

### 7.5 Click "Create repository"

---

## Step 8: Connect Local Repository to GitHub

After creating the repository, GitHub will show you instructions. Follow these:

### 8.1 Copy Your Repository URL

You'll see something like:
```
https://github.com/YOUR_USERNAME/gerlach-research-platform.git
```

**Example:**
```
https://github.com/johnsmith/gerlach-research-platform.git
```

### 8.2 Add Remote Origin

In PowerShell (still in `C:\Users\blueb\Desktop\Big5`):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/gerlach-research-platform.git
```

**Replace YOUR_USERNAME with your actual GitHub username!**

### 8.3 Verify Remote

```powershell
git remote -v
```

**Expected Output:**
```
origin  https://github.com/YOUR_USERNAME/gerlach-research-platform.git (fetch)
origin  https://github.com/YOUR_USERNAME/gerlach-research-platform.git (push)
```

---

## Step 9: Rename Branch to 'main'

GitHub uses 'main' as the default branch name.

```powershell
git branch -M main
```

---

## Step 10: Push to GitHub

### 10.1 Push Your Code

```powershell
git push -u origin main
```

### 10.2 Authentication

You'll be prompted to authenticate. **Two options:**

#### Option A: Personal Access Token (Recommended)

1. **Create Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name: "Gerlach Research Upload"
   - Select scopes: ✅ `repo` (all sub-items)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

2. **Use Token:**
   - When prompted for password, paste your token
   - Username: your GitHub username
   - Password: paste the token (not your GitHub password)

#### Option B: GitHub Desktop (Easier)

1. Download GitHub Desktop: https://desktop.github.com
2. Install and sign in
3. Add existing repository: `C:\Users\blueb\Desktop\Big5`
4. Click "Publish repository"

### 10.3 Verify Upload

**Expected Output:**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), XX.XX KiB | XX.XX MiB/s, done.
Total XX (delta X), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/gerlach-research-platform.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## Step 11: Verify on GitHub

### 11.1 Go to Your Repository

Open browser: `https://github.com/YOUR_USERNAME/gerlach-research-platform`

### 11.2 Check Files

You should see:
- ✅ `agent_research_app.py`
- ✅ `task_response_ui.py`
- ✅ `gerlach_personality_llms.py`
- ✅ `requirements.txt`
- ✅ `agents/` folder
- ✅ `Task/` folder
- ✅ `docs/` folder
- ✅ `.gitignore`
- ❌ NO `research_data/` folder (good!)

---

## Step 12: Add README (Optional but Recommended)

### 12.1 Create README on GitHub

1. Click "Add a README" button on your repository page
2. Or create locally:

```powershell
notepad README.md
```

### 12.2 Add This Content

```markdown
# Gerlach Research Platform

Multi-agent research platform for studying human-LLM collaboration with Gerlach personality types.

## Features

- Big Five personality assessment (50 questions)
- Four LLM personalities (Average, Role Model, Self-Centred, Reserved)
- Two research tasks (Noble Industries, Popcorn Brain)
- Task-specific data capture
- Post-experiment survey (37 questions)
- Comprehensive report generation

## Deployment

This application is deployed on Streamlit Cloud.

## Research Use Only

This platform is for academic research purposes.
```

### 12.3 Commit and Push

```powershell
git add README.md
git commit -m "Add README"
git push
```

---

## Troubleshooting

### Problem: "git: command not found"

**Solution:**
1. Install Git from: https://git-scm.com/download/win
2. Restart PowerShell
3. Try again

### Problem: Authentication Failed

**Solution:**
1. Use Personal Access Token (not password)
2. Generate token at: https://github.com/settings/tokens
3. Use token as password when prompted

### Problem: "research_data/" is being uploaded

**Solution:**
```powershell
git rm -r --cached research_data/
git commit -m "Remove research data"
git push
```

### Problem: Large files rejected

**Solution:**
- Check file sizes: `git ls-files -s`
- GitHub has 100MB file limit
- Remove large files from commit
- Add to .gitignore

### Problem: Wrong files uploaded

**Solution:**
```powershell
# Remove file from Git (keeps local copy)
git rm --cached filename.ext
git commit -m "Remove unwanted file"
git push
```

---

## Making Updates Later

After initial upload, when you make changes:

```powershell
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Describe your changes here"

# 4. Push to GitHub
git push
```

**Example:**
```powershell
git add .
git commit -m "Fix survey question display bug"
git push
```

---

## Next Steps

After uploading to GitHub:

1. ✅ **Verify all files are on GitHub**
2. ✅ **Check .gitignore is working** (no sensitive data)
3. ➡️ **Deploy to Streamlit Cloud** (see DEPLOYMENT_GUIDE_STREAMLIT_CLOUD.md)

---

## Quick Reference Commands

```powershell
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline

# See what changed
git diff
```

---

## Security Checklist

Before pushing, verify:

- [ ] `.gitignore` includes `research_data/`
- [ ] `.gitignore` includes `.env` and `secrets.toml`
- [ ] No API keys in code
- [ ] No participant data in repository
- [ ] No passwords or tokens in files
- [ ] `research_data/` folder is empty or ignored

---

## Support

If you encounter issues:

1. Check GitHub documentation: https://docs.github.com
2. Search Stack Overflow: https://stackoverflow.com/questions/tagged/git
3. GitHub Community: https://github.community

---

*Last Updated: February 24, 2026*
