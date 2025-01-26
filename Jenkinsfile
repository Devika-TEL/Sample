pipeline {
    agent any
    
    environment {
        VENV_PATH = "${WORKSPACE}/venv"
        STREAMLIT_PORT = '8501'
        SERVICE_NAME = 'streamlit-app'
    }
    
    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    sh """
                        # Ensure necessary directories exist
                        mkdir -p ${WORKSPACE}
                        mkdir -p ${VENV_PATH}
                    """
                }
            }
        }
        
        stage('Checkout Code') {
            steps {
                // Checkout from Git repository
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    sh """
                        # Create virtual environment
                        python3.11 -m venv ${VENV_PATH}
                        
                        # Activate virtual environment and upgrade pip
                        . ${VENV_PATH}/bin/activate
                        pip install --upgrade pip setuptools wheel
                        
                        # Install requirements
                        pip install streamlit==1.31.0 -v
                        pip install -r requirements.txt
                    """
                }
            }
        }
        
        stage('Create Systemd Service File') {
            steps {
                script {
                    sh """
                        # Create systemd service file
                        cat > ${WORKSPACE}/${SERVICE_NAME}.service << EOL
[Unit]
Description=Streamlit Application
After=network.target

[Service]
Type=simple
User=jenkins
WorkingDirectory=${WORKSPACE}
Environment="PATH=${VENV_PATH}/bin"
ExecStart=${VENV_PATH}/bin/streamlit run ${WORKSPACE}/app.py --server.port=${STREAMLIT_PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL
                    """
                }
            }
        }
        
        stage('Deploy Streamlit Service') {
            steps {
                script {
                    sh """
                        # Stop existing service if running
                        sudo systemctl stop ${SERVICE_NAME} || true
                        
                        # Copy service file to systemd directory
                        sudo cp ${WORKSPACE}/${SERVICE_NAME}.service /etc/systemd/system/
                        
                        # Reload systemd, enable, and restart service
                        sudo systemctl daemon-reload
                        sudo systemctl enable ${SERVICE_NAME}
                        sudo systemctl restart ${SERVICE_NAME}
                    """
                }
            }
        }
        
        stage('Verify Service') {
            steps {
                script {
                    sh """
                        # Check service status
                        sudo systemctl status ${SERVICE_NAME}
                        
                        # Verify port is listening
                        sleep 10
                        netstat -tuln | grep :${STREAMLIT_PORT}
                        
                        # Health check via curl
                        curl -s http://localhost:${STREAMLIT_PORT} > /dev/null
                    """
                }
            }
        }
    }
    
    post {
        success {
            script {
                sh """
                    echo "Streamlit application deployed successfully"
                    echo "Access at: http://localhost:${STREAMLIT_PORT}"
                """
            }
        }
        
        failure {
            script {
                sh """
                    echo "Deployment failed. Checking logs..."
                    sudo journalctl -u ${SERVICE_NAME}
                """
            }
        }
    }
}
