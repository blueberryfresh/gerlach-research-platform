@echo off
REM Quick Start Script for GitHub Upload
REM Gerlach Research Platform

echo ========================================
echo GitHub Upload - Gerlach Research Platform
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Navigate to project directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if .gitignore exists
if not exist ".gitignore" (
    echo Creating .gitignore file...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo .Python
        echo env/
        echo venv/
        echo.
        echo # Streamlit
        echo .streamlit/secrets.toml
        echo.
        echo # Research Data - DO NOT UPLOAD
        echo research_data/
        echo *.json
        echo *.csv
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Logs
        echo *.log
        echo.
        echo # Secrets
        echo .env
        echo *.key
    ) > .gitignore
    echo .gitignore created!
    echo.
)

REM Check if already initialized
if exist ".git" (
    echo Git repository already initialized.
    echo.
) else (
    echo Initializing Git repository...
    git init
    echo.
)

echo ========================================
echo IMPORTANT: Before proceeding
echo ========================================
echo.
echo 1. Make sure you have created a repository on GitHub
echo 2. Go to: https://github.com/new
echo 3. Repository name: gerlach-research-platform
echo 4. Make it PRIVATE
echo 5. Do NOT initialize with README
echo.
echo Press any key when you have created the repository...
pause >nul
echo.

REM Get GitHub username and repository name
set /p GITHUB_USER="Enter your GitHub username: "
set /p REPO_NAME="Enter repository name (default: gerlach-research-platform): "

if "%REPO_NAME%"=="" set REPO_NAME=gerlach-research-platform

echo.
echo Repository URL will be:
echo https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
set /p CONFIRM="Is this correct? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo Upload cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================
echo Step 1: Adding files to Git
echo ========================================
echo.

git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

echo Files added successfully!
echo.

echo ========================================
echo Step 2: Creating commit
echo ========================================
echo.

git commit -m "Initial commit - Gerlach Research Platform"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit
    pause
    exit /b 1
)

echo Commit created successfully!
echo.

echo ========================================
echo Step 3: Connecting to GitHub
echo ========================================
echo.

REM Check if remote already exists
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo Remote 'origin' already exists. Removing...
    git remote remove origin
)

git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
if %errorlevel% neq 0 (
    echo ERROR: Failed to add remote
    pause
    exit /b 1
)

echo Remote added successfully!
echo.

echo ========================================
echo Step 4: Renaming branch to 'main'
echo ========================================
echo.

git branch -M main
echo Branch renamed to 'main'
echo.

echo ========================================
echo Step 5: Pushing to GitHub
echo ========================================
echo.
echo You will be prompted for authentication.
echo.
echo IMPORTANT:
echo - Username: Your GitHub username
echo - Password: Use a Personal Access Token (NOT your password)
echo.
echo If you don't have a token:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Select 'repo' scope
echo 4. Copy the token and use it as password
echo.
echo Press any key to continue with push...
pause >nul
echo.

git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to push to GitHub
    echo.
    echo Common issues:
    echo 1. Authentication failed - Use Personal Access Token
    echo 2. Repository doesn't exist - Create it on GitHub first
    echo 3. Wrong repository URL - Check username and repo name
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Upload Complete!
echo ========================================
echo.
echo Your code is now on GitHub at:
echo https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo Next steps:
echo 1. Verify files on GitHub (open the URL above)
echo 2. Deploy to Streamlit Cloud
echo 3. See DEPLOYMENT_GUIDE_STREAMLIT_CLOUD.md for details
echo.
echo Press any key to exit...
pause >nul
