# FastAPI with Industry-Best-Practice Logging

A modern FastAPI application demonstrating industry best practices for structured logging using **Loguru**, with complete request/response tracking, error handling, and JSON-formatted logs for production environments.

## Features

- ✅ **FastAPI** - Modern Python web framework
- ✅ **Poetry** - Python dependency management
- ✅ **Loguru** - Powerful and flexible logging library
- ✅ **Structured Logging** - JSON-formatted logs for easy parsing and analysis
- ✅ **Correlation ID** - Industry-standard distributed request tracing using contextvars
- ✅ **Request Tracing** - Unique request IDs propagated across async operations
- ✅ **Multiple Log Handlers** - Console, file, error, and structured JSON logs
- ✅ **Log Rotation** - Automatic log file rotation and compression
- ✅ **Pydantic Models** - Data validation and serialization
- ✅ **API Documentation** - Auto-generated OpenAPI/Swagger docs
- ✅ **Unit Tests** - Comprehensive test suite with pytest
- ✅ **Kubernetes Ready** - Production-ready K8s manifests
- ✅ **Fluent Bit Integration** - Log aggregation with DaemonSet
- ✅ **Azure Log Analytics** - Cloud-based log retention and analysis
- ✅ **Auto Scaling** - Horizontal Pod Autoscaler (HPA) configured
- ✅ **High Availability** - Pod Disruption Budgets and anti-affinity

## Project Structure

```
python-logging-demo/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API endpoints with logging and correlation ID
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   ├── logging.py             # Loguru setup and configuration
│   │   ├── correlation_id.py      # Correlation ID context management (contextvars)
│   │   └── middleware.py          # Request/response logging middleware
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models for validation
│   ├── __init__.py
│   └── main.py                    # FastAPI application entry point
├── tests/
│   └── test_api.py               # API tests with logging and correlation ID tests
├── k8s/                           # Kubernetes manifests
│   ├── namespace.yaml
│   ├── fastapi-service.yaml
│   ├── fastapi-configmap.yaml
│   ├── fastapi-deployment.yaml
│   ├── fastapi-hpa.yaml
│   ├── fastapi-pdb.yaml
│   ├── fluent-bit-*.yaml
│   ├── deploy.sh                 # Deployment script
│   └── setup-azure.sh            # Azure setup script
├── fluent-bit/                   # Fluent Bit configuration
│   ├── fluent-bit.conf
│   ├── custom_parsers.conf
│   └── setup.sh
├── logs/                          # Log files directory (created at runtime)
├── pyproject.toml                # Poetry configuration
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Local Docker Compose setup
├── Makefile                      # Development commands
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment variables template
├── README.md                     # This file
├── KUBERNETES.md                 # Kubernetes deployment guide
├── FLUENT_BIT.md                 # Fluent Bit configuration guide
├── AZURE.md                      # Azure Log Analytics setup guide
└── LOGGING.md                    # Logging documentation
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Poetry (install from https://python-poetry.org/)

### Setup Steps

1. **Clone/Open the project:**
   ```bash
   cd python-logging-demo
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Create environment file (optional):**
   ```bash
   cp .env.example .env
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application settings
APP_NAME=FastAPI Logging Demo
DEBUG=False
LOG_LEVEL=INFO
LOG_DIR=logs

# Logging configuration
# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Logging Configuration

The logging is configured in [app/core/logging.py](app/core/logging.py) with the following handlers:

1. **Console Handler**
   - Colored output for development
   - Real-time monitoring

2. **General Log File** (`logs/app.log`)
   - Rotates at 100 MB
   - Retains for 10 days
   - Compressed when rotated

3. **Error Log File** (`logs/errors.log`)
   - Only ERROR level and above
   - Rotates at 50 MB
   - Retains for 30 days

4. **Structured JSON Logs** (`logs/structured.json`)
   - Machine-readable format
   - Easy integration with log aggregation tools (ELK, Datadog, etc.)
   - Includes request context and extra fields

## Running the Application

### Development Mode

```bash
poetry run python -m uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

### Production Mode

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using the Makefile (if available)

```bash
# Start development server
make dev

# Run tests
make test

# View logs
make logs
```

## API Endpoints

### Health Check
```http
GET /api/health
```

Returns the current health status and version.

### User Management

**Create User:**
```http
POST /api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

**Get User:**
```http
GET /api/users/{user_id}
```

**List Users:**
```http
GET /api/users
```

**Update User:**
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "age": 28
}
```

**Delete User:**
```http
DELETE /api/users/{user_id}
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## Structured Logging Features

### Request ID Tracking

Every request gets a unique request ID that:
- Is included in all related logs
- Is returned in the `X-Request-ID` response header
- Enables distributed tracing across services

Example log with request context:
```json
{
  "timestamp": "2024-01-17T10:30:45.123456",
  "level": "INFO",
  "logger": "app.api.routes",
  "function": "create_user",
  "line": 42,
  "message": "Creating new user",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "user_age": 30
}
```

### Log Levels

- **DEBUG** - Detailed information for debugging
- **INFO** - General informational messages
- **WARNING** - Warning messages for potentially harmful situations
- **ERROR** - Error messages for error events
- **CRITICAL** - Critical messages for very serious errors

## Testing

Run the test suite:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_api.py

# Run with coverage
poetry run pytest --cov=app tests/
```

## Log File Examples

### Console Output
```
2024-01-17 10:30:45.123 | INFO     | app.core.middleware:__call__:24 - Incoming request
method=GET path=/api/health query_params={} client=127.0.0.1 request_id=550e8400-e29b-41d4-a716-446655440000
```

