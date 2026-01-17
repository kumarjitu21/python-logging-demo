"""Tests for the FastAPI application."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_create_user():
    """Test user creation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        response = await client.post("/api/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_user():
    """Test get user by ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create user first
        user_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "age": 28
        }
        create_response = await client.post("/api/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Get user
        response = await client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_list_users():
    """Test list all users."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_request_id_header():
    """Test that request ID is returned in response headers."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_user_not_found():
    """Test get non-existent user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/users/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_validation_error():
    """Test invalid user data."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        invalid_data = {
            "name": "",  # Empty name
            "email": "invalid"
        }
        response = await client.post("/api/users", json=invalid_data)
        assert response.status_code == 422  # Validation error
