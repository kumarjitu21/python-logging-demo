# Logging Architecture & Best Practices

This document explains the logging implementation and how to use it effectively.

## Overview

The project uses **Loguru** - a modern Python logging library that simplifies structured logging with:
- Multiple handlers (console, file, JSON)
- Automatic log rotation and compression
- Context binding for request tracing
- Rich formatting and color output

## Logging Configuration

### Setup Location
Configuration is in [app/core/logging.py](app/core/logging.py)

### Log Handlers

#### 1. Console Output (Development)
- **Format**: Colored, human-readable
- **Level**: Controlled by `LOG_LEVEL` env var
- **Purpose**: Real-time monitoring during development

```
2026-01-17 14:46:09 | INFO | app.api.routes:create_user:60 - Creating new user
```

#### 2. General Application Log (app.log)
- **Path**: `logs/app.log`
- **Format**: Structured text with context
- **Rotation**: 100 MB
- **Retention**: 10 days
- **Compression**: ZIP on rotation

#### 3. Error Log (errors.log)
- **Path**: `logs/errors.log`
- **Format**: Detailed error information
- **Level**: ERROR and above only
- **Rotation**: 50 MB
- **Retention**: 30 days (longer than general logs)

#### 4. Structured JSON Log (structured.json)
- **Path**: `logs/structured.json`
- **Format**: Machine-readable JSON
- **Purpose**: Integration with log aggregation tools
- **Rotation**: 100 MB

## Request Tracing

### Unique Request IDs

Every HTTP request gets a unique request ID that:
1. Is generated in middleware
2. Is added to request state
3. Is bound to all logs for that request
4. Is returned in response headers (`X-Request-ID`)

### Example Log Entry with Request Context

```python
logger.bind(request_id=request_id).info(
    "Creating new user",
    user_name="John Doe",
    user_email="john@example.com",
    user_age=30,
)
```

This produces:
```
2026-01-17 14:46:09 | INFO | app.api.routes:create_user:60 - Creating new user
request_id=550e8400-e29b-41d4-a716-446655440000
user_name=John Doe
user_email=john@example.com
user_age=30
```

And in JSON:
```json
{
  "timestamp": "2026-01-17T14:46:09.123456",
  "level": "INFO",
  "logger": "app.api.routes",
  "function": "create_user",
  "line": 60,
  "message": "Creating new user",
  "extra": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "user_age": 30
  }
}
```

## Usage Examples

### Basic Logging

```python
from loguru import logger

# Simple info log
logger.info("User created successfully")

# With extra context
logger.info("User created", user_id=123, user_name="John")

# Different log levels
logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue")
```

### With Request Context

```python
from fastapi import Request
from loguru import logger

async def create_user(user: UserCreate, request: Request):
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Creating new user",
        user_name=user.name,
        user_email=user.email,
    )
    
    try:
        # Create user logic
        logger.bind(request_id=request_id).info(
            "User created successfully",
            user_id=new_user.id,
        )
        return new_user
    except Exception as exc:
        logger.bind(request_id=request_id).error(
            "Error creating user",
            error=str(exc),
            exc_info=True,
        )
        raise
```

### Performance Monitoring

The middleware automatically logs:
- Request method and path
- Response status code
- Processing time in milliseconds

```python
# Middleware log output
2026-01-17 14:46:09 | INFO | app.core.middleware:dispatch:39 - Response sent
method=POST path=/api/users status_code=200 process_time_ms=45.23
```

## Log Levels

Choose appropriate levels:

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Detailed diagnostic info | "Parsing user input: ..." |
| INFO | General informational | "User created successfully" |
| WARNING | Warning but not error | "Missing optional field" |
| ERROR | Error occurred | "Database connection failed" |
| CRITICAL | Severe error | "Out of memory" |

Set via environment:
```bash
export LOG_LEVEL=DEBUG    # Most verbose
export LOG_LEVEL=INFO     # Default
export LOG_LEVEL=WARNING  # Less verbose
export LOG_LEVEL=ERROR    # Only errors
```

## Middleware Logging Details

The [LoggingMiddleware](app/core/middleware.py) automatically logs:

### On Request
- Method (GET, POST, etc.)
- Path (/api/users, /api/health, etc.)
- Query parameters
- Client IP address
- Generated request ID

