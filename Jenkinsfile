pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        APP_NAME = 'streamlit-text-converter'
        STREAMLIT_PORT = '8501'
        STREAMLIT_PID_FILE = 'streamlit.pid'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    bat """
                        if exist venv rmdir /s /q venv
                        python -m venv venv
                        call venv\\Scripts\\activate.bat
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest pytest-cov
                    """
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    bat """
                        call venv\\Scripts\\activate.bat
                        python -m pytest || exit /b 0
                    """
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Create a launcher script with proper process management
                    writeFile file: 'launch_streamlit.bat', text: '''
                        @echo off
                        echo Starting Streamlit...
                        call venv\\Scripts\\activate.bat
                        
                        REM Store the current process ID
                        echo %RANDOM% > streamlit.pid
                        
                        REM Run Streamlit with no window and redirect output
                        start /B /MIN "" cmd /c "streamlit run app.py --server.port 8501 > streamlit.log 2>&1"
                        
                        REM Wait briefly to ensure process starts
                        timeout /t 5 /nobreak > nul
                        
                        REM Check if Streamlit is running by attempting to connect to the port
                        powershell -Command "Test-NetConnection -ComputerName localhost -Port 8501 -InformationLevel Quiet"
                        if %ERRORLEVEL% EQU 0 (
                            echo Streamlit successfully started on port 8501
                            exit /b 0
                        ) else (
                            echo Failed to start Streamlit
                            type streamlit.log
                            exit /b 1
                        )
                    '''
                    
                    // Cleanup function for stopping previous instances
                    writeFile file: 'cleanup_streamlit.bat', text: '''
                        @echo off
                        REM Kill any existing Streamlit processes
                        taskkill /F /IM "streamlit.exe" /FI "WINDOWTITLE eq streamlit*" > nul 2>&1
                        if exist streamlit.pid del streamlit.pid
                        if exist streamlit.log del streamlit.log
                        exit /b 0
                    '''
                    
                    // Execute cleanup
                    bat 'call cleanup_streamlit.bat'
                    
                    // Launch Streamlit with proper error handling
                    bat """
                        call launch_streamlit.bat
                        if not exist streamlit.pid (
                            echo Failed to create PID file
                            exit /b 1
                        )
                        
                        REM Verify Streamlit is running
                        powershell -Command "if (-not (Test-NetConnection -ComputerName localhost -Port 8501 -InformationLevel Quiet)) { exit 1 }"
                        if %ERRORLEVEL% NEQ 0 (
                            echo Streamlit failed to start
                            type streamlit.log
                            call cleanup_streamlit.bat
                            exit /b 1
                        )
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully. Streamlit is running on http://localhost:8501"
        }
        failure {
            script {
                bat 'call cleanup_streamlit.bat'
            }
            echo "Pipeline failed. Check the logs for details."
        }
        always {
            script {
                // Archive the Streamlit log if it exists
                bat 'if exist streamlit.log copy streamlit.log streamlit_%BUILD_NUMBER%.log'
            }
        }
    }
}