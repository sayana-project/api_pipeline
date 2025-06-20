from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_home():
    response = client.get("/api/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_protected_route():
    response = client.get("/api/users/", auth=("admin", "password"))
    assert response.status_code == 200

def test_wrong_auth():
    response = client.get("/api/users/", auth=("baduser", "badpass"))
    assert response.status_code == 401

def test_search():
    response = client.get("/api/users/search?q=a", auth=("admin", "password"))
    assert response.status_code == 200 or response.status_code == 404