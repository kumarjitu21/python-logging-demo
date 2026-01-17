# GitHub Actions CI/CD Pipeline

This document describes the continuous integration and deployment pipelines configured in GitHub Actions.

## Overview

The project uses GitHub Actions for automated testing, code quality checks, Docker builds, and Kubernetes deployment.

## Workflows

### 1. Tests Workflow (`tests.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**

#### Test Job
- **Matrix**: Python 3.9, 3.10, 3.11, 3.12
- **Steps**:
  - Checkout code with full history
  - Set up Python with cached pip
  - Install Poetry
  - Cache dependencies
  - Run flake8 linting (strict and warnings)
  - Run mypy type checking
  - Run isort import checking
  - Run pytest with coverage
  - Upload coverage to Codecov

#### Security Job
- **Steps**:
  - Run Bandit for security vulnerabilities
  - Check dependencies with Safety
  - Continue on error (informational)

**Triggers:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

**Access Artifacts:**
- Coverage reports available in Actions artifacts
- Codecov badge in README

### 2. Docker Workflow (`docker.yml`)

Builds and pushes Docker images to GitHub Container Registry.

**Jobs:**

#### Build Job
- **Matrix**: Ubuntu latest
- **Registry**: `ghcr.io`
- **Steps**:
  - Checkout code
  - Set up Docker Buildx
  - Authenticate with registry
  - Extract metadata (tags, labels)
  - Build and push image with cache
  - Output image digest

#### Scan Job
- **Trigger**: After successful build
- **Tool**: Trivy vulnerability scanner
- **Output**: SARIF format for GitHub Security tab

**Triggers:**
```yaml
on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]
```

**Image Tags:**
- `latest` - Latest main branch build
- `branch-name` - Branch-specific builds
- `v1.0.0` - Semantic version tags
- `sha-xxxxx` - Commit SHA builds

### 3. Code Quality Workflow (`quality.yml`)

Analyzes code quality on every push and PR.

**Jobs:**

#### Quality Analysis Job
- **Steps**:
  - Run Pylint
  - Run Black formatter check
  - Run isort import check
  - Run flake8 linting
  - Run mypy type checking
  - Upload to SonarCloud (PR only)
  - Generate coverage summary

**Triggers:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

**Continue on Error**: All checks continue even if one fails (informational)

### 4. Kubernetes Deployment Workflow (`deploy-k8s.yml`)

Deploys application to Kubernetes cluster.

**Manual Trigger:**
```yaml
on:
  push:
    branches: [main]
    paths:
      - 'k8s/**'
      - '.github/workflows/deploy-k8s.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        options: [staging, production]
```

**Jobs:**

#### Deploy Job
- **Steps**:
  - Checkout code
  - Set up kubectl
  - Configure kubeconfig from secrets
  - Get Docker image tag
  - Update K8s manifests with image tag
  - Apply manifests
  - Wait for rollout (5-minute timeout)
  - Verify deployment
  - Post status

**Environments:**
- Uses GitHub Environments for separation
- Different secrets for staging/production
- Requires kubeconfig in secrets

**Environment Setup:**
```bash
# For staging:
Settings → Environments → staging
Add secret: KUBECONFIG (base64 encoded)

# For production:
Settings → Environments → production
Add secret: KUBECONFIG (base64 encoded)
```

## Secrets Configuration

### Required Secrets

#### For Docker Build (`docker.yml`)
No additional secrets needed - uses built-in `GITHUB_TOKEN`

#### For Kubernetes Deployment (`deploy-k8s.yml`)
**Repository Secrets:**
- `KUBECONFIG` - Base64 encoded kubeconfig file

**Environment Secrets:**
- Add to `Settings → Environments → {staging,production}`
- `KUBECONFIG` - Environment-specific kubeconfig

#### For SonarCloud (`quality.yml`)
**Repository Secrets:**
- `SONARCLOUD_TOKEN` - SonarCloud authentication token

### Setting up Secrets

```bash
# Example: Add kubeconfig as secret
cat ~/.kube/config | base64 | pbcopy
# Then paste in GitHub Secrets UI

# Or via GitHub CLI:
gh secret set KUBECONFIG < <(cat ~/.kube/config | base64)
```

## Environment Setup