### Structured JSON Log
```json
{
  "timestamp": "2024-01-17T10:30:45.123456",
  "level": "INFO",
  "logger": "app.core.middleware",
  "function": "__call__",
  "line": 24,
  "message": "Incoming request",
  "extra": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "method": "GET",
    "path": "/api/health",
    "query_params": {},
    "client": "127.0.0.1"
  }
}
```

## Best Practices Implemented

1. **Structured Logging** - All logs include contextual information
2. **Log Rotation** - Automatic rotation prevents disk space issues
3. **Error Tracking** - Separate error logs for easier debugging
4. **Request Tracing** - Unique IDs for request correlation
5. **JSON Format** - Machine-readable logs for analysis tools
6. **Backtrace & Diagnose** - Enhanced error information
7. **Context Binding** - Request context throughout the request lifecycle
8. **Middleware Logging** - Automatic request/response logging
9. **Performance Tracking** - Request duration in logs
10. **Production Ready** - Appropriate compression and retention policies

## Integration with Log Aggregation Tools

### ELK Stack (Elasticsearch, Logstash, Kibana)

Parse the structured JSON logs in Logstash:
```ruby
filter {
  json {
    source => "message"
  }
}
```

### Datadog

Forward logs using:
```bash
poetry run python -m json.tool logs/structured.json | curl -X POST "https://http-intake.logs.datadoghq.com/v1/input" \
  -H "DD-API-KEY: your-api-key" \
  -d @-
```

### CloudWatch

Configure AWS CloudWatch agent to read from:
- `/logs/app.log`
- `/logs/errors.log`
- `/logs/structured.json`

## Troubleshooting

### Logs not appearing

1. Check `LOG_LEVEL` environment variable
2. Verify `logs/` directory exists
3. Check file permissions
4. Review application startup logs

### Performance issues

1. Reduce `log_level` from DEBUG to INFO
2. Check disk I/O for rotated files
3. Monitor log file sizes
4. Consider adjusting rotation thresholds

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **loguru** - Logging library
- **pydantic** - Data validation
- **pydantic-settings** - Settings management
- **python-json-logger** - JSON formatting
- **structlog** - Structured logging (optional enhancement)

## Development

### Code Quality

```bash
# Format code
poetry run black app/ tests/

# Lint code
poetry run flake8 app/ tests/

# Type checking
poetry run mypy app/

# Sort imports
poetry run isort app/ tests/
```

### Adding New Endpoints

1. Create route in [app/api/routes.py](app/api/routes.py)
2. Add request/response models in [app/models/schemas.py](app/models/schemas.py)
3. Add logging using `logger.bind(request_id=request_id)` for context
4. Add tests in [tests/test_api.py](tests/test_api.py)

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to extend this example with:
- Database integration (SQLAlchemy, SQLModel)
- Authentication (JWT, OAuth2)
- WebSocket support
- GraphQL endpoints
- Additional middleware
- Custom log formatters

## Kubernetes & Cloud Deployment

### Quick Start

For complete Kubernetes deployment with Fluent Bit and Azure Log Analytics:

```bash
# Build and deploy to AKS
chmod +x k8s/deploy.sh k8s/setup-azure.sh
./k8s/setup-azure.sh  # Setup Azure Log Analytics
./k8s/deploy.sh       # Deploy FastAPI and Fluent Bit
```

### What's Included

**Kubernetes Manifests:**
- 3-pod FastAPI deployment with auto-scaling (3-10 replicas)
- LoadBalancer service for external access
- Horizontal Pod Autoscaler (CPU/Memory based)
- Pod Disruption Budget for high availability
- ConfigMaps for configuration management

**Fluent Bit Setup:**
- DaemonSet on all nodes for log collection
- Kubernetes metadata enrichment
- Azure Log Analytics output
- Structured JSON log forwarding
- Automatic parsing of container logs

**Azure Integration:**
- Log Analytics workspace creation
- Workspace credential management
- Log retention and archival
- KQL query samples
- Alert configuration

### Documentation

- [KUBERNETES.md](KUBERNETES.md) - Complete K8s deployment guide
- [FLUENT_BIT.md](FLUENT_BIT.md) - Fluent Bit configuration details
- [AZURE.md](AZURE.md) - Azure Log Analytics setup and queries

### Key Features

1. **Auto-Scaling:** Scales from 3 to 10 replicas based on CPU/Memory
2. **High Availability:** Pod anti-affinity across nodes, min 2 pods available
3. **Structured Logging:** JSON-formatted logs for easy analysis
4. **Request Tracing:** Unique IDs for distributed request tracking
5. **Cloud Native:** Kusto Query Language (KQL) for advanced analytics
6. **Cost Optimized:** Log rotation, retention policies, and storage archival

### Sample Azure Log Analytics Queries

```kusto
# All logs
FastAPILogs

# Error tracking
FastAPILogs | where level == "ERROR" | order by TimeGenerated desc

# Request latency analysis
FastAPILogs 
| where message contains "Response sent"
| extend latency=tofloat(process_time_ms)
| summarize avg_ms=avg(latency), p95_ms=percentile(latency, 95) by k8s_pod_name

# Request rate
FastAPILogs 
| where message contains "Incoming request"
| summarize request_count=count() by bin(TimeGenerated, 1m)
| render timechart
```

### Production Checklist

- [x] Containerized with Docker
- [x] Kubernetes-ready manifests
- [x] Log aggregation with Fluent Bit
- [x] Cloud-native logging (Azure Log Analytics)
- [x] Auto-scaling and high availability
- [x] Health checks and readiness probes
- [x] Security context and RBAC
- [ ] Persistent volume for state (if needed)
- [ ] Network policies (if needed)
- [ ] Service mesh integration (optional)
- [ ] GitOps setup with ArgoCD (optional)
