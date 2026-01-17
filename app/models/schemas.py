"""Request/response models for structured data validation."""
from typing import Optional

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")


class UserCreate(BaseModel):
    """User creation request model."""

    name: str = Field(..., min_length=1, max_length=100, description="User name")
    email: str = Field(..., description="User email")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")


class UserResponse(BaseModel):
    """User response model."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    age: Optional[int] = Field(None, description="User age")

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Unique request ID for tracing")
