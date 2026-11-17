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
                echo 'Checking out the configured repository and branch.'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''@echo off
echo Creating the project virtual environment with Python 3...
py -3 -m venv .venv
if errorlevel 1 (
    echo ERROR: Could not create .venv. Confirm the Python launcher and Python 3 are installed for the Jenkins service account.
    exit /b 1
)

echo Installing project dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    exit /b 1
)
'''
            }
        }

        stage('Test') {
            steps {
                bat '''@echo off
echo Running the TaskFlow pytest suite...
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 (
    echo ERROR: Tests failed. The pipeline will stop before building or deploying.
    exit /b 1
)
'''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''@echo off
echo Checking Docker CLI availability...
where docker
if errorlevel 1 (
    echo ERROR: Docker CLI was not found on the Jenkins agent PATH.
    exit /b 1
)

echo Checking Docker daemon access for the Jenkins service account...
docker version
if errorlevel 1 (
    echo ERROR: Docker CLI cannot reach the Docker daemon. Grant the Jenkins service account access to Docker Desktop or the configured Docker daemon, then restart the Jenkins service.
    exit /b 1
)

echo Building image %IMAGE_NAME%...
docker build -t "%IMAGE_NAME%" .
if errorlevel 1 (
    echo ERROR: Docker image build failed.
    exit /b 1
)
'''
            }
        }

        stage('Deploy') {
            steps {
                bat '''@echo off
echo Replacing the previous TaskFlow container, if present...
docker inspect "%CONTAINER_NAME%" >NUL 2>&1
if errorlevel 1 (
    echo No existing container named %CONTAINER_NAME% was found; continuing with a fresh deployment.
) else (
    docker rm -f "%CONTAINER_NAME%"
    if errorlevel 1 (
        echo ERROR: Could not remove the existing container %CONTAINER_NAME%.
        exit /b 1
    )
)

echo Starting %CONTAINER_NAME% on host port %HOST_PORT%...
docker run -d --name "%CONTAINER_NAME%" --restart unless-stopped -p "%HOST_PORT%:8501" -v taskflow-data:/data "%IMAGE_NAME%"
if errorlevel 1 (
    echo ERROR: TaskFlow container failed to start. Check the Docker output and port %HOST_PORT% availability.
    exit /b 1
)

echo TaskFlow deployment started. Open http://localhost:%HOST_PORT% after the container becomes healthy.
'''
            }
        }
    }

    post {
        success {
            echo 'TaskFlow pipeline completed successfully.'
        }
        failure {
            echo 'TaskFlow pipeline failed. Review the stage output above; failed tests and Docker errors are not ignored.'
        }
    }
}
