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
                    bat "python -m venv venv"
                    bat "venv\\Scripts\\activate && python -m pip install --upgrade pip || exit 1"
                    bat "venv\\Scripts\\activate && pip install -r requirements.txt || exit 1"
                }
            }
        }

        stage('Run Streamlit App') {
    steps {
        script {
            // Clean up any existing Streamlit process
            bat '''
            if exist ${STREAMLIT_PID_FILE} (
                for /f %%i in (${STREAMLIT_PID_FILE}) do taskkill /PID %%i /F
                del ${STREAMLIT_PID_FILE}
            )
            '''

            // Start the Streamlit app in the background
            bat '''
            venv\\Scripts\\activate && start /B cmd /C "streamlit run app.py --server.port=${STREAMLIT_PORT} > streamlit.log 2>&1" && (echo %%ERRORLEVEL%% > ${STREAMLIT_PID_FILE})
            '''
        }
    }
}


        stage('Test Application') {
            steps {
                script {
                    // Add your application tests here
                    echo 'Running tests...'
                    bat "curl -f http://localhost:${STREAMLIT_PORT} || exit 1"
                }
            }
        }
    }

    post {
    always {
        script {
            // Stop the Streamlit process after the build
            bat '''
            if exist ${STREAMLIT_PID_FILE} (
                for /f %%i in (${STREAMLIT_PID_FILE}) do taskkill /PID %%i /F
                del ${STREAMLIT_PID_FILE}
            )
            '''
        }

        // Archive logs for debugging
        archiveArtifacts artifacts: 'streamlit.log', onlyIfSuccessful: false
    }

    success {
        echo 'Build and deployment successful!'
    }

    failure {
        echo 'Build failed. Check logs for details.'
    }
}
}
