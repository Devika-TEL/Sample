pipeline {
    agent any
    
    environment {
        // Set Python virtual environment path
        VENV_PATH = "${WORKSPACE}/venv"
        // Streamlit port
        STREAMLIT_PORT = '8051'
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Checkout your source code
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    // Create virtual environment
                    sh '''
                        python3.11 -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        python3.11 -m pip install --upgrade pip setuptools wheel
                        pip install streamlit==1.31.0 -v
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Streamlit App') {
            steps {
                script {
                    // Kill any existing Streamlit processes on the specified port
                    sh """
                        # Find and kill any process using the Streamlit port
                        lsof -ti :${STREAMLIT_PORT} | xargs -r kill -9 || true
                    """
                    
                    // Run Streamlit in the background and save the PID
                    sh """
                        . ${VENV_PATH}/bin/activate
                        nohup streamlit run your_app.py --server.port=${STREAMLIT_PORT} > streamlit.log 2>&1 &
                        echo \$! > streamlit.pid
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    // Wait a moment for the app to start
                    sh 'sleep 10'
                    
                    // Check if the app is running
                    sh """
                        if curl -s http://localhost:${STREAMLIT_PORT} > /dev/null; then
                            echo "Streamlit app is running successfully"
                        else
                            echo "Failed to start Streamlit app"
                            exit 1
                        fi
                    """
                }
            }
        }
    }
    
    post {
        success {
            script {
                // Print out the PID for reference
                sh 'cat streamlit.pid'
                echo "Streamlit app is running on http://localhost:${STREAMLIT_PORT}"
            }
        }
        
        cleanup {
            script {
                // Optional: Ensure the Streamlit app continues running
                // This step prevents the process from being killed after the pipeline
                sh '''
                    # Detach the process from the Jenkins job
                    disown $(cat streamlit.pid)
                '''
            }
        }
    }
}