### GitHub Repository Settings

**Settings → Actions → General:**
- ✓ Allow all actions and reusable workflows
- ✓ Workflow permissions: Read and write

**Settings → Code and automation → Environments:**

**Staging Environment:**
- Required reviewers: None
- Deployment branches: All branches

**Production Environment:**
- Required reviewers: 1+ team members
- Deployment branches: main only

## Cache Strategy

### Python Cache
```yaml
- uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ python-version }}-${{ hashFiles('poetry.lock') }}
```

### Docker Layer Cache
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Performance Optimization

### Matrix Optimization
Runs tests in parallel for multiple Python versions:
```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
```

### Conditional Steps
Skip expensive operations for pull requests:
```yaml
if: github.event_name != 'pull_request'
```

### Continue on Error
Non-blocking checks continue execution:
```yaml
continue-on-error: true
```

## Status Checks

### Required Checks (Branch Protection)

Set in `Settings → Branches → main → Required status checks`

Required:
- ✓ Test Python 3.12
- ✓ Lint with flake8
- ✓ Type check with mypy

Optional (informational):
- Security checks
- Code quality analysis
- Docker build

## Troubleshooting

### Tests Failing Locally but Passing in CI

1. Check Python version matches CI (3.12)
2. Run with same cache:
   ```bash
   poetry lock
   poetry install
   ```
3. Run exact same tests:
   ```bash
   poetry run pytest tests/ -v
   ```

### Docker Build Failures

1. Check Dockerfile syntax
2. Verify base image availability
3. Check build context includes all files
4. Review build logs in Actions UI

### Kubernetes Deployment Issues

1. Verify kubeconfig is valid and base64 encoded
2. Check cluster connectivity
3. Review manifest YAML syntax
4. Check image availability in registry

### SonarCloud Integration

1. Create SonarCloud organization
2. Add project in SonarCloud dashboard
3. Generate token in SonarCloud
4. Add token as GitHub secret: `SONARCLOUD_TOKEN`

## Monitoring

### GitHub Actions Dashboard

Access at: `https://github.com/{owner}/{repo}/actions`

**View:**
- Workflow runs
- Job logs
- Execution times
- Failure reasons

### Artifacts

Automatically saved:
- Coverage reports
- Test results
- Build logs

Access via:
1. Go to Actions tab
2. Click workflow run
3. Download artifacts

### Status Badge

Add to README.md:
```markdown
[![Tests](https://github.com/{owner}/{repo}/actions/workflows/tests.yml/badge.svg)](https://github.com/{owner}/{repo}/actions)
[![Docker](https://github.com/{owner}/{repo}/actions/workflows/docker.yml/badge.svg)](https://github.com/{owner}/{repo}/actions)
```

## Best Practices

### 1. Keep Workflows Lean
- Run only necessary checks
- Use matrix for parallel execution
- Cache dependencies

### 2. Security
- Use GitHub Environments for secrets
- Limit secret access with branch filters
- Review external actions versions

### 3. Notifications
- Configure branch notification rules
- Set up pull request reviews
- Monitor workflow status

### 4. Documentation
- Document all workflows
- Keep README badges updated
- Link to workflow files

### 5. Testing
- Test locally before pushing
- Run full test suite in CI
- Keep tests fast (<5 minutes)

## Extending the Workflows

### Add New Check

1. Create new job in workflow
2. Define trigger conditions
3. Add required steps
4. Set continue-on-error if needed

Example:
```yaml
- name: Run custom linter
  run: poetry run custom-lint app/
  continue-on-error: true
```

### Add New Environment

1. Create environment in Settings
2. Add required secrets
3. Configure deployment rules
4. Update deploy workflow

### Add New Docker Registry

```yaml
- uses: docker/login-action@v3
  with:
    registry: docker.io
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

## Performance Metrics

### Typical Execution Times

- Tests (3.12): ~2-3 minutes
- Docker build: ~3-5 minutes
- Code quality: ~1-2 minutes
- Deployment: ~2-3 minutes

**Total PR check time**: ~5-7 minutes

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [SonarCloud Documentation](https://sonarcloud.io/documentation)
- [Kubernetes Deployment](k8s/README.md)
- [Contributing Guidelines](CONTRIBUTING.md)
