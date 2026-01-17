# Contributing to FastAPI Logging Demo

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites
- Python 3.9+
- Poetry
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/python-logging-demo.git
   cd python-logging-demo
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Code Style

We follow PEP 8 and use automated tools for consistency:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

### Before Committing

Format and check your code:

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Run tests
make test
```

Or run all checks:
```bash
make format lint typecheck test
```

### Commit Messages

Follow conventional commits format:

```
feat: add new feature
fix: fix a bug
docs: update documentation
test: add or update tests
refactor: refactor code
chore: update dependencies
perf: improve performance
```

Example:
```
feat: add request rate limiting middleware

- Implement token bucket algorithm
- Add configurable rate limits per endpoint
- Include rate limit headers in responses
```

## Making Changes

### Adding Features

1. Create a feature branch
2. Write tests for new functionality
3. Implement the feature
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

### Modifying Logging

When modifying logging behavior:

1. Update [app/core/logging.py](app/core/logging.py)
2. Add corresponding tests in [tests/test_api.py](tests/test_api.py)
3. Update [LOGGING.md](LOGGING.md) documentation
4. Add examples in [EXAMPLES.md](EXAMPLES.md) if applicable

### Adding API Endpoints

1. Create route in [app/api/routes.py](app/api/routes.py)
2. Add Pydantic models in [app/models/schemas.py](app/models/schemas.py)
3. Add comprehensive logging with request context
4. Write tests in [tests/test_api.py](tests/test_api.py)
5. Update API documentation in README.md

## Testing

### Run Tests
```bash
poetry run pytest tests/ -v
poetry run pytest tests/ -v --cov=app
```

### Test Coverage
Aim for >80% code coverage. Check coverage:
```bash
poetry run pytest --cov=app --cov-report=html tests/
open htmlcov/index.html
```

### Write Tests
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies
- Use fixtures for common setup

Example test:
```python
@pytest.mark.asyncio
async def test_create_user_valid_data(request: Request):
    """Test user creation with valid data."""
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }
    response = await client.post("/api/users", json=user_data)
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
```

## Pull Request Process

1. **Create a PR** with a descriptive title
2. **Link related issues** using #issue_number
3. **Describe changes** - what and why
4. **Add testing evidence** - test results, coverage
5. **Update docs** - README, LOGGING, EXAMPLES
6. **Wait for reviews** - address feedback

### PR Description Template

```markdown
## Description
Brief description of changes.

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tested on Python 3.9, 3.10, 3.11, 3.12
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples
- Keep documentation in sync with code
- Use relative links to other files

### Documentation Files

- **README.md** - Main documentation
- **GETTING_STARTED.md** - Quick start guide
- **LOGGING.md** - Logging architecture
- **EXAMPLES.md** - Code examples
- **CONTRIBUTING.md** - This file
- **k8s/README.md** - Kubernetes deployment

## Running Locally

### Development Server
```bash
make dev
```

### Access API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### View Logs
```bash
make logs
make logs-errors
make logs-json
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
poetry install
```

### Dependency Conflicts
```bash
poetry lock
poetry install
```

### Test Failures
```bash
# Run with verbose output
poetry run pytest -vv tests/

# Run specific test
poetry run pytest tests/test_api.py::test_health_check -v
```

## Project Structure

```
app/
├── api/routes.py          # API endpoints
├── core/
│   ├── config.py          # Settings
│   ├── logging.py         # Logging config
│   └── middleware.py      # HTTP middleware
├── models/schemas.py      # Pydantic models
└── main.py               # FastAPI app

tests/
└── test_api.py           # Unit tests

k8s/                       # Kubernetes manifests
logs/                      # Log files

.github/workflows/         # CI/CD pipelines
```

## Coding Standards

### Python Version
- Minimum: Python 3.9
- Target: Python 3.12

### Type Hints
- Use type hints for all functions
- Run mypy: `poetry run mypy app/`

### Docstrings
- Use Google-style docstrings
- Document parameters and return values

```python
def create_user(user: UserCreate, request: Request) -> UserResponse:
    """Create a new user.
    
    Args:
        user: User creation request
        request: FastAPI request object
        
    Returns:
        UserResponse: Created user details
        
    Raises:
        HTTPException: If validation fails
    """
```

### Logging
- Use loguru: `from loguru import logger`
- Include request context: `logger.bind(request_id=request_id)`
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

```python
logger.bind(request_id=request_id).info(
    "User created",
    user_id=user.id,
    user_name=user.name,
)
```

## Issues and Discussions

### Reporting Bugs

Create an issue with:
1. Clear description
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Python version, etc.)

### Feature Requests

Describe:
1. Use case
2. Proposed solution
3. Alternatives considered
4. Examples if applicable

### Discussions

Use GitHub Discussions for:
- Questions
- Design decisions
- General feedback

## Continuous Integration

All PRs must pass:
- ✓ Unit tests (pytest)
- ✓ Code formatting (black, isort)
- ✓ Linting (flake8)
- ✓ Type checking (mypy)
- ✓ Security checks (bandit)
- ✓ Code coverage (>80%)

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG
3. Create release branch
4. Tag release: `git tag v1.0.0`
5. Push tag triggers release workflow

## Questions?

- Check existing issues/discussions
- Review documentation
- Ask in pull request comments
- Create a new discussion

## License

By contributing, you agree to license your work under the same license as the project.

Thank you for contributing! 🎉
