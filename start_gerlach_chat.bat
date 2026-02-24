@echo off
echo ========================================
echo Gerlach Personality Chat Interface
echo ========================================
echo.
echo Starting Streamlit chat interface...
echo.
python -m streamlit run gerlach_chat_interface.py --server.headless true --browser.gatherUsageStats false
pause
