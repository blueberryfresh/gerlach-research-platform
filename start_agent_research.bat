@echo off
REM Launcher script for Multi-Agent Research Platform
echo ========================================
echo  Gerlach Multi-Agent Research Platform
echo ========================================
echo.
echo Starting the application...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if ANTHROPIC_API_KEY is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo WARNING: ANTHROPIC_API_KEY environment variable is not set!
    echo Please set it before running the app:
    echo   set ANTHROPIC_API_KEY=your-api-key-here
    echo.
    pause
)

REM Start Streamlit app
python -m streamlit run agent_research_app.py --server.port 8505
