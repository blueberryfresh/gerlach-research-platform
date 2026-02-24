@echo off
echo ========================================
echo  Big5 Personality LLMs Web Interface
echo ========================================
echo.
echo Starting server...
echo.
echo The interface will open automatically in your browser
echo If it doesn't open, go to: http://localhost:8503
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the Streamlit server
start /B python -m streamlit run unified_composite_web.py --server.port 8503 --server.address localhost --server.headless false

REM Wait a moment for server to start
timeout /t 5 /nobreak >nul

REM Open browser
start http://localhost:8503

echo.
echo Server is running! Close this window to stop the server.
echo.
pause
