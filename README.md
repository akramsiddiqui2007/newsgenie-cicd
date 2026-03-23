# NewsGenie

An agentic AI news assistant with a containerized application, Docker-based delivery, and an end-to-end CI/CD pipeline for automated build and deployment.

## Table of Contents

- [Project Overview](#project-overview)
- [What This Project Solves](#what-this-project-solves)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [How the Agent Works](#how-the-agent-works)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Local Setup](#detailed-local-setup)
- [Environment Variables](#environment-variables)
- [Run with Docker](#run-with-docker)
- [Run Tests](#run-tests)
- [CI/CD Pipeline Overview](#cicd-pipeline-overview)
- [Deployment Flow](#deployment-flow)
- [GitHub Setup and Push Instructions](#github-setup-and-push-instructions)
- [Security and Secret Handling](#security-and-secret-handling)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Project Overview

**NewsGenie** is an agentic AI news assistant designed to process news-oriented user questions through a multi-step workflow instead of a single direct model call. The application routes the query, rewrites it for better retrieval, expands intent where needed, retrieves relevant content, and synthesizes a structured answer.

The project is productionized with:

- a dedicated application folder under `app/`
- Docker containerization
- GitLab CI/CD automation
- Ansible-based deployment
- deployment to a GCP VM
- a working build-and-deploy flow using a shell runner tagged `gcp-shell`

This repository keeps the **application code, Docker setup, Ansible deployment code, and CI/CD pipeline together** so the full system is versioned in one place.

## What This Project Solves

Most demo AI apps stop at local execution. This project goes further by showing how to:

- build an agentic AI application
- package it in Docker
- automate builds and image publishing
- deploy it using infrastructure automation
- keep app and deployment code versioned together
- make onboarding easier through clear documentation

That makes NewsGenie both a useful application and a strong portfolio-grade engineering project.

## Key Features

- Agentic query workflow for news use cases
- Query routing by type/category
- Query rewriting for better retrieval quality
- Query expansion for broader coverage
- Resilience-oriented test flow
- Dockerized application packaging
- Automated image build and push
- Automated deployment to GCP VM
- GitLab CI/CD pipeline with separate build and deploy stages
- Ansible-driven deployment logic

## Architecture Overview

### Application flow

1. User submits a news query
2. The app classifies the query
3. The query is rewritten for better retrieval
4. The query is expanded with additional context if needed
5. Relevant content is retrieved
6. A final synthesized response is produced

### Deployment flow

1. Code is pushed to the repository
2. GitLab CI pipeline starts on the `main` branch
3. Docker image is built from `./app`
4. The image is pushed to Docker Hub
5. Ansible deploys the latest container version to the GCP VM

### Current working CI/CD pattern

This project currently uses the following working pattern:

- Docker image is built from the repository's `app/` directory
- GitLab Runner uses the `gcp-shell` tag
- deployment runs against the GCP VM
- Ansible is used during deploy
- SSH key flow uses `~/.ssh/newsgenie_oci`
- CI/CD definition is maintained in `.gitlab-ci.yml`

## Repository Structure

```text
newsgenie/
├── app/                         # application source code and Docker build context
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── src/
│   └── tests/
├── ansible/                     # deployment playbooks and inventory examples
│   ├── deploy.yml
│   ├── inventory/
│   │   ├── README.md
│   │   └── hosts.example
│   └── roles/
├── docs/
│   ├── cicd.md
│   ├── architecture.md
│   └── images/
├── .gitlab-ci.yml
├── .gitignore
├── .env.example
└── README.md
```

> Keep the pipeline **in the same repository** as the app.  
> The pipeline, Docker image, and Ansible deployment are all part of the same deliverable.

## Technology Stack

### Application
- Python
- Agentic AI workflow
- LLM integration
- retrieval and summarization logic
- test modules for resilience and flow validation

### DevOps and Deployment
- Docker
- GitLab CI/CD
- Ansible
- Docker Hub
- GCP VM
- shell runner tagged `gcp-shell`

## How the Agent Works

The NewsGenie workflow is structured in stages.

### 1. Route Query
The incoming request is first classified into a type and category so that the app knows how to process it.

### 2. Rewrite Query
The original user input is rewritten into a more retrieval-friendly version. This improves relevance and precision.

### 3. Expand Query
The system broadens the rewritten query by adding supporting context, alternate terms, or related scope.

### 4. Retrieve Information
The app retrieves relevant content using the optimized query representation.

### 5. Synthesize Response
The final response is generated from the retrieved material in a user-friendly structure.

## Prerequisites

Before running this project, make sure you have:

- Python 3.10 or newer
- Git
- Docker
- access to any required API keys
- GitLab project access if using CI/CD
- Docker Hub account for pushing images
- GCP VM access for deployment
- Ansible installed for manual deployments

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/newsgenie.git
cd newsgenie
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
cp .env.example .env
python app/main.py
```

If your app is Streamlit-based:

```bash
streamlit run app/main.py
```

## Detailed Local Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/newsgenie.git
cd newsgenie
```

### Step 2: Create a virtual environment

#### Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Python dependencies

```bash
pip install -r app/requirements.txt
```

### Step 4: Create environment file

#### Linux/macOS
```bash
cp .env.example .env
```

#### Windows PowerShell
```powershell
Copy-Item .env.example .env
```

### Step 5: Add your environment values

Open `.env` and set your real values.

Example:

```env
OPENAI_API_KEY=your_api_key_here
NEWS_API_KEY=your_news_api_key_here
APP_ENV=development
PORT=8501
```

### Step 6: Start the app

```bash
python app/main.py
```

Or, if applicable:

```bash
streamlit run app/main.py
```

## Environment Variables

Keep a safe template file in the repo as `.env.example`.

Recommended structure:

```env
OPENAI_API_KEY=your_api_key_here
NEWS_API_KEY=your_news_api_key_here
APP_ENV=development
PORT=8501
```

### Important
- Never commit `.env`
- Never commit real API keys
- Keep only example templates in GitHub

## Run with Docker

### Build the image

```bash
docker build -t newsgenie:latest ./app
```

### Run the container

```bash
docker run --env-file .env -p 8501:8501 newsgenie:latest
```

Adjust the port if your app uses a different one.

### Verify the container

```bash
docker ps
```

## Run Tests

From the project root:

```bash
python -m pytest
```

For targeted tests:

```bash
python -m tests.test_step11_resilience
```

Update the command if your actual test path differs.

## CI/CD Pipeline Overview

This project uses **GitLab CI/CD** with two main stages:

- `build`
- `deploy`

### Build stage
The build stage:

- runs on a runner tagged `gcp-shell`
- logs into Docker Hub
- builds the Docker image from `./app`
- tags the image with commit SHA and `latest`
- pushes both images to Docker Hub

### Deploy stage
The deploy stage:

- runs on the same tagged runner
- prepares Python/Ansible environment
- uses `~/.ssh/newsgenie_oci`
- runs the Ansible deployment playbook
- updates the running container on the GCP VM

For full details, see [`docs/cicd.md`](docs/cicd.md).

## Deployment Flow

The current working deployment model is:

1. Push code to `main`
2. GitLab starts pipeline
3. Docker image is built from `./app`
4. Image is pushed to Docker Hub
5. Ansible connects to the deployment target
6. The target host pulls the new image
7. Existing container is replaced with the latest one

### Manual deployment example

```bash
cd ansible
ansible-playbook -i inventory/hosts deploy.yml
```

Use a sanitized or local private inventory file that is not committed to GitHub.

## GitHub Setup and Push Instructions

### Step 1: Clean the repository

Make sure the repo does **not** contain:

- `.venv/`
- `.env`
- SSH private keys
- Docker credentials
- local logs
- cache directories
- sensitive inventory files

### Step 2: Check `.gitignore`

Ensure your `.gitignore` excludes local and secret files.

### Step 3: Initialize Git if needed

```bash
git init
```

### Step 4: Add files

```bash
git add .
```

### Step 5: Commit

```bash
git commit -m "Initial commit: NewsGenie app, Docker, CI/CD, docs, and deployment automation"
```

### Step 6: Create GitHub repo

Create a new GitHub repository named `newsgenie`.

### Step 7: Add remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/newsgenie.git
```

### Step 8: Push

```bash
git branch -M main
git push -u origin main
```

## Security and Secret Handling

Do not commit any of the following:

- `.env`
- SSH private keys
- cloud credentials
- Docker Hub tokens
- real server IPs if they are sensitive
- unmasked inventory files
- local runner secrets

Use safe placeholders such as:

- `.env.example`
- `ansible/inventory/hosts.example`

## Troubleshooting

### Virtual environment activation fails
Check that Python is installed and available on your system path.

### Docker build fails
Confirm that:
- `app/Dockerfile` exists
- `app/requirements.txt` is correct
- the build context is `./app`

### CI pipeline cannot log in to Docker Hub
Check:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `IMAGE_NAME`

### SSH key permission issue
Run:

```bash
chmod 600 ~/.ssh/newsgenie_oci
```

### Ansible cannot connect to the deployment host
Check:
- VM IP and host name
- SSH username
- firewall rules
- private key path
- inventory settings

## Future Improvements

- add architecture diagrams under `docs/images/`
- add monitoring and logging
- add rollback support in deployment
- add post-deploy smoke tests
- add environment-specific deployment profiles
- add GitHub Actions variant if needed
- add Kubernetes deployment option

## Author

Akram Siddiqui

## License

Add your preferred license here.

## Additional Documentation

- [Architecture](docs/architecture.md)
- [CI/CD](docs/cicd.md)
