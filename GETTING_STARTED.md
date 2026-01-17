# Getting Started Guide

This is a complete FastAPI project with industry-best-practice structured logging using Loguru.

## Quick Start

### 1. Install Dependencies
```bash
poetry install
```

### 2. Start Development Server
```bash
poetry run uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Features

### ✅ FastAPI Framework
- Modern async Python web framework
- Automatic OpenAPI/Swagger documentation
- Pydantic models for data validation
- Type hints for IDE support

### ✅ Loguru Integration
- Powerful structured logging
- Automatic log rotation
- Multiple log handlers (console, file, JSON)
- Request tracing with unique IDs

### ✅ Structured Logging
- JSON-formatted logs for analysis tools
- Request ID propagation
- Context binding for request lifecycle
- Performance metrics (response times)

### ✅ Professional Setup
- Poetry for dependency management
- Comprehensive test suite
- Docker support
- Environment configuration

## Available Commands

```bash
# Install dependencies
make install

# Start development server
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Type checking
make typecheck

# View logs
make logs
make logs-errors
make logs-json

# Clean cache
make clean
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Create User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  }'
```

### Get User
```bash
curl http://localhost:8000/api/users/1
```

### List Users
```bash
curl http://localhost:8000/api/users
```

### Update User
```bash
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 28
  }'
```

### Delete User
```bash
curl -X DELETE http://localhost:8000/api/users/1
```

## Logging Features

### Request Tracing
Every request gets a unique ID that:
- Appears in all related log entries
- Is returned in the `X-Request-ID` response header
- Enables distributed tracing

Example:
```
2026-01-17 14:46:09 | INFO | app.api.routes:create_user:60 - Creating new user
request_id=550e8400-e29b-41d4-a716-446655440000
user_name=John Doe
user_email=john@example.com
```

### Log Files
- **logs/app.log** - General application logs
- **logs/errors.log** - Error logs only
- **logs/structured.json** - Machine-readable JSON logs

### Log Levels
Configure via environment variable:
```bash
export LOG_LEVEL=DEBUG
export LOG_LEVEL=INFO
export LOG_LEVEL=WARNING
export LOG_LEVEL=ERROR
```

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── api/
│   └── routes.py        # API endpoints
├── core/
│   ├── config.py        # Settings and configuration
│   ├── logging.py       # Loguru configuration
│   └── middleware.py    # Request/response logging
└── models/
    └── schemas.py       # Pydantic models

tests/
└── test_api.py         # Unit tests

logs/
├── app.log             # Application logs
├── errors.log          # Error logs
└── structured.json     # JSON logs
```

## Testing

Run all tests:
```bash
poetry run pytest tests/ -v
```

Run with coverage:
```bash
poetry run pytest --cov=app tests/
```

Run specific test:
```bash
poetry run pytest tests/test_api.py::test_health_check -v
```

## Production Deployment

### Using Docker
```bash
# Build Docker image
docker build -t fastapi-logging-demo:latest .

# Run Docker container
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e DEBUG=False \
  -v $(pwd)/logs:/app/logs \
  fastapi-logging-demo:latest
```

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Deployment
```bash
poetry install --no-dev
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration

Create a `.env` file:
```env
APP_NAME=FastAPI Logging Demo
DEBUG=False
LOG_LEVEL=INFO
LOG_DIR=logs
VERSION=0.1.0
```

## Integration Examples

### With ELK Stack
The JSON logs can be parsed by Logstash:
```ruby
filter {
  json {
    source => "message"
  }
}
```

### With Datadog
Forward logs to Datadog:
```bash
tail -f logs/structured.json | \
  curl -X POST "https://http-intake.logs.datadoghq.com/v1/input" \
  -H "DD-API-KEY: your-key" -d @-
```

### With CloudWatch
Configure CloudWatch Agent to read from:
- `logs/app.log`
- `logs/errors.log`
- `logs/structured.json`

## Best Practices Implemented

1. **Structured Logging** - All logs include context
2. **Log Rotation** - Prevents disk space issues
3. **Error Tracking** - Separate error logs
4. **Request Tracing** - Unique IDs for correlation
5. **JSON Formatting** - Easy parsing and analysis
6. **Backtrace & Diagnose** - Enhanced error information
7. **Context Binding** - Request context throughout lifecycle
8. **Middleware Logging** - Automatic request/response logging
9. **Performance Metrics** - Response times in logs
10. **Production Ready** - Appropriate compression and retention

## Troubleshooting

### Logs not appearing
1. Check `LOG_LEVEL` environment variable
2. Verify `logs/` directory exists
3. Check file permissions
4. Review application startup

### Performance issues
1. Reduce log level from DEBUG to INFO
2. Check disk I/O for rotated files
3. Monitor log file sizes
4. Adjust rotation thresholds

### Tests failing
1. Ensure all dependencies are installed: `poetry install`
2. Check Python version: `python --version` (3.9+)
3. Run tests with verbose output: `poetry run pytest -v`

## Next Steps

1. **Database Integration** - Add SQLAlchemy/SQLModel
2. **Authentication** - Implement JWT/OAuth2
3. **WebSockets** - Add real-time features
4. **GraphQL** - Add GraphQL endpoints
5. **Caching** - Integrate Redis
6. **Message Queue** - Add Celery/RabbitMQ
7. **Monitoring** - Add Prometheus metrics
8. **API Rate Limiting** - Implement rate limiting

## Support

For issues and questions:
1. Check the [Loguru documentation](https://loguru.readthedocs.io/)
2. See [FastAPI documentation](https://fastapi.tiangolo.com/)
3. Review [Poetry documentation](https://python-poetry.org/)

## License

This project is provided as-is for educational and development purposes.
