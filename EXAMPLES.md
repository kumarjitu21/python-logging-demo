# Examples and Use Cases

This document provides practical examples of how to use the logging system in different scenarios.

## Table of Contents

1. [API Endpoint Examples](#api-endpoint-examples)
2. [Database Operations](#database-operations)
3. [Error Handling](#error-handling)
4. [Background Tasks](#background-tasks)
5. [Debugging Patterns](#debugging-patterns)
6. [Integration Patterns](#integration-patterns)

## API Endpoint Examples

### Simple GET Endpoint

```python
from fastapi import APIRouter, Request
from loguru import logger
from app.models.schemas import HealthCheckResponse

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request):
    """Health check endpoint."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info("Health check performed")
    
    return HealthCheckResponse(status="healthy", version="0.1.0")
```

### POST with Validation

```python
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, request: Request):
    """Create a new user."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    # Log input
    logger.bind(request_id=request_id).info(
        "Creating new user",
        name=user.name,
        email=user.email,
        age=user.age,
    )
    
    # Validate (Pydantic handles this)
    if not user.email:
        logger.bind(request_id=request_id).warning(
            "Invalid email provided",
            email=user.email,
        )
        raise HTTPException(status_code=400, detail="Invalid email")
    
    # Create user
    new_user = database.create(user)
    
    # Log success
    logger.bind(request_id=request_id).info(
        "User created successfully",
        user_id=new_user.id,
        user_name=new_user.name,
    )
    
    return new_user
```

### PUT with Conditional Logic

```python
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, request: Request):
    """Update a user."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Updating user",
        user_id=user_id,
        new_name=user.name,
    )
    
    # Check if user exists
    existing_user = database.get(user_id)
    if not existing_user:
        logger.bind(request_id=request_id).warning(
            "User not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log changes
    if existing_user.name != user.name:
        logger.bind(request_id=request_id).debug(
            "Name changed",
            old_name=existing_user.name,
            new_name=user.name,
        )
    
    # Update user
    updated = database.update(user_id, user)
    
    logger.bind(request_id=request_id).info(
        "User updated successfully",
        user_id=user_id,
    )
    
    return updated
```

### DELETE with Cascading

```python
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    """Delete a user."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Deleting user",
        user_id=user_id,
    )
    
    # Check if user exists
    user = database.get(user_id)
    if not user:
        logger.bind(request_id=request_id).warning(
            "Cannot delete - user not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404)
    
    # Log user details before deletion
    logger.bind(request_id=request_id).debug(
        "User details before deletion",
        user_id=user.id,
        user_name=user.name,
        user_email=user.email,
    )
    
    # Delete related records
    logger.bind(request_id=request_id).debug(
        "Deleting related records",
        user_id=user_id,
    )
    database.delete_related(user_id)
    
    # Delete user
    database.delete(user_id)
    
    logger.bind(request_id=request_id).info(
        "User deleted successfully",
        user_id=user_id,
    )
    
    return {"message": "User deleted"}
```

## Database Operations

### SQLAlchemy Query Logging

```python
from sqlalchemy import select
from loguru import logger

async def get_user_with_posts(user_id: int, request: Request):
    """Get user with all posts."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).debug(
        "Querying user with posts",
        user_id=user_id,
    )
    
    # Query
    query = select(User).where(User.id == user_id)
    
    try:
        user = await db.execute(query)
        user_data = user.scalars().first()
        
        if not user_data:
            logger.bind(request_id=request_id).warning(
                "User not found in database",
                user_id=user_id,
            )
            return None
        
        logger.bind(request_id=request_id).info(
            "User retrieved from database",
            user_id=user_id,
            post_count=len(user_data.posts),
        )
        
        return user_data
        
    except Exception as exc:
        logger.bind(request_id=request_id).error(
            "Database query error",
            user_id=user_id,
            error=str(exc),
            exc_info=True,
        )
        raise
```

### Batch Operations

```python
async def create_users_batch(users: list[UserCreate], request: Request):
    """Create multiple users."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Starting batch user creation",
        total_count=len(users),
    )
    
    created_users = []
    failed_count = 0
    
    for idx, user in enumerate(users):
        try:
            logger.bind(request_id=request_id).debug(
                "Creating user",
                batch_index=idx,
                user_email=user.email,
            )
            
            new_user = await db.create_user(user)
            created_users.append(new_user)
            
            logger.bind(request_id=request_id).debug(
                "User created in batch",
                batch_index=idx,
                user_id=new_user.id,
            )
            
        except Exception as exc:
            failed_count += 1
            logger.bind(request_id=request_id).warning(
                "Failed to create user in batch",
                batch_index=idx,
                user_email=user.email,
                error=str(exc),
            )
    
    logger.bind(request_id=request_id).info(
        "Batch user creation completed",
        total=len(users),
        created=len(created_users),
        failed=failed_count,
    )
    
    return created_users
```

## Error Handling

### Try-Except with Logging

```python
from fastapi import HTTPException
from loguru import logger

async def process_payment(user_id: int, amount: float, request: Request):
    """Process user payment."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Processing payment",
        user_id=user_id,
        amount=amount,
    )
    
    try:
        # Get user
        user = database.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check balance
        if user.balance < amount:
            logger.bind(request_id=request_id).warning(
                "Insufficient balance",
                user_id=user_id,
                balance=user.balance,
                required=amount,
            )
            raise ValueError("Insufficient balance")
        
        # Process payment
        logger.bind(request_id=request_id).debug(
            "Deducting amount from balance",
            user_id=user_id,
            deduct_amount=amount,
        )
        
        database.deduct_balance(user_id, amount)
        
        logger.bind(request_id=request_id).info(
            "Payment processed successfully",
            user_id=user_id,
            amount=amount,
            new_balance=user.balance - amount,
        )
        
        return {"status": "success", "amount": amount}
        
    except ValueError as exc:
        logger.bind(request_id=request_id).warning(
            "Payment validation error",
            user_id=user_id,
            error=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc))
        
    except Exception as exc:
        logger.bind(request_id=request_id).error(
            "Payment processing error",
            user_id=user_id,
            amount=amount,
            error=str(exc),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Payment processing failed")
```

### Custom Exception Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError with logging."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).error(
        "ValueError occurred",
        error=str(exc),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
        headers={"X-Request-ID": request_id},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with logging."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).critical(
        "Unhandled exception",
        error_type=type(exc).__name__,
        error=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
        headers={"X-Request-ID": request_id},
    )
```

## Background Tasks

### Scheduled Task Logging

```python
from celery import Celery
from loguru import logger
import time

celery_app = Celery("tasks")

@celery_app.task
def sync_external_data():
    """Sync data from external API."""
    task_id = sync_external_data.request.id
    
    logger.info(
        "Starting external data sync",
        task_id=task_id,
    )
    
    start_time = time.time()
    
    try:
        # Fetch data
        logger.debug("Fetching data from external API", task_id=task_id)
        data = fetch_external_api()
        
        logger.info(
            "Data fetched",
            task_id=task_id,
            record_count=len(data),
        )
        
        # Process data
        processed_count = 0
        for record in data:
            try:
                database.save(record)
                processed_count += 1
            except Exception as exc:
                logger.warning(
                    "Failed to process record",
                    task_id=task_id,
                    record_id=record.id,
                    error=str(exc),
                )
        
        duration = time.time() - start_time
        
        logger.info(
            "External data sync completed",
            task_id=task_id,
            processed=processed_count,
            duration_seconds=f"{duration:.2f}",
        )
        
    except Exception as exc:
        logger.error(
            "External data sync failed",
            task_id=task_id,
            error=str(exc),
            exc_info=True,
        )
        raise
```

## Debugging Patterns

### Performance Profiling

```python
import time
from loguru import logger

async def slow_operation(request: Request):
    """Operation that needs profiling."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info("Starting slow operation")
    
    checkpoints = {}
    
    # Phase 1
    start = time.time()
    phase1_result = await phase1()
    checkpoints['phase1'] = time.time() - start
    
    # Phase 2
    start = time.time()
    phase2_result = await phase2(phase1_result)
    checkpoints['phase2'] = time.time() - start
    
    # Phase 3
    start = time.time()
    result = await phase3(phase2_result)
    checkpoints['phase3'] = time.time() - start
    
    logger.bind(request_id=request_id).info(
        "Operation completed",
        phase1_ms=f"{checkpoints['phase1']*1000:.2f}",
        phase2_ms=f"{checkpoints['phase2']*1000:.2f}",
        phase3_ms=f"{checkpoints['phase3']*1000:.2f}",
        total_ms=f"{sum(checkpoints.values())*1000:.2f}",
    )
    
    return result
```

### State Tracking

```python
async def complex_workflow(user_id: int, request: Request):
    """Track workflow state for debugging."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    state = {
        "user_id": user_id,
        "steps": [],
        "current_step": None,
    }
    
    try:
        # Step 1: Validate input
        state["current_step"] = "validate"
        logger.bind(request_id=request_id, **state).debug("Validating input")
        validate_user(user_id)
        state["steps"].append("validate")
        
        # Step 2: Load data
        state["current_step"] = "load_data"
        logger.bind(request_id=request_id, **state).debug("Loading data")
        data = load_user_data(user_id)
        state["steps"].append("load_data")
        
        # Step 3: Process data
        state["current_step"] = "process"
        logger.bind(request_id=request_id, **state).debug("Processing data")
        processed = process_data(data)
        state["steps"].append("process")
        
        # Step 4: Save results
        state["current_step"] = "save"
        logger.bind(request_id=request_id, **state).debug("Saving results")
        result = save_results(processed)
        state["steps"].append("save")
        
        logger.bind(request_id=request_id).info(
            "Workflow completed",
            **state,
        )
        
        return result
        
    except Exception as exc:
        logger.bind(request_id=request_id).error(
            "Workflow failed",
            **state,
            error=str(exc),
            exc_info=True,
        )
        raise
```

## Integration Patterns

### Multiple Service Calls

```python
async def aggregate_user_data(user_id: int, request: Request):
    """Aggregate data from multiple services."""
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.bind(request_id=request_id).info(
        "Aggregating user data",
        user_id=user_id,
    )
    
    results = {}
    
    # Call service 1
    try:
        logger.bind(request_id=request_id).debug(
            "Calling service 1",
            user_id=user_id,
        )
        results['profile'] = await service1.get_profile(user_id)
        logger.bind(request_id=request_id).debug("Service 1 success")
    except Exception as exc:
        logger.warning(
            "Service 1 failed",
            request_id=request_id,
            error=str(exc),
        )
    
    # Call service 2
    try:
        logger.bind(request_id=request_id).debug(
            "Calling service 2",
            user_id=user_id,
        )
        results['orders'] = await service2.get_orders(user_id)
        logger.bind(request_id=request_id).debug("Service 2 success")
    except Exception as exc:
        logger.warning(
            "Service 2 failed",
            request_id=request_id,
            error=str(exc),
        )
    
    logger.bind(request_id=request_id).info(
        "Data aggregation completed",
        user_id=user_id,
        services_available=list(results.keys()),
    )
    
    return results
```

## See Also

- [Main Logging Documentation](LOGGING.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [Loguru Documentation](https://loguru.readthedocs.io/)
