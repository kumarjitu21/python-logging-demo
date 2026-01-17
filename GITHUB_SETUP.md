# GitHub Setup Guide

Complete guide for publishing your FastAPI Logging Demo project to GitHub with proper CI/CD configuration.

## Table of Contents
1. [Create Repository](#create-repository)
2. [Push Code to GitHub](#push-code-to-github)
3. [Configure GitHub Settings](#configure-github-settings)
4. [Set up Secrets and Environments](#set-up-secrets-and-environments)
5. [Enable GitHub Features](#enable-github-features)
6. [Verify CI/CD](#verify-cicd)

## Create Repository

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. **Repository name**: `python-logging-demo`
3. **Description**: `FastAPI project with industry-best-practice structured logging using Loguru, Kubernetes, and Azure integration`
4. **Visibility**: Public (or Private)
5. **Initialize**: Don't initialize (we have local files)
6. Click **Create repository**

### Step 2: Update Local Configuration

```bash
# Update README with your GitHub username
cd /Users/jitendrakumar/projects/python-logging-demo

# Replace YOUR_USERNAME in files:
sed -i '' 's/YOUR_USERNAME/your-github-username/g' REPO_README.md
sed -i '' 's/YOUR_USERNAME/your-github-username/g' CI_CD.md
```

## Push Code to GitHub

### Step 1: Initialize Git and Push

```bash
cd /Users/jitendrakumar/projects/python-logging-demo

# Initialize git if not already done
git init
git add .
git commit -m "initial: FastAPI project with structured logging, Kubernetes, and CI/CD"

# Add remote repository
git remote add origin https://github.com/your-username/python-logging-demo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Verify Push

```bash
# Check remote
git remote -v

# Check branch
git branch -a
```

## Configure GitHub Settings

### Step 1: Repository Settings

Go to: https://github.com/your-username/python-logging-demo/settings

#### General
- ✓ Template repository: Disabled
- ✓ Default branch: `main`
- ✓ Delete head branches: Enabled

#### Code and automation → Actions
- ✓ Allow all actions and reusable workflows
- ✓ Workflow permissions: **Read and write permissions**

#### Code and automation → Pages
- Source: GitHub Actions (for potential docs)

### Step 2: Branch Protection

Go to: **Settings → Branches → Add rule**

**Branch name pattern**: `main`

**Protect matching branches**:
- ✓ Require a pull request before merging
- ✓ Dismiss stale pull request approvals when new commits are pushed
- ✓ Require status checks to pass before merging
- ✓ Require branches to be up to date before merging

**Required status checks**:
- `test-3.12` (or latest Python version)
- `lint`
- `type-check`

**Require code reviews**:
- ✓ Require at least 1 review
- ✓ Dismiss stale pull request approvals

### Step 3: Collaborators & Teams

Go to: **Settings → Collaborators and teams**

Add team members if applicable.

## Set up Secrets and Environments

### Step 1: Create Environments

Go to: **Settings → Environments**

#### Staging Environment
1. Click **New environment**
2. Name: `staging`
3. Add deployment branches: All branches
4. Save environment

#### Production Environment
1. Click **New environment**
2. Name: `production`
3. Add deployment branches: Only `main`
4. Add required reviewers: 1-2 team members
5. Save environment

### Step 2: Add Secrets for Docker Registry

Go to: **Settings → Secrets and variables → Actions**

#### Repository Secrets
```
No secrets needed for public docker registry (GitHub Container Registry uses GITHUB_TOKEN)
```

### Step 3: Add Secrets for Kubernetes Deployment

For each environment (staging, production):

1. Go to: **Settings → Environments → {environment}**
2. Click **Add secret**

#### Required Secrets

**Name**: `KUBECONFIG`
**Value**: Your base64-encoded kubeconfig file

```bash
# Generate secret value
cat ~/.kube/config | base64 -w 0 | pbcopy
```

Paste the value in GitHub.

### Step 4: Add Secrets for SonarCloud (Optional)

Go to: **Settings → Secrets and variables → Actions**

**Name**: `SONARCLOUD_TOKEN`
**Value**: Your SonarCloud token from https://sonarcloud.io/account/security

## Enable GitHub Features

### Step 1: Enable Issues

Go to: **Settings → General → Features**

- ✓ Issues: Enabled
- ✓ Discussions: Enabled (optional)
- ✓ Projects: Enabled (optional)

### Step 2: Set Issue Templates

Already configured in `.github/ISSUE_TEMPLATE/`

Verify at: **Settings → Features → Set up templates**
- Bug report template
- Feature request template

### Step 3: Add Status Badge to README

In your README.md, add:

```markdown
[![Tests](https://github.com/your-username/python-logging-demo/actions/workflows/tests.yml/badge.svg)](https://github.com/your-username/python-logging-demo/actions)
[![Docker](https://github.com/your-username/python-logging-demo/actions/workflows/docker.yml/badge.svg)](https://github.com/your-username/python-logging-demo/actions)
[![Quality](https://github.com/your-username/python-logging-demo/actions/workflows/quality.yml/badge.svg)](https://github.com/your-username/python-logging-demo/actions)
```

## Verify CI/CD

### Step 1: Check Workflow Status

1. Go to: **Actions** tab
2. Should see 4 workflows:
   - Tests
   - Build and Push Docker Image
   - Code Quality Analysis
   - Deploy to Kubernetes

### Step 2: Trigger Test Workflow

```bash
# Make a small change and push
echo "# Updated" >> README.md
git add .
git commit -m "docs: update README"
git push origin main
```

Watch the workflow run in Actions tab.

### Step 3: Monitor First Run

**Tests Workflow** should:
- ✓ Test on Python 3.9, 3.10, 3.11, 3.12
- ✓ Run linting, type checking, tests
- ✓ Pass all checks

**Docker Workflow** should (on push to main):
- ✓ Build Docker image
- ✓ Push to ghcr.io
- ✓ Scan with Trivy

**Quality Workflow** should:
- ✓ Run code quality analysis
- ✓ Upload to SonarCloud (if configured)

## Optional: SonarCloud Integration

### Step 1: Create SonarCloud Account

1. Go to https://sonarcloud.io
2. Sign in with GitHub
3. Click **Analyze a new project**
4. Select your repository
5. Choose plan (free for public repos)

### Step 2: Generate Token

1. Go to https://sonarcloud.io/account/security
2. Generate new token
3. Copy token value

### Step 3: Add to GitHub

1. Go to **Settings → Secrets and variables → Actions**
2. Add secret: `SONARCLOUD_TOKEN`
3. Value: Your token from SonarCloud

### Step 4: Verify Integration

After next PR:
- SonarCloud comment appears in PR
- Quality gate shows in Actions

## Optional: Codecov Integration

### Step 1: Connect Codecov

1. Go to https://codecov.io
2. Sign in with GitHub
3. Select repository
4. Authorize Codecov

### Step 2: Coverage Badge

Add to README:
```markdown
[![codecov](https://codecov.io/gh/your-username/python-logging-demo/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/python-logging-demo)
```

Coverage reports automatically uploaded by GitHub Actions.

## Troubleshooting

### Workflows Not Running

**Solution**: Check **Settings → Actions → General**
- Allow all actions and reusable workflows must be enabled

### Push Rejected

**Problem**: Branch protection rules
**Solution**: Create a pull request instead

```bash
git checkout -b feature/update
git commit -am "update"
git push -u origin feature/update
# Then create PR in GitHub UI
```

### Secrets Not Working

**Problem**: Secret not found in workflow
**Solution**: 
- Check secret exists
- Verify spelling matches in workflow file
- Check environment has access to secret

### Docker Push Fails

**Problem**: Authentication
**Solution**: 
- GITHUB_TOKEN is automatic, no setup needed
- Check repository has Actions enabled

## Next Steps

### 1. Update Repository Name
In your local README and docs:
```bash
sed -i '' 's/python-logging-demo/your-repo-name/g' *.md
```

### 2. Update Author Information
- Update LICENSE with your name
- Update pyproject.toml authors
- Update package metadata

### 3. Customize Workflows
- Add additional environment-specific steps
- Configure notifications
- Set up auto-deployment

### 4. Documentation
- Add badges to README
- Create CHANGELOG.md
- Document deployment process

### 5. First Release

```bash
# Create release tag
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

This triggers Docker workflow with semantic version tag.

## GitHub Actions Status

Monitor your workflows:
- https://github.com/your-username/python-logging-demo/actions

Access workflow details:
- Click workflow name
- Click run number
- View logs and artifacts

## Useful GitHub CLI Commands

```bash
# Create repository
gh repo create python-logging-demo --public --source=. --push

# Create release
gh release create v0.1.0 -t "Version 0.1.0" -n "Initial release"

# Create secret
gh secret set KUBECONFIG < kubeconfig.txt -c staging

# View actions
gh actions list
```

## Common Workflow Customizations

### Add Notification on Failure

Add to workflow:
```yaml
- name: Slack Notification
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

### Auto-merge Dependabot PRs

Create `.github/workflows/dependabot.yml`:
```yaml
name: Dependabot auto-merge
on: pull_request

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - uses: fastify/github-action-merge-dependabot@v3
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Deploy to Multiple Environments

Create separate workflows for:
- `deploy-staging.yml`
- `deploy-production.yml`

## Security Best Practices

✓ Use environment secrets for sensitive data
✓ Enable branch protection on main
✓ Require code reviews
✓ Use GITHUB_TOKEN for authentication
✓ Rotate secrets regularly
✓ Audit workflow access logs
✓ Keep actions up to date

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments)

## Support

For issues:
1. Check GitHub documentation
2. Review workflow logs
3. Open issue in repository
4. Ask in GitHub Discussions

---

**You're all set!** Your FastAPI project is now on GitHub with complete CI/CD pipeline. 🎉
