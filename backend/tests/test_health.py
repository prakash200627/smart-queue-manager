def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json
    assert data["status"] == "ok"
    assert data["service"] == "smart-queue-manager"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert data["details"]["database"] == "ok"
