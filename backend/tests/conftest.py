import os
import pytest

# Enforce testing environment variables
os.environ["FLASK_ENV"] = "testing"
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"
os.environ["SECRET_KEY"] = "test-secret-key"

from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"]
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_headers(client):
    # Register and login an admin user
    client.post("/auth/register", json={
        "username": "admin_user",
        "password": "securepassword123",
        "role": "admin"
    })
    res = client.post("/auth/login", json={
        "username": "admin_user",
        "password": "securepassword123"
    })
    token = res.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def operator_headers(client):
    # Register and login an operator user
    client.post("/auth/register", json={
        "username": "operator_user",
        "password": "securepassword123",
        "role": "operator"
    })
    res = client.post("/auth/login", json={
        "username": "operator_user",
        "password": "securepassword123"
    })
    token = res.json["access_token"]
    return {"Authorization": f"Bearer {token}"}
