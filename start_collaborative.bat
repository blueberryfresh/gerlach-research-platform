@echo off
echo ========================================
echo Gerlach Collaborative Problem Solving
echo ========================================
echo.
echo Starting unified interface with all 4 personalities...
echo.
python -m streamlit run gerlach_collaborative_interface.py --server.headless true --browser.gatherUsageStats false
pause
