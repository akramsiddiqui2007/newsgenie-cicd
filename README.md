````markdown
# NewsGenie CI/CD

NewsGenie is an agentic AI news assistant that routes, rewrites, expands, retrieves, and synthesizes news-related queries. This repository contains the full project in a single repo, including the application, Docker setup, GitLab CI/CD pipeline, deployment automation, infrastructure templates, and project documentation.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Repository Structure](#repository-structure)
4. [Architecture Summary](#architecture-summary)
5. [Tech Stack](#tech-stack)
6. [Prerequisites](#prerequisites)
7. [Environment Variables](#environment-variables)
8. [Run the App Locally](#run-the-app-locally)
9. [Run with Docker](#run-with-docker)
10. [CI/CD Pipeline Overview](#cicd-pipeline-overview)
11. [GitLab CI/CD Setup](#gitlab-cicd-setup)
12. [Deployment with Ansible](#deployment-with-ansible)
13. [Terraform Notes](#terraform-notes)
14. [How to Trigger the Pipeline](#how-to-trigger-the-pipeline)
15. [How to Verify Deployment](#how-to-verify-deployment)
16. [Troubleshooting](#troubleshooting)
17. [Security Notes](#security-notes)
18. [Additional Documentation](#additional-documentation)
19. [License](#license)

---

## Project Overview

NewsGenie is built as an agentic AI application for news workflows. Instead of sending every user input directly into a model in a single step, the application uses a structured workflow to improve response quality and resilience.

The project includes:

- application code under `app/`
- Docker containerization
- GitLab CI/CD pipeline
- Ansible deployment automation
- Terraform example configuration
- documentation for architecture and CI/CD

This repo is intentionally organized as a **single repository** so that application code, build logic, deployment automation, and documentation all evolve together.

---

## Key Features

- agentic workflow for news queries
- query routing and classification
- query rewriting and expansion
- multiple model client integrations
- news retrieval and web search tool integrations
- Streamlit-based user interface
- Dockerized application runtime
- GitLab CI/CD pipeline for build and deployment
- Ansible-based deployment flow
- infrastructure-ready repository structure

---

## Repository Structure

```text
newsgenie-cicd/
├── app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── src/
│       ├── config.py
│       ├── prompts.py
│       ├── state.py
│       ├── graph/
│       ├── models/
│       ├── tools/
│       └── utils/
├── ansible/
│   ├── inventory/
│   │   ├── README.md
│   │   └── hosts.example
│   └── vars.example.yml
├── docs/
│   ├── architecture.md
│   └── cicd.md
├── terraform/
│   └── terraform.tfvars.example
├── .env.example
├── .gitignore
├── .gitlab-ci.yml
├── README.md
└── LICENSE
````

---

## Architecture Summary

At a high level, NewsGenie follows this flow:

1. user submits a query in the Streamlit interface
2. workflow logic classifies and routes the query
3. query may be rewritten for better retrieval quality
4. query may be expanded with additional context
5. news and web retrieval tools are invoked
6. retrieved content is filtered and synthesized
7. model client generates the final answer
8. UI presents the result back to the user

Main entry point:

* `app/app.py`

Core workflow:

* `app/src/graph/workflow.py`

Model integrations:

* `app/src/models/openai_client.py`
* `app/src/models/gemini_client.py`

Tool integrations:

* `app/src/tools/news_api.py`
* `app/src/tools/web_search.py`

Detailed architecture notes are available in [docs/architecture.md](docs/architecture.md).

---

## Tech Stack

### Application

* Python
* Streamlit
* OpenAI client integration
* Gemini client integration

### DevOps and Deployment

* Docker
* GitLab CI/CD
* Ansible
* Terraform
* Docker Hub
* GCP VM deployment target

---

## Prerequisites

Before running this project, make sure you have:

* Python 3.10 or above
* `pip`
* Docker installed
* Git installed
* a valid OpenAI API key
* any required news API key used by the app
* GitLab Runner access for CI/CD
* Docker Hub repository for pushed images
* target VM access for deployment

---

## Environment Variables

Create a local `.env` file from the example file.

### Example

```bash
cp .env.example .env
```

Typical contents:

```env
OPENAI_API_KEY=your_real_openai_api_key
NEWS_API_KEY=your_real_news_api_key
APP_ENV=development
PORT=8501
```

Important notes:

* do not commit `.env`
* do not surround keys with unnecessary quotes unless your parser requires it
* use a valid active OpenAI key
* keep production secrets in secure secret storage, not in git

---

## Run the App Locally

### 1. Clone the repository

```bash
git clone https://github.com/akramsiddiqui2007/newsgenie-cicd.git
cd newsgenie-cicd
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r app/requirements.txt
```

### 4. Create your local `.env`

```bash
cp .env.example .env
nano .env
```

Add your real keys and save the file.

### 5. Start the app

This project uses Streamlit.

```bash
streamlit run app/app.py
```

### 6. Open in browser

```text
http://localhost:8501
```

---

## Run with Docker

### 1. Build the image

Important: the Docker build context is the `app/` directory.

```bash
docker build -t newsgenie:latest ./app
```

### 2. Run the container

```bash
docker run --rm --env-file .env -p 8501:8501 newsgenie:latest
```

### 3. Open the app

```text
http://localhost:8501
```

### 4. What successful startup looks like

You should see output similar to:

* Streamlit app starts successfully
* Local URL is shown
* no API key authentication error
* app responds to queries

---

## CI/CD Pipeline Overview

This project uses **GitLab CI/CD** for build and deployment automation.

Pipeline file:

* `.gitlab-ci.yml`

Current flow:

1. code is pushed to the `main` branch
2. GitLab pipeline starts
3. Docker image is built from `./app`
4. image is tagged with commit SHA and `latest`
5. image is pushed to Docker Hub
6. Ansible deployment runs against the target VM

Pipeline stages:

* `build`
* `deploy`

---

## GitLab CI/CD Setup

### 1. Runner requirement

Your GitLab Runner must be active and tagged as:

```text
gcp-shell
```

### 2. Required GitLab CI/CD variables

Configure these in:

**GitLab → Settings → CI/CD → Variables**

Required variables:

* `DOCKERHUB_USERNAME`
* `DOCKERHUB_TOKEN`
* `IMAGE_NAME`

Example:

```text
IMAGE_NAME=docker.io/yourdockerhubusername/newsgenie
```

### 3. Current pipeline pattern

The current pipeline builds the image from:

```bash
./app
```

and uses a shell runner tagged:

```text
gcp-shell
```

### 4. Example pipeline behavior

Build stage:

* logs in to Docker Hub
* builds Docker image from `./app`
* tags image with commit SHA
* tags image as `latest`
* pushes both tags

Deploy stage:

* prepares Python virtual environment
* installs Ansible
* uses SSH key on runner host
* runs Ansible playbook

### 5. Current pipeline file

Your repo contains:

* `.gitlab-ci.yml`

The pipeline should remain versioned in the same repo as the app.

### 6. Example `.gitlab-ci.yml`

Below is the working structure used in this project:

```yaml
stages:
  - build
  - deploy

variables:
  APP_IMAGE: "$IMAGE_NAME:$CI_COMMIT_SHORT_SHA"
  APP_IMAGE_LATEST: "$IMAGE_NAME:latest"

build_and_push_image:
  stage: build
  tags:
    - gcp-shell
  script:
    - cd "$CI_PROJECT_DIR"
    - echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
    - docker build -t "$APP_IMAGE" -t "$APP_IMAGE_LATEST" ./app
    - docker push "$APP_IMAGE"
    - docker push "$APP_IMAGE_LATEST"
  only:
    - main

deploy_to_gcp_vm:
  stage: deploy
  tags:
    - gcp-shell
  before_script:
    - cd "$CI_PROJECT_DIR"
    - chmod 600 ~/.ssh/newsgenie_oci
    - python3 -m venv .venv
    - source .venv/bin/activate
    - pip install --upgrade pip
    - pip install ansible
  script:
    - ansible-playbook -i ansible/inventory/hosts.example ansible/deploy.yml
  only:
    - main
```

### 7. Notes about the deployment command

The current checked-in pipeline uses:

```bash
ansible-playbook -i ansible/inventory/hosts.example ansible/deploy.yml
```

That is acceptable as a documented example, but for a real deployment you should use a real inventory file on the runner host, not `hosts.example`.

A production-style command would look like:

```bash
ansible-playbook -i ansible/inventory/hosts ansible/deploy.yml
```

---

## Deployment with Ansible

This repository includes Ansible-related files and examples under:

* `ansible/`

Inventory examples:

* `ansible/inventory/hosts.example`
* `ansible/inventory/README.md`

Vars example:

* `ansible/vars.example.yml`

### Important

Do not commit:

* real inventory files
* live VM IPs if sensitive
* private keys
* secret vars files such as `ansible/vars.yml`

### Example deployment command

For a real deployment setup, the command will look like:

```bash
ansible-playbook -i ansible/inventory/hosts ansible/deploy.yml
```

If you are using an example inventory for documentation/testing only:

```bash
ansible-playbook -i ansible/inventory/hosts.example ansible/deploy.yml
```

Use a real inventory file on the runner or deployment host for actual deployments.

---

## Terraform Notes

Terraform example values are kept in:

* `terraform/terraform.tfvars.example`

Do not commit:

* `.terraform/`
* `*.tfstate`
* `*.tfstate.*`
* `.terraform.lock.hcl` if you do not want environment-specific lock tracking
* live `terraform.tfvars` with secrets

This repository is configured to keep local Terraform artifacts out of git.

---

## How to Trigger the Pipeline

### 1. Make a small code change

Example: update a Streamlit title or caption in:

* `app/app.py`

### 2. Test locally first

```bash
docker build -t newsgenie:latest ./app
docker run --rm --env-file .env -p 8501:8501 newsgenie:latest
```

Open:

```text
http://localhost:8501
```

### 3. Commit and push

```bash
git add .
git commit -m "Small UI update"
git push origin main
```

### 4. Watch the GitLab pipeline

Confirm:

* build job starts
* image builds successfully
* image pushes to Docker Hub
* deploy job starts
* deploy job completes successfully

---

## How to Verify Deployment

After the pipeline runs:

### 1. Check GitLab job logs

Verify:

* Docker build completed
* Docker push completed
* Ansible deployment completed

### 2. Check Docker Hub

Confirm:

* new image tag with commit SHA exists
* `latest` tag is updated

### 3. Check the target VM

SSH into the VM and run:

```bash
docker ps
docker images
docker logs <container_id>
```

### 4. Check the deployed application

Open the deployed URL in browser and confirm the latest code change is visible.

---

## Troubleshooting

### App starts but API calls fail with 401

Cause:

* invalid or revoked API key

Fix:

* update `.env`
* confirm correct variable names
* restart the container

### Streamlit starts locally but Docker fails

Check:

* `app/Dockerfile`
* `app/requirements.txt`
* correct port mapping
* correct env file passed to container

### GitHub push blocked by secrets

Cause:

* secrets were committed into repo history

Fix:

* remove secret from tracked files
* rewrite history if needed
* rotate the exposed secret

### GitHub push blocked by large Terraform/provider files

Cause:

* `.terraform/` or provider binaries were committed

Fix:

* remove them from git
* ignore Terraform local artifacts
* recommit clean files only

### GitLab runner does not pick up jobs

Check:

* runner is online
* runner has the `gcp-shell` tag
* project is allowed to use the runner

### Docker login fails in pipeline

Check:

* `DOCKERHUB_USERNAME`
* `DOCKERHUB_TOKEN`
* `IMAGE_NAME`

### Deploy job fails

Check:

* SSH key exists on runner
* SSH key has correct permissions
* Ansible can run on runner
* inventory path is correct
* target VM is reachable

---

## Security Notes

This repo intentionally keeps secret-bearing files out of version control.

Safe example files committed:

* `.env.example`
* `ansible/vars.example.yml`
* `ansible/inventory/hosts.example`
* `terraform/terraform.tfvars.example`

Do not commit:

* `.env`
* `ansible/vars.yml`
* real inventory files
* SSH private keys
* Terraform state files
* Docker auth credentials

If a secret was ever committed, rotate it immediately.

---

## Additional Documentation

* [Architecture](docs/architecture.md)
* [CI/CD](docs/cicd.md)

---

## License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.

```
```

