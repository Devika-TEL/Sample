pipeline {
    agent any

    environment {
        VENV_PATH = "${WORKSPACE}/venv"
        STREAMLIT_PORT = '8501'
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    sh """
                        python3.11 -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        python3.11 -m pip install --upgrade pip setuptools wheel
                        pip install streamlit==1.31.0 -v
                    """
                }
            }
        }

        stage('Run Streamlit App') {
            steps {
                script {
                    sh """
                        
                        # Activate virtual environment and run Streamlit
                        . ${VENV_PATH}/bin/activate
                        nohup streamlit run app.py --server.port=${STREAMLIT_PORT} --server.address=10.120.12.188 > streamlit.log 2>&1 &
                        echo \$! > streamlit.pid
                        sleep 10
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sh """
                        curl -s 10.120.12.188:${STREAMLIT_PORT} > /dev/null
                        if [ \$? -eq 0 ]; then
                            echo "Streamlit app is running successfully"
                        else
                            echo "Failed to start Streamlit app"
                            exit 1
                        fi
                    """
                }
            }
        }
        stage('Keep Build Running') {
            steps {
                script {
                    sh 'while true; do sleep 1d; done'
                }
            }
        }
    }

    post {
        success {
            script {
                sh """
                    echo "Streamlit app is running on 10.120.12.188:${STREAMLIT_PORT}"
                    cat streamlit.pid
                """
            }
        }
    }
}
