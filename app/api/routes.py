"""API routes for health checks and user management."""
from fastapi import APIRouter, Request, HTTPException
from loguru import logger
from app.models.schemas import HealthCheckResponse, UserCreate, UserResponse
from app.core.config import settings

router = APIRouter()

# In-memory database for demo purposes
users_db: dict = {}
next_user_id = 1


def get_correlation_id(request: Request) -> str:
    """Extract correlation ID from request state."""
    return getattr(request.state, "correlation_id", "N/A")


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check(request: Request) -> HealthCheckResponse:
    """
    Health check endpoint to verify service status.

    Returns:
        HealthCheckResponse: Service status and version
    """
    correlation_id = get_correlation_id(request)

    logger.bind(correlation_id=correlation_id).info(
        "Health check performed",
        endpoint="/health",
    )

    return HealthCheckResponse(
        status="healthy",
        version=settings.version,
    )


@router.post(
    "/users",
    response_model=UserResponse,
    tags=["Users"],
    summary="Create a new user",
)
async def create_user(user: UserCreate, request: Request) -> UserResponse:
    """
    Create a new user with validated data.

    Args:
        user: User creation request
        request: FastAPI request object

    Returns:
        UserResponse: Created user details
    """
    correlation_id = get_correlation_id(request)
    global next_user_id

    logger.bind(correlation_id=correlation_id).info(
        "Creating new user",
        user_name=user.name,
        user_email=user.email,
        user_age=user.age,
    )

    try:
        # Create user
        user_id = next_user_id
        next_user_id += 1

        new_user = UserResponse(
            id=user_id,
            name=user.name,
            email=user.email,
            age=user.age,
        )

        users_db[user_id] = new_user

        logger.bind(correlation_id=correlation_id).info(
            "User created successfully",
            user_id=user_id,
            user_name=user.name,
        )

        return new_user

    except Exception as exc:
        logger.bind(correlation_id=correlation_id).error(
            "Error creating user",
            error=str(exc),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by ID",
)
async def get_user(user_id: int, request: Request) -> UserResponse:
    """
    Retrieve user details by ID.

    Args:
        user_id: User ID to retrieve
        request: FastAPI request object

    Returns:
        UserResponse: User details

    Raises:
        HTTPException: If user not found
    """
    correlation_id = get_correlation_id(request)

    logger.bind(correlation_id=correlation_id).info(
        "Fetching user details",
        user_id=user_id,
    )

    if user_id not in users_db:
        logger.bind(correlation_id=correlation_id).warning(
            "User not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    user = users_db[user_id]

    logger.bind(correlation_id=correlation_id).info(
        "User retrieved successfully",
        user_id=user_id,
        user_name=user.name,
    )

    return user


@router.get(
    "/users",
    response_model=list[UserResponse],
    tags=["Users"],
    summary="List all users",
)
async def list_users(request: Request) -> list[UserResponse]:
    """
    List all users in the system.

    Args:
        request: FastAPI request object

    Returns:
        List of all users
    """
    correlation_id = get_correlation_id(request)

    logger.bind(correlation_id=correlation_id).info(
        "Fetching all users",
        total_users=len(users_db),
    )

    return list(users_db.values())


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user details",
)
async def update_user(user_id: int, user: UserCreate, request: Request) -> UserResponse:
    """
    Update existing user details.

    Args:
        user_id: User ID to update
        user: Updated user data
        request: FastAPI request object

    Returns:
        UserResponse: Updated user details

    Raises:
        HTTPException: If user not found
    """
    correlation_id = get_correlation_id(request)

    logger.bind(correlation_id=correlation_id).info(
        "Updating user",
        user_id=user_id,
        new_name=user.name,
        new_email=user.email,
    )

    if user_id not in users_db:
        logger.bind(correlation_id=correlation_id).warning(
            "Cannot update - user not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    try:
        updated_user = UserResponse(
            id=user_id,
            name=user.name,
            email=user.email,
            age=user.age,
        )

        users_db[user_id] = updated_user

        logger.bind(correlation_id=correlation_id).info(
            "User updated successfully",
            user_id=user_id,
        )

        return updated_user

    except Exception as exc:
        logger.bind(correlation_id=correlation_id).error(
            "Error updating user",
            user_id=user_id,
            error=str(exc),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete(
    "/users/{user_id}",
    tags=["Users"],
    summary="Delete user",
)
async def delete_user(user_id: int, request: Request) -> dict:
    """
    Delete a user by ID.

    Args:
        user_id: User ID to delete
        request: FastAPI request object

    Returns:
        Success message

    Raises:
        HTTPException: If user not found
    """
    correlation_id = get_correlation_id(request)

    logger.bind(correlation_id=correlation_id).info(
        "Deleting user",
        user_id=user_id,
    )

    if user_id not in users_db:
        logger.bind(correlation_id=correlation_id).warning(
            "Cannot delete - user not found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    try:
        del users_db[user_id]

        logger.bind(correlation_id=correlation_id).info(
            "User deleted successfully",
            user_id=user_id,
        )

        return {"message": f"User {user_id} deleted successfully"}

    except Exception as exc:
        logger.bind(correlation_id=correlation_id).error(
            "Error deleting user",
            user_id=user_id,
            error=str(exc),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to delete user")
