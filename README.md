# TaskFlow

TaskFlow is a lightweight task management dashboard built with Python and Streamlit. It stores tasks in a local SQLite database and includes a dashboard, task editing workflow, and simple analytics. The repository also demonstrates a Docker image, a Jenkins CI/CD pipeline, and local container provisioning with Terraform.

## Features

- Dashboard totals, completion percentage, status chart, and recent tasks.
- Create, search, filter, edit, complete, and delete tasks.
- Priority and due date tracking with input validation and delete confirmation.
- Status and priority analytics using Plotly.
- Persistent SQLite storage, including a Docker volume for container deployments.

## Technology stack

Python 3.11+, Streamlit, SQLite, Pandas, Plotly, Pytest, Docker, Jenkins, and Terraform with the `kreuzwerker/docker` provider. No remote services or credentials are required.

## Project structure

```text
app.py                 Streamlit pages and UI
database.py            SQLite persistence functions
task_logic.py          Validation and completion calculations
tests/                 Database and application logic tests
scripts/healthcheck.py HTTP health probe used by Docker
Dockerfile             Container image definition
Jenkinsfile            Declarative CI/CD pipeline
terraform/             Local Docker image and container resources
```

## Prerequisites

- Python 3.11 or newer for local development.
- Docker Engine and Docker CLI for container workflows.
- For the checked-in Jenkins pipeline: Jenkins running natively on Windows, the Python launcher (`py`) with Python 3, Docker CLI, and a Jenkins service account that can access the Docker daemon.
- Terraform 1.3 or newer for the optional Terraform deployment.

## Run locally

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open <http://localhost:8501>. By default the app creates `taskflow.db` beside the application. Set `TASKFLOW_DB_PATH` to choose another database location, for example `export TASKFLOW_DB_PATH="$PWD/data/taskflow.db"`.

## Run tests

```bash
python -m pytest
```

Database tests use temporary SQLite files and do not touch the application database.

## Docker

Build and run with the requested commands:

```bash
docker build -t taskflow:latest .
docker run -d --name taskflow -p 8501:8501 taskflow:latest
```

Open <http://localhost:8501>. The image runs as an unprivileged user and checks Streamlit's health endpoint. For data that survives container replacement, mount a volume:

```bash
docker run -d --name taskflow -p 8501:8501 -v taskflow-data:/data taskflow:latest
```

The container stores its database at `/data/taskflow.db`. To stop and remove the container, run `docker rm -f taskflow`.

## Jenkins CI/CD

Create a Pipeline job in Jenkins, connect it to this Git repository, and configure the `main` branch. The checked-in `Jenkinsfile` targets a native Windows Jenkins built-in node: it uses `checkout scm` exactly once, creates `.venv` with `py -3`, installs dependencies and runs pytest through `.venv\Scripts\python.exe`, builds `taskflow:latest` with Docker CLI, then safely removes and replaces the local `taskflow` container on host port 8501. It mounts the named `taskflow-data` volume so deployments keep application data. Failed tests, missing Docker CLI, Docker daemon access errors, image build errors, and deployment errors fail the pipeline.

The Jenkins Windows service account must have Python and Docker available on its PATH and permission to use the Docker daemon. For Docker Desktop, verify Docker Desktop is running and grant that account access to the Docker Desktop engine (including any required `docker-users` membership), then restart the Jenkins service so it receives the updated account permissions. The pipeline checks `docker version` before building; a CLI installation alone does not prove that the service account can reach the daemon.

The pipeline is declarative and requires no credentials unless your Git source itself requires them; configure those in Jenkins' SCM settings rather than in the repository. Run **Build Now** (or enable a webhook/polling trigger in the job configuration) and inspect the stage output in **Console Output**. The deploy stage removes a same-named prior container and starts the image only after tests and image build succeed.

## Terraform deployment

Terraform manages a local Docker container. First build the image locally; Terraform expects the image to exist on the Docker daemon it is configured to use:

```bash
docker build -t taskflow:latest .
cd terraform
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Confirm the apply prompt when ready. Terraform reports the container name and URL (`http://localhost:8501`). To remove its container, run:

```bash
terraform destroy
```

Set values with flags such as `terraform apply -var="application_name=taskflow-demo" -var="host_port=8502"`. Jenkins deployment and Terraform deployment are alternative methods: do not have both manage a container with the same name/port at the same time. Their container state is managed independently.

## Architecture and workflow

The Streamlit UI calls small functions in `database.py`; that module owns SQLite initialization and parameterized database operations. `task_logic.py` contains testable validation and summary calculations. Pandas prepares chart/table data and Plotly renders the charts. Locally, SQLite writes to the project directory; in Docker it writes into `/data`, which can be backed by a named volume. Jenkins checks out, installs, tests, builds, and deploys. Terraform declares the local Docker image/container resources separately.

## Screenshots

Add screenshots of the Dashboard, Tasks page, and Analytics page here after launching the app. Suggested files: `docs/screenshots/dashboard.png`, `docs/screenshots/tasks.png`, and `docs/screenshots/analytics.png`.
