import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "AI RADAR"
    assert data["database"] == "healthy"

def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "sources_total" in data
    assert "stories_discovered_total" in data

def test_preferences_endpoint():
    response = client.get("/api/preferences")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "AI Models" in data["categories"]
