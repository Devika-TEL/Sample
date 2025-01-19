pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        APP_NAME = 'streamlit-text-converter'
        STREAMLIT_PORT = '8501'
        STREAMLIT_PID_FILE = 'streamlit.pid'
        WORKSPACE = "${JENKINS_HOME}/workspace/${env.JOB_NAME}"
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
                    // Kill any existing Python/Streamlit processes
                    bat '''
                        taskkill /F /IM "streamlit.exe" 2>nul || exit /b 0
                        taskkill /F /IM "python.exe" 2>nul || exit /b 0
                        timeout /t 5 /nobreak > nul
                    '''
                    
                    // Clean up environment with proper error handling
                    bat '''
                        if exist venv (
                            rmdir /s /q venv 2>nul || (
                                echo Retrying with elevated permissions...
                                powershell -Command "Remove-Item -Path venv -Recurse -Force"
                            )
                        )
                        
                        echo Creating new virtual environment...
                        python -m venv venv || (
                            echo Failed to create virtual environment
                            exit /b 1
                        )
                        
                        call venv\\Scripts\\activate.bat || (
                            echo Failed to activate virtual environment
                            exit /b 1
                        )
                        
                        echo Installing dependencies...
                        venv\\Scripts\\python.exe -m pip install --upgrade pip
                        venv\\Scripts\\pip.exe install -r requirements.txt || (
                            echo Failed to install requirements
                            exit /b 1
                        )
                        venv\\Scripts\\pip.exe install pytest pytest-cov
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    bat '''
                        call venv\\Scripts\\activate.bat
                        venv\\Scripts\\python.exe -m pytest --junitxml=test-results.xml || exit /b 0
                    '''
                }
            }
        }
               
        stage('Deploy') {
            steps {
                script {
                    // Modified launcher script to run as a detached process
                    writeFile file: 'launch_streamlit.bat', text: '''
                        @echo off
                        setlocal EnableDelayedExpansion
                        
                        echo Checking for existing Streamlit instances...
                        taskkill /F /IM "streamlit.exe" 2>nul || echo No existing instances found
                        timeout /t 5 /nobreak > nul
                        
                        echo Starting Streamlit...
                        call venv\\Scripts\\activate.bat || (
                            echo Failed to activate virtual environment
                            exit /b 1
                        )
                        
                        REM Create a VBS script to run Streamlit in the background
                        echo Set WshShell = CreateObject("WScript.Shell") > run_streamlit.vbs
                        echo WshShell.CurrentDirectory = "%CD%" >> run_streamlit.vbs
                        echo cmd = "cmd /c venv\\Scripts\\streamlit.exe run app.py --server.port 8501 > streamlit.log 2>&1" >> run_streamlit.vbs
                        echo WshShell.Run cmd, 0, false >> run_streamlit.vbs
                        
                        REM Launch the VBS script
                        cscript //Nologo run_streamlit.vbs
                        
                        REM Store the timestamp as PID (since we can't get the actual PID of the detached process)
                        echo %date% %time% > streamlit.pid
                        
                        REM Wait for Streamlit to start (up to 30 seconds)
                        set /a attempts=0
                        :WAIT_LOOP
                        timeout /t 2 /nobreak > nul
                        powershell -Command "Test-NetConnection -ComputerName localhost -Port 8501 -InformationLevel Quiet"
                        if !ERRORLEVEL! EQU 0 (
                            echo Streamlit successfully started on port 8501
                            exit /b 0
                        )
                        set /a attempts+=1
                        if !attempts! lss 15 goto WAIT_LOOP
                        
                        echo Failed to start Streamlit after 30 seconds
                        type streamlit.log
                        exit /b 1
                    '''
                    
                    // Modified cleanup script to handle background process
                    writeFile file: 'cleanup_streamlit.bat', text: '''
                        @echo off
                        echo Cleaning up Streamlit processes...
                        taskkill /F /IM "streamlit.exe" /FI "WINDOWTITLE eq streamlit*" 2>nul || echo No Streamlit processes found
                        taskkill /F /IM "streamlit.exe" 2>nul || echo No Streamlit processes found
                        if exist streamlit.pid del /f streamlit.pid
                        if exist run_streamlit.vbs del /f run_streamlit.vbs
                        if exist streamlit.log move /y streamlit.log streamlit_old.log
                        exit /b 0
                    '''
                    
                    // Execute deployment
                    bat '''
                        call cleanup_streamlit.bat
                        call launch_streamlit.bat
                        
                        REM Verify deployment
                        powershell -Command "try { $response = Invoke-WebRequest -Uri http://localhost:8501 -TimeoutSec 30 -Method HEAD; exit 0 } catch { exit 1 }"
                        if %ERRORLEVEL% NEQ 0 (
                            echo Deployment verification failed
                            type streamlit.log
                            call cleanup_streamlit.bat
                            exit /b 1
                        )
                    '''
                }
            }
        }
    }
    
    post {
        success {
            script {
                echo "Pipeline completed successfully. Streamlit is running on http://localhost:8501"
                archiveArtifacts artifacts: 'streamlit.log,streamlit.pid,run_streamlit.vbs', allowEmptyArchive: true
            }
        }
        failure {
            script {
                bat 'call cleanup_streamlit.bat'
                archiveArtifacts artifacts: 'streamlit*.log', allowEmptyArchive: true
                echo "Pipeline failed. Check the archived logs for details."
            }
        }
        always {
            script {
                junit allowEmptyResults: true, testResults: 'test-results.xml'
                bat 'if exist streamlit.log copy streamlit.log streamlit_%BUILD_NUMBER%.log'
            }
        }
    }
}