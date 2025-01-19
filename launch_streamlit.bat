@echo off
echo Starting Streamlit...

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Set environment variables if needed
set PYTHONUNBUFFERED=1

:: Launch Streamlit with specific server settings
start /B streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true

:: Wait a moment to let Streamlit start
timeout /t 5 /nobreak

:: Check if the process is running
netstat -ano | findstr :8501
if %ERRORLEVEL% EQU 0 (
    echo Streamlit successfully started on port 8501
    exit /b 0
) else (
    echo Failed to start Streamlit
    exit /b 1
)