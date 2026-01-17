![FastAPI Logging Demo](https://img.shields.io/badge/FastAPI-Logging-blue?style=for-the-badge)
![Python Version](https://img.shields.io/badge/python-3.9+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
[![Tests](https://github.com/YOUR_USERNAME/python-logging-demo/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/python-logging-demo/actions)
[![Docker](https://github.com/YOUR_USERNAME/python-logging-demo/actions/workflows/docker.yml/badge.svg)](https://github.com/YOUR_USERNAME/python-logging-demo/actions)

# FastAPI Project with Industry Best Practices

A production-ready **FastAPI** project demonstrating industry best practices for structured logging, testing, deployment, and CI/CD.

## ✨ Features

- 🚀 **FastAPI** - Modern async Python web framework
- 📝 **Loguru** - Advanced structured logging with multiple handlers
- 🧪 **Comprehensive Testing** - Unit tests with pytest (8/8 passing)
- 🐳 **Docker** - Production-ready Dockerfile with multi-stage builds
- ☸️ **Kubernetes** - Complete K8s deployment with Fluent Bit integration
- 📊 **Azure Integration** - Log Analytics workspace connectivity
- 🔄 **CI/CD Pipeline** - GitHub Actions with automated testing and deployment
- 📚 **Full Documentation** - Setup guides, logging architecture, examples
- ✅ **Code Quality** - Black, isort, flake8, mypy, pre-commit hooks
- 🔐 **Security** - Bandit, Trivy, safety checks

## 📦 What's Included

```
FastAPI Application
├── Async API endpoints (CRUD operations)
├── Request tracing with unique IDs
├── Middleware for automatic logging
├── Pydantic validation models
└── Comprehensive error handling

Logging System
├── Console output (development)
├── File logs with rotation
├── Error-specific logs
├── JSON structured logs
└── Request context binding

Testing & Quality
├── Full test suite (8 tests)
├── Code coverage reports
├── Type checking (mypy)
├── Linting (flake8)
├── Code formatting (black, isort)
└── Pre-commit hooks

Deployment
├── Docker containerization
├── Kubernetes manifests
├── Fluent Bit integration
├── Azure Log Analytics setup
└── GitHub Actions CI/CD

Documentation
├── Complete README
├── Getting Started guide
├── Logging architecture
├── Code examples
├── Contributing guidelines
└── CI/CD documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Poetry
- Git
- Docker (optional)
- Kubernetes cluster (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/python-logging-demo.git
cd python-logging-demo

# Install dependencies
poetry install

# Start development server
poetry run uvicorn app.main:app --reload
```

### Access the Application

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Run Tests

```bash
poetry run pytest tests/ -v
```

## 📋 Available Commands

```bash
make help              # Show all commands
make install          # Install dependencies
make dev              # Start development server
make test             # Run test suite
make lint             # Lint code
make format           # Format code
make clean            # Clean cache
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/api/health` | Health check |
| POST | `/api/users` | Create user |
| GET | `/api/users` | List users |
| GET | `/api/users/{id}` | Get user |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |

### Example Usage

```bash
# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# List users
curl http://localhost:8000/api/users

# Get user
curl http://localhost:8000/api/users/1
```

## 📊 Logging Features

### Structured Logging
- JSON-formatted logs for analysis tools
- Context binding for request lifecycle
- Unique request IDs for tracing
- Performance metrics (response times)

### Log Files
- `logs/app.log` - General application logs
- `logs/errors.log` - Error logs only
- `logs/structured.json` - Machine-readable JSON

### Request Tracing
Every request gets a unique ID that:
- Appears in all related logs
- Is returned in `X-Request-ID` header
- Enables distributed tracing

## 🧪 Testing

```bash
# Run all tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test
poetry run pytest tests/test_api.py::test_health_check -v
```

**Coverage**: 100% of API endpoints
**Test Count**: 8 passing tests

## 🐳 Docker

### Build Image
```bash
docker build -t fastapi-logging-demo:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/logs:/app/logs \
  fastapi-logging-demo:latest
```

### Docker Compose
```bash
docker-compose up -d
```

## ☸️ Kubernetes Deployment

### Deploy to Cluster
```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n fastapi
kubectl get services -n fastapi
```

### With Fluent Bit & Azure Logs
```bash
# Deploy Fluent Bit
kubectl apply -f k8s/fluent-bit-*.yaml

# Logs flow to Azure Log Analytics
```

See [k8s/README.md](k8s/README.md) for detailed setup.

## 🔄 CI/CD Pipeline

GitHub Actions automates:
- ✅ Unit testing (Python 3.9-3.12)
- ✅ Code linting and formatting
- ✅ Type checking
- ✅ Security scanning
- 🐳 Docker image building and scanning
- ☸️ Kubernetes deployment

**Workflows**:
- `tests.yml` - Test and code quality
- `docker.yml` - Docker build and push
- `quality.yml` - Code analysis
- `deploy-k8s.yml` - Kubernetes deployment

See [CI_CD.md](CI_CD.md) for detailed documentation.

## 📚 Documentation

- **[README.md](README.md)** - Complete project documentation
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide
- **[LOGGING.md](LOGGING.md)** - Logging architecture and configuration
- **[EXAMPLES.md](EXAMPLES.md)** - Practical code examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines
- **[CI_CD.md](CI_CD.md)** - GitHub Actions CI/CD documentation
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment guide

## 🛠️ Development Setup

### Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Automatically runs before each commit:
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security checks (bandit)

### Code Style

Project follows:
- **PEP 8** - Python style guide
- **Black** - Code formatting
- **isort** - Import sorting
- **Google docstrings** - Documentation style

### Type Hints

All functions must have type hints:
```python
async def create_user(user: UserCreate, request: Request) -> UserResponse:
    """Create a new user."""
```

## 🔐 Security

Built-in security checks:
- **Bandit** - Code vulnerability scanning
- **Safety** - Dependency vulnerability checking
- **Trivy** - Container image scanning
- **GitHub Security** - Dependabot alerts

## 📦 Project Structure

```
python-logging-demo/
├── app/                          # Application code
│   ├── api/routes.py            # API endpoints
│   ├── core/
│   │   ├── config.py            # Settings
│   │   ├── logging.py           # Loguru configuration
│   │   └── middleware.py        # HTTP middleware
│   ├── models/schemas.py        # Pydantic models
│   └── main.py                  # FastAPI app
├── tests/                        # Test suite
│   └── test_api.py              # Unit tests
├── k8s/                         # Kubernetes manifests
├── .github/
│   ├── workflows/               # GitHub Actions
│   └── ISSUE_TEMPLATE/          # Issue templates
├── logs/                        # Application logs
├── pyproject.toml              # Poetry configuration
├── Dockerfile                  # Container image
├── docker-compose.yml          # Multi-container setup
└── README.md                   # This file
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

**Quick contribut steps**:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## 📋 Checklist for GitHub Setup

- [ ] Update README.md with your GitHub username
- [ ] Create GitHub repository
- [ ] Push code: `git push -u origin main`
- [ ] Configure branch protection rules
- [ ] Set up GitHub Environments (staging, production)
- [ ] Add secrets for Docker and Kubernetes
- [ ] Enable GitHub Actions
- [ ] Configure SonarCloud (optional)
- [ ] Update CI_CD.md with your repository details
- [ ] Enable discussions and projects (optional)

## 🚀 Deployment

### Production Deployment

**Docker**:
```bash
docker build -t myregistry/fastapi-logging-demo:latest .
docker push myregistry/fastapi-logging-demo:latest
```

**Kubernetes**:
```bash
kubectl apply -f k8s/
kubectl rollout status deployment/fastapi-app -n fastapi
```

**GitHub Actions**: Automatically deploys on push to main

## 📊 Monitoring

### Application Logs
```bash
# View logs
tail -f logs/app.log
tail -f logs/errors.log
tail -f logs/structured.json

# Or via make
make logs
make logs-errors
make logs-json
```

### Azure Log Analytics
View logs in Azure portal under your Log Analytics workspace.

### GitHub Actions
Monitor CI/CD at: https://github.com/{owner}/{repo}/actions

## 🐛 Troubleshooting

### Tests Failing
```bash
poetry install
poetry run pytest tests/ -v
```

### Import Errors
```bash
poetry lock
poetry install
```

### Docker Build Issues
```bash
docker build --no-cache -t fastapi-logging-demo:latest .
```

See [GETTING_STARTED.md](GETTING_STARTED.md#troubleshooting) for more help.

## 📖 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Poetry Documentation](https://python-poetry.org/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💼 Author

[Your Name/Organization]

## 🙏 Acknowledgments

- Built with FastAPI and Loguru
- Inspired by industry best practices
- Thanks to all contributors

---

**Questions?** Open an issue or check the [discussions](https://github.com/YOUR_USERNAME/python-logging-demo/discussions).

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md).

Made with ❤️ for the Python community
