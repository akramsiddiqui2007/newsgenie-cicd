# CI/CD Pipeline Documentation

This document explains the working CI/CD and deployment model for the **NewsGenie** project.

## 1. Overview

NewsGenie uses GitLab CI/CD to automate image build, image publishing, and deployment.

The pipeline currently follows this pattern:

- source code lives in one repository
- the application lives under `app/`
- Docker image is built from `./app`
- the pipeline is defined in `.gitlab-ci.yml`
- GitLab jobs run on a shell runner tagged `gcp-shell`
- deployment uses Ansible
- SSH key flow uses `~/.ssh/newsgenie_oci`
- the target environment is a GCP VM

This is the right setup for this project because the app, image build, and deployment logic all belong to the same delivery unit.

## 2. Why App and CI/CD Are Kept Together

For NewsGenie, the recommended approach is to keep:

- app code
- Docker configuration
- Ansible deployment code
- CI/CD pipeline

in the **same repository**.

### Benefits
- one version history for the full project
- easier onboarding
- easier rollback and traceability
- simpler documentation
- app and deployment changes stay in sync

A separate CI/CD repository is only useful when one shared platform team manages many applications through a central deployment framework.

## 3. Pipeline Stages

The pipeline has two main stages:

```yaml
stages:
  - build
  - deploy
```

### Build stage
Builds and pushes the image.

### Deploy stage
Deploys the new image to the target host using Ansible.

## 4. Current Working Variables

Example variables from the current working pattern:

```yaml
variables:
  APP_IMAGE: "$IMAGE_NAME:$CI_COMMIT_SHORT_SHA"
  APP_IMAGE_LATEST: "$IMAGE_NAME:latest"
```

### Meaning
- `APP_IMAGE` creates a commit-specific image tag
- `APP_IMAGE_LATEST` maintains a rolling latest tag

This gives both traceability and a simple deployment reference.

## 5. Build Stage Details

The build stage currently follows this flow:

1. move to the project directory
2. authenticate with Docker Hub
3. build image from `./app`
4. tag image twice:
   - short commit SHA
   - `latest`
5. push both tags

Representative build job:

```yaml
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
```

## 6. Deploy Stage Details

The deploy stage currently uses:

- the same `gcp-shell` runner
- a Python virtual environment when needed
- Ansible for deployment
- SSH key `~/.ssh/newsgenie_oci`

Representative deploy logic:

```yaml
deploy_to_gcp_vm:
  stage: deploy
  tags:
    - gcp-shell
  before_script:
    - cd "$CI_PROJECT_DIR"
    - chmod 600 ~/.ssh/newsgenie_oci
    - python3 -m venv .venv
    - source .venv/bin/activate
  script:
    - ansible-playbook -i ansible/inventory/hosts ansible/deploy.yml
  only:
    - main
```

Adjust the playbook and inventory path if your final project structure differs slightly.

## 7. Deployment Architecture

### Components

- GitLab repository
- GitLab Runner with `gcp-shell` tag
- Docker Hub
- GCP VM
- Ansible deployment playbook
- private SSH key for deployment access

### End-to-end flow

1. Developer pushes code to `main`
2. GitLab triggers pipeline
3. Build stage runs
4. Docker image is built from `./app`
5. Image is pushed to Docker Hub
6. Deploy stage starts
7. Ansible connects to the target environment
8. Target pulls latest image
9. Running container is updated
10. New application version becomes active

## 8. Recommended Repository Layout

```text
newsgenie/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── src/
│   └── tests/
├── ansible/
│   ├── deploy.yml
│   ├── inventory/
│   │   ├── README.md
│   │   └── hosts.example
│   └── roles/
├── docs/
│   └── cicd.md
├── .gitlab-ci.yml
├── .env.example
├── .gitignore
└── README.md
```

## 9. Required GitLab CI/CD Variables

Store secrets in GitLab project variables, not in the repository.

Typical required variables:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `IMAGE_NAME`

You may also need environment-specific variables depending on how your playbooks are written.

## 10. Secrets and Sensitive Files

Do not commit:

- `.env`
- private SSH keys
- live inventory with sensitive data
- cloud credentials
- Docker Hub tokens

Commit only sanitized examples such as:

- `.env.example`
- `ansible/inventory/hosts.example`

## 11. Suggested `.gitlab-ci.yml` Pattern

Below is a polished version aligned with your working model:

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
    - pip install ansible
  script:
    - ansible-playbook -i ansible/inventory/hosts ansible/deploy.yml
  only:
    - main
```

## 12. Manual Deployment Command

For manual deployment outside CI:

```bash
cd ansible
ansible-playbook -i inventory/hosts deploy.yml
```

Use a local inventory file or a non-committed private inventory.

## 13. Common Issues

### Docker login failure
Check GitLab variables for:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### Wrong build context
Make sure the build command points to:

```bash
docker build -t "$APP_IMAGE" -t "$APP_IMAGE_LATEST" ./app
```

### SSH permission denied
Fix key permissions:

```bash
chmod 600 ~/.ssh/newsgenie_oci
```

### Runner not picking up jobs
Check that:
- the runner is active
- the runner has the `gcp-shell` tag
- the job tags match exactly

### Ansible connection failure
Check:
- target host/IP
- SSH user
- inventory path
- firewall rules
- private key location

## 14. Recommended Next Enhancements

- add post-deploy health checks
- add smoke tests in pipeline
- add rollback strategy
- add separate environments such as dev and prod
- add deployment logs and monitoring
- add architecture diagram under `docs/images/`

## 15. Final Recommendation

For this project, keep the CI/CD code in the same repository as the application.

Use:
- one main `README.md`
- one `docs/cicd.md`
- one clear `.gitignore`

That gives you a clean GitHub repo that is easy for others to understand, run, and extend.
