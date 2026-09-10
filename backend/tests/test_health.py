"""
Tests for health check endpoints and database connectivity.
"""
def test_health_check_returns_ok_and_database_connected(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "app" in data


def test_api_health_check_returns_ok_and_database_connected(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "app" in data
