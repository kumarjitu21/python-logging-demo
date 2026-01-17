# Correlation ID Integration

## Overview

Correlation IDs are a critical component of distributed tracing and observability in modern applications. This project implements industry-standard correlation ID tracking using contextvars (Python's built-in context management), enabling end-to-end request tracing across microservices.

## Features

- **Automatic Correlation ID Generation**: Every request gets a unique UUID if not provided
- **Header Propagation**: Supports both `X-Correlation-ID` and `X-Request-ID` headers
- **Request Context**: Correlation ID available in request state for all endpoints
- **Context Variables**: Correlation ID maintained in async context for nested operations
- **Structured Logging**: Correlation ID included in all log entries
- **Response Headers**: Correlation ID returned in response headers for client tracking

## Architecture

### Correlation ID Flow

```
Client Request
    ↓
[X-Correlation-ID or X-Request-ID header]
    ↓
LoggingMiddleware (extract or generate)
    ↓
Set in request.state.correlation_id
Set in context variable (contextvars)
    ↓
Route Handlers (access via get_correlation_id())
    ↓
Log Entries (automatically included via logger.bind())
    ↓
Response Headers [X-Correlation-ID, X-Request-ID]
    ↓
Client Response
```

## Implementation Details

### 1. Correlation ID Module (`app/core/correlation_id.py`)

Custom implementation using Python's `contextvars` for managing correlation IDs across async contexts:

```python
import contextvars

_correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id',
    default=None
)

def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context."""
    _correlation_id_var.set(correlation_id)

def get_correlation_id() -> Optional[str]:
    """Get correlation ID from context."""
    return _correlation_id_var.get()
```

**Why contextvars?**
- Built into Python 3.9+
- Designed for async-safe context storage
- No external dependencies
- Industry standard for request tracing

### 2. Middleware Integration (`app/core/middleware.py`)

The `LoggingMiddleware` extracts or generates correlation IDs:

```python
# Extract from headers or generate new UUID
request_correlation_id = (
    request.headers.get("X-Correlation-ID")
    or request.headers.get("X-Request-ID")
    or str(uuid.uuid4())
)

# Store in multiple places for compatibility
request.state.correlation_id = request_correlation_id
request.state.request_id = request_correlation_id

# Set in context for nested operations
set_correlation_id(request_correlation_id)

# Include in response headers
response.headers["X-Correlation-ID"] = request_correlation_id
response.headers["X-Request-ID"] = request_correlation_id
```

### 3. Logging Integration (`app/core/logging.py`)

Correlation ID is automatically included in all logs:

```python
logger.bind(correlation_id=correlation_id).info(
    "Creating new user",
    user_name=user.name,
    user_email=user.email,
)
```

**Console Output:**
```
INFO | app.api.routes:create_user:70 | correlation_id=550e8400-e29b-41d4-a716-446655440000 - Creating new user
```

**JSON Output:**
```json
{
  "timestamp": "2026-01-17T10:30:45.123456",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": "INFO",
  "logger": "app.api.routes",
  "function": "create_user",
  "line": 70,
  "message": "Creating new user",
  "extra": {
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }
}
```

### 4. Route Handler Usage (`app/api/routes.py`)

Helpers for accessing correlation ID:

```python
def get_correlation_id(request: Request) -> str:
    """Extract correlation ID from request state."""
    return getattr(request.state, "correlation_id", "N/A")

# Usage in endpoints
@router.post("/users")
async def create_user(user: UserCreate, request: Request) -> UserResponse:
    correlation_id = get_correlation_id(request)
    logger.bind(correlation_id=correlation_id).info(
        "Creating new user",
        user_name=user.name,
    )
```

## Usage Examples

### 1. Generate Correlation ID Automatically

```bash
curl http://localhost:8000/api/health

# Response headers:
# x-correlation-id: 550e8400-e29b-41d4-a716-446655440000
# x-request-id: 550e8400-e29b-41d4-a716-446655440000
```

### 2. Propagate Existing Correlation ID

```bash
curl -H "X-Correlation-ID: my-trace-id-12345" http://localhost:8000/api/health

# Response headers:
# x-correlation-id: my-trace-id-12345
# x-request-id: my-trace-id-12345
```

### 3. End-to-End Tracing

Client → Service A → Service B → Service C

```bash
# Initial request
TRACE_ID=$(uuidgen)
curl -H "X-Correlation-ID: $TRACE_ID" http://service-a/api/process

# Service A logs with $TRACE_ID
# Service A calls Service B with same $TRACE_ID
curl -H "X-Correlation-ID: $TRACE_ID" http://service-b/api/process

# Service B logs with $TRACE_ID
# All logs correlated in Fluent Bit / Azure Log Analytics
```

### 4. Log Correlation in Fluent Bit

Logs automatically include correlation_id:

```
[2026-01-17T10:30:45.123Z] correlation_id=550e8400-e29b-41d4-a716-446655440000 user_id=42 status=201
[2026-01-17T10:30:46.456Z] correlation_id=550e8400-e29b-41d4-a716-446655440000 operation=send_notification recipient=user@example.com
[2026-01-17T10:30:47.789Z] correlation_id=550e8400-e29b-41d4-a716-446655440000 operation=complete result=success
```

## Testing

### Unit Tests

The test suite includes correlation ID verification:

```python
@pytest.mark.asyncio
async def test_correlation_id_header():
    """Test that correlation ID is returned in response headers."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert "x-correlation-id" in response.headers

@pytest.mark.asyncio
async def test_correlation_id_propagation():
    """Test that custom correlation ID is propagated."""
    test_id = str(uuid.uuid4())
    headers = {"X-Correlation-ID": test_id}
    response = await client.get("/api/health", headers=headers)
    assert response.headers.get("x-correlation-id") == test_id
```

**Run tests:**
```bash
poetry run pytest tests/ -v
# All 9 tests PASSED ✓
```

## Integration with Observability Stack

### Azure Log Analytics

Correlation ID enables log correlation in Azure:

```kusto
// Query logs for a specific request trace
customLogs
| where correlation_id == "550e8400-e29b-41d4-a716-446655440000"
| order by timestamp asc
| project timestamp, level, message, user_id, operation
```

### Fluent Bit Configuration

```conf
[INPUT]
    Name tail
    Path /var/log/app/structured.json
    Tag app.*

[OUTPUT]
    Name azure
    Match app.*
    Customer_ID ${CUSTOMER_ID}
    Shared_Key ${SHARED_KEY}
    Table_Name logs
    # correlation_id automatically included in JSON
```

### Kubernetes Integration

In Kubernetes manifests, correlation IDs flow through pod logs:

```bash
# View logs for a specific trace
kubectl logs -f deployment/app -n fastapi | grep "550e8400-e29b-41d4-a716-446655440000"
```

## Best Practices

### 1. Always Forward Correlation IDs
```python
# When calling downstream services
import httpx
client = httpx.AsyncClient()
headers = {"X-Correlation-ID": correlation_id}
response = await client.get(url, headers=headers)
```

### 2. Use Standard Headers
- Primary: `X-Correlation-ID` (W3C Trace Context aligned)
- Fallback: `X-Request-ID` (backward compatible)

### 3. Include in All Logs
```python
logger.bind(correlation_id=correlation_id).info(
    "operation_completed",
    duration_ms=elapsed,
    status="success"
)
```

### 4. Propagate Through Async Code
Context variables automatically work with async/await:

```python
async def background_task():
    # Correlation ID still available from context
    correlation_id = get_correlation_id()
    logger.bind(correlation_id=correlation_id).info("Background task running")

asyncio.create_task(background_task())
```

### 5. Return to Clients
Always include in response headers for client-side tracking:

```python
response.headers["X-Correlation-ID"] = correlation_id
```

## Monitoring and Troubleshooting

### Check if Correlation ID is Working

```bash
# Start the app
poetry run python -m uvicorn app.main:app --reload

# In another terminal, test
curl -v http://localhost:8000/api/health 2>&1 | grep -i "x-correlation"

# Check logs for correlation_id field
tail -f logs/structured.json | python -m json.tool | grep correlation_id
```

### Correlate Requests Across Services

```bash
# 1. Make request and capture correlation ID
TRACE_ID=$(curl -s http://service-a/api/process | jq -r '.trace_id')

# 2. Query logs with this ID
grep "$TRACE_ID" logs/*.json

# 3. View all services' logs for this trace
az log-analytics query --workspace-id $WS_ID \
  --query "customLogs | where correlation_id == '$TRACE_ID'"
```

## Performance Impact

- **Negligible**: ContextVars are extremely lightweight
- **No serialization overhead**: Only string storage
- **Async-friendly**: No blocking operations
- **Memory efficient**: Single UUID per request

## Standards and References

- **W3C Trace Context**: https://www.w3.org/TR/trace-context/
- **Python contextvars**: https://docs.python.org/3/library/contextvars.html
- **OpenTelemetry**: https://opentelemetry.io/
- **Industry Practice**: Standard in distributed tracing (Datadog, New Relic, Splunk)

## Troubleshooting

### Correlation ID not appearing in logs

**Check 1**: Verify middleware is registered
```python
app.add_middleware(LoggingMiddleware)  # Must be added
```

**Check 2**: Ensure logger.bind() is called
```python
logger.bind(correlation_id=correlation_id).info(...)  # Correct
logger.info(...)  # Missing correlation_id
```

### Correlation ID not propagated to downstream services

**Check**: Include header in outbound requests
```python
# Wrong - correlation ID lost
await httpx.get(url)

# Correct - correlation ID preserved
correlation_id = get_correlation_id()
await httpx.get(url, headers={"X-Correlation-ID": correlation_id})
```

### Performance degradation

**Solution**: Use correlation_id parameter in logger.bind()
```python
# Efficient
logger.bind(correlation_id=cid).info(msg)

# Avoid expensive operations in logging
logger.bind(correlation_id=cid).info(msg, expensive_fn())
```

## Future Enhancements

1. **OpenTelemetry Integration**: Automatic span generation from correlation IDs
2. **B3 Propagation**: Support Zipkin B3 headers
3. **Baggage**: Add W3C Baggage support for metadata propagation
4. **Tracing Dashboard**: Visualize request flows in Azure / Kibana
5. **Custom Extractors**: Plugin system for custom ID extraction logic

## Related Documentation

- [Logging Architecture](LOGGING.md)
- [Kubernetes Deployment](KUBERNETES.md)
- [Azure Log Analytics Setup](AZURE.md)
- [Fluent Bit Configuration](FLUENT_BIT.md)
- [CI/CD Pipelines](CI_CD.md)
