
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        IMAGE_NAME = 'taskflow:latest'
        CONTAINER_NAME = 'taskflow'
        HOST_PORT = '8501'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out TaskFlow from GitHub.'
                checkout scm
            }
        }

        stage('Install Dependencies') {
    steps {
        bat '''@echo off
echo Creating Python virtual environment...

"C:/Users/lenovo/AppData/Local/Programs/Python/Python313/python.exe" -m venv .venv
if errorlevel 1 exit /b 1

echo Installing dependencies...

.venv/Scripts/python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

.venv/Scripts/python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Dependencies installed successfully.
'''
    }
}

        stage('Test') {
            steps {
                bat '''@echo off
echo Running TaskFlow automated tests...
.venv/Scripts/python.exe -m pytest -q
if errorlevel 1 (
    echo ERROR: Automated tests failed.
    exit /b 1
)
echo All tests passed.
'''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''@echo off
echo Checking Docker availability...
where docker
if errorlevel 1 (
    echo ERROR: Docker CLI not found.
    exit /b 1
)

docker version
if errorlevel 1 (
    echo ERROR: Docker daemon is unavailable.
    exit /b 1
)

echo Building TaskFlow Docker image...
docker build -t "%IMAGE_NAME%" .
if errorlevel 1 (
    echo ERROR: Docker image build failed.
    exit /b 1
)

echo Docker image built successfully.
'''
            }
        }

        stage('Deploy') {
            steps {
                bat '''@echo off
echo Checking existing TaskFlow container...
docker inspect "%CONTAINER_NAME%" >NUL 2>&1

if not errorlevel 1 (
    echo Removing previous TaskFlow container...
    docker rm -f "%CONTAINER_NAME%"
    if errorlevel 1 exit /b 1
)

echo Deploying TaskFlow...
docker run -d --name "%CONTAINER_NAME%" --restart unless-stopped -p "%HOST_PORT%:8501" -v taskflow-data:/data "%IMAGE_NAME%"

if errorlevel 1 (
    echo ERROR: Deployment failed.
    exit /b 1
)

echo TaskFlow deployment started.
echo Application URL: http://localhost:%HOST_PORT%
'''
            }
        }
    }

    post {
        success {
            echo 'TaskFlow CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'TaskFlow pipeline failed. Check the console output.'
        }

        always {
            echo 'TaskFlow pipeline execution finished.'
        }
    }
}
