import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.database import get_db_connection

@pytest.fixture
def client(tmp_path):
    database = str(tmp_path / "test.db")

    app = create_app({
        "TESTING": True,
        "DATABASE": database,
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "TestPassword123!",
        "SECRET_KEY": "test-secret"
    })

    with app.test_client() as test_client:
        yield test_client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["application"] == "ACEest Fitness & Gym"

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

def test_login_success(client):
    response = client.post("/api/login", json={
        "username": "admin",
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    assert response.json["role"] == "Admin"

def test_login_failure(client):
    response = client.post("/api/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_create_and_list_client(client):
    created = client.post("/api/clients", json={"name": "Test Client"})
    assert created.status_code == 201

    response = client.get("/api/clients")
    assert response.status_code == 200
    assert response.json[0]["name"] == "Test Client"

def test_duplicate_client(client):
    client.post("/api/clients", json={"name": "Test Client"})
    response = client.post("/api/clients", json={"name": "Test Client"})
    assert response.status_code == 409

def test_add_workout(client):
    created = client.post("/api/clients", json={"name": "Workout Client"})
    client_id = created.json["id"]

    response = client.post(
        f"/api/clients/{client_id}/workouts",
        json={"workout_type": "Strength", "duration_min": 45}
    )
    assert response.status_code == 201

def test_missing_client_membership(client):
    response = client.get("/api/clients/999/membership")
    assert response.status_code == 404
