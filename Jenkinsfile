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
                    sh "python${PYTHON_VERSION} -m venv venv"
                    sh "source venv/bin/activate && pip install --upgrade pip"
                    sh "source venv/bin/activate && pip install -r requirements.txt"
                }
            }
        }

        stage('Run Streamlit App') {
            steps {
                script {
                    // Clean up any existing Streamlit process
                    sh '''
                    if [ -f ${STREAMLIT_PID_FILE} ]; then
                        kill $(cat ${STREAMLIT_PID_FILE}) || true
                        rm -f ${STREAMLIT_PID_FILE}
                    fi
                    '''

                    // Start the Streamlit app
                    sh '''
                    source venv/bin/activate && \
                    streamlit run app.py --server.port=${STREAMLIT_PORT} > streamlit.log 2>&1 &
                    echo $! > ${STREAMLIT_PID_FILE}
                    '''
                }
            }
        }

        stage('Test Application') {
            steps {
                script {
                    // Add your application tests here
                    echo 'Running tests...'
                    sh "curl -f http://localhost:${STREAMLIT_PORT} || exit 1"
                }
            }
        }
    }

    post {
        always {
            script {
                // Stop the Streamlit process after the build
                sh '''
                if [ -f ${STREAMLIT_PID_FILE} ]; then
                    kill $(cat ${STREAMLIT_PID_FILE}) || true
                    rm -f ${STREAMLIT_PID_FILE}
                fi
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
