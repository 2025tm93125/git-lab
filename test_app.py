from app import app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    data = response.get_json()

    assert data["application"] == "ACEest Fitness & Gym"
    assert data["status"] == "running"


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_calculate_calories():
    client = app.test_client()

    response = client.post(
        "/calculate-calories",
        json={"weight": 70, "factor": 22}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["weight"] == 70.0
    assert data["factor"] == 22.0
    assert data["calories"] == 1540.0
