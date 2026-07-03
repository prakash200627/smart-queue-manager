import pytest

def test_register_happy_path(client):
    res = client.post("/auth/register", json={
        "username": "new_user",
        "password": "strongpassword123",
        "role": "customer"
    })
    assert res.status_code == 200
    assert res.json["message"] == "User registered"

def test_register_duplicate_username(client):
    # First registration
    client.post("/auth/register", json={
        "username": "duplicate_user",
        "password": "strongpassword123"
    })
    # Duplicate registration
    res = client.post("/auth/register", json={
        "username": "duplicate_user",
        "password": "differentpassword"
    })
    assert res.status_code == 400
    assert "Username already exists" in res.json["error"]

def test_register_validation_missing_fields(client):
    res = client.post("/auth/register", json={
        "password": "strongpassword123"
    })
    assert res.status_code == 400
    assert res.json["field"] == "username"
    assert "username is required" in res.json["error"]

def test_register_validation_short_password(client):
    res = client.post("/auth/register", json={
        "username": "short_pass",
        "password": "123"
    })
    assert res.status_code == 400
    assert res.json["field"] == "password"
    assert "Length must be between 6 and 255." in res.json["error"]

def test_login_happy_path(client):
    client.post("/auth/register", json={
        "username": "login_user",
        "password": "strongpassword123"
    })
    res = client.post("/auth/login", json={
        "username": "login_user",
        "password": "strongpassword123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json
    assert res.json["username"] == "login_user"
    assert res.json["role"] == "customer"

def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "wrong_pass_user",
        "password": "strongpassword123"
    })
    res = client.post("/auth/login", json={
        "username": "wrong_pass_user",
        "password": "incorrectpassword"
    })
    assert res.status_code == 401
    assert "Invalid credentials" in res.json["error"]

def test_rate_limiting(client):
    # Make 5 requests within limits
    for i in range(5):
        res = client.post("/auth/login", json={
            "username": f"user_{i}",
            "password": "somepassword"
        })
        assert res.status_code != 429
        
    # The 6th request should hit the 5 per minute limit
    res = client.post("/auth/login", json={
        "username": "rate_limited_user",
        "password": "somepassword"
    })
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json["error"]
