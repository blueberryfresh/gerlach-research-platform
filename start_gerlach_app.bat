@echo off
REM Launcher script for Gerlach Personality Types App
echo ========================================
echo  Gerlach (2018) Personality Types App
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
python -m streamlit run gerlach_personality_app.py --server.port 8504

pause