### On Response
- Status code (200, 404, 500, etc.)
- Processing time
- Request ID for correlation

### On Error
- Error message
- Processing time before error
- Stack trace (with exc_info=True)

## Integration with Log Aggregation Tools

### Elasticsearch + Logstash + Kibana (ELK Stack)

Parse JSON logs with Logstash:
```ruby
input {
  file {
    path => "/app/logs/structured.json"
    codec => "json"
  }
}

filter {
  if [level] == "ERROR" {
    mutate { add_tag => [ "error" ] }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

### Datadog

Send logs to Datadog:
```bash
# Configure Datadog Agent to read logs
# In datadog-agent/conf.d/python.d/conf.yaml:

logs:
  - type: file
    path: /app/logs/structured.json
    service: fastapi-demo
    source: python
    tags:
      - env:production
```

### Splunk

Index JSON logs with Splunk:
```
TRANSFORMS-set-sourcetype = structured_json
REGEX = (?<json>.*)
```

### AWS CloudWatch

Send logs via CloudWatch agent:
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/app/logs/app.log",
            "log_group_name": "/fastapi/app",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

## Log File Management

### Automatic Rotation

Files rotate automatically when they reach size limits:
- **app.log**: 100 MB
- **errors.log**: 50 MB
- **structured.json**: 100 MB

### Retention Policies

Files are kept for:
- **app.log**: 10 days
- **errors.log**: 30 days
- **structured.json**: 10 days

### Manual Cleanup

```bash
# Remove all logs
rm -rf logs/*

# Archive old logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

## Performance Considerations

### 1. Log Level
- Production: `INFO` or `WARNING`
- Development: `DEBUG`
- Avoid DEBUG in production (verbose output)

### 2. Disk I/O
- Log rotation happens automatically
- Compression reduces disk space
- Monitor disk usage

### 3. Network
- Don't send all logs to remote service
- Filter by level (errors only in production)
- Batch and compress before sending

### 4. Memory
- Loguru is memory efficient
- Context binding uses minimal memory
- JSON formatting is fast

## Troubleshooting

### Logs not appearing
```bash
# Check log directory exists
ls -la logs/

# Check file permissions
chmod 644 logs/*.log

# Verify log level setting
echo $LOG_LEVEL
```

### Log files growing too large
1. Check rotation settings in `app/core/logging.py`
2. Reduce retention period
3. Increase rotation size threshold
4. Enable compression

### Performance degradation
1. Reduce log level
2. Disable JSON logger if not using
3. Check disk I/O
4. Monitor file descriptors

## Best Practices

### ✅ Do:
- Use appropriate log levels
- Include request ID in all logs
- Log at entry and exit of functions
- Include relevant context in logs
- Handle exceptions with logging

### ❌ Don't:
- Log passwords or sensitive data
- Use print() instead of logger
- Log everything at ERROR level
- Ignore log files growing
- Mix logging libraries

## Examples

### Logging a Function Call

```python
from loguru import logger

async def get_user(user_id: int, request: Request):
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).debug(
        "Fetching user",
        user_id=user_id,
    )
    
    if user_id not in database:
        logger.bind(request_id=request_id).warning(
            "User not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404)
    
    user = database[user_id]
    
    logger.bind(request_id=request_id).info(
        "User retrieved",
        user_id=user_id,
        user_name=user.name,
    )
    
    return user
```

### Logging Database Operations

```python
async def save_user(user: User):
    logger.info(
        "Saving user to database",
        user_id=user.id,
        user_name=user.name,
    )
    
    try:
        db.add(user)
        db.commit()
        logger.info("User saved successfully", user_id=user.id)
    except Exception as exc:
        db.rollback()
        logger.error(
            "Failed to save user",
            user_id=user.id,
            error=str(exc),
            exc_info=True,
        )
        raise
```

## Configuration Reference

Edit `app/core/logging.py` to customize:

```python
# Console handler
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | {name}:{function}:{line} - {message}",
    level=settings.log_level,
    colorize=True,
)

# File handler
logger.add(
    "logs/app.log",
    rotation="100 MB",      # Rotate at 100 MB
    retention="10 days",    # Keep for 10 days
    compression="zip",      # Compress rotated files
)
```

## See Also

- [Loguru Documentation](https://loguru.readthedocs.io/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Python Logging Best Practices](https://docs.python.org/3/library/logging.html)
