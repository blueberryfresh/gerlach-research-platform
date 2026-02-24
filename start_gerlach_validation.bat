@echo off
echo ========================================
echo Gerlach Personality Validation Suite
echo ========================================
echo.
echo Starting Streamlit validation interface...
echo.
python -m streamlit run gerlach_validation_interface.py --server.headless true --browser.gatherUsageStats false
pause
