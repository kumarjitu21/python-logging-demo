.PHONY: help install dev test lint format clean logs

help:
	@echo "FastAPI Logging Demo - Available Commands"
	@echo "=========================================="
	@echo "make install    - Install dependencies"
	@echo "make dev        - Start development server (reload enabled)"
	@echo "make test       - Run test suite"
	@echo "make lint       - Run code linting (flake8)"
	@echo "make format     - Format code (black, isort)"
	@echo "make typecheck  - Run type checking (mypy)"
	@echo "make clean      - Clean up cache and logs"
	@echo "make logs       - View application logs"
	@echo "make help       - Show this help message"

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-quiet:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level critical

test:
	poetry run pytest -v tests/

test-cov:
	poetry run pytest --cov=app tests/ -v

lint:
	poetry run flake8 app/ tests/ --max-line-length=120

format:
	poetry run black app/ tests/
	poetry run isort app/ tests/

typecheck:
	poetry run mypy app/ --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage

logs:
	tail -f logs/app.log

logs-errors:
	tail -f logs/errors.log

logs-json:
	tail -f logs/structured.json

docker-build:
	docker build -t fastapi-logging-demo:latest .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/logs:/app/logs fastapi-logging-demo:latest
