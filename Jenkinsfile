pipeline {
    agent any
    options { timestamps() }
    environment {
        IMAGE_NAME = 'taskflow:latest'
        CONTAINER_NAME = 'taskflow'
        HOST_PORT = '8501'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install --upgrade pip'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps { sh '.venv/bin/python -m pytest' }
        }
        stage('Build Docker Image') {
            steps { sh 'docker build -t "$IMAGE_NAME" .' }
        }
        stage('Deploy') {
            steps {
                sh '''
                    echo "Replacing local container $CONTAINER_NAME"
                    docker rm -f "$CONTAINER_NAME" || true
                    docker run -d --name "$CONTAINER_NAME" --restart unless-stopped \\
                        -p "$HOST_PORT:8501" -v taskflow-data:/data "$IMAGE_NAME"
                    echo "TaskFlow is deploying on port $HOST_PORT"
                '''
            }
        }
    }
    post {
        success { echo 'TaskFlow pipeline completed successfully.' }
        failure { echo 'TaskFlow pipeline failed. Review the stage output above.' }
    }
}
