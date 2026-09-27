import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal
from app.models import Source, Story

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test source if not existing
    src = db.query(Source).filter(Source.url == "https://test.ai/feed").first()
    if not src:
        src = Source(name="Test AI Source", type="RSS", url="https://test.ai/feed", priority=1)
        db.add(src)
        db.commit()
        db.refresh(src)

    # Create test story if not existing
    story = db.query(Story).filter(Story.canonical_url == "https://test.ai/story-1").first()
    if not story:
        story = Story(
            canonical_url="https://test.ai/story-1",
            original_url="https://test.ai/story-1",
            title="Testing AI Agents Architecture",
            normalized_title="testing ai agents architecture",
            headline="Testing AI Agents Architecture",
            summary="A test story about autonomous agents.",
            why_it_matters="Important test validation.",
            category="AI Agents",
            source_id=src.id,
            importance_score=85.0,
            novelty_score=70.0,
            technical_score=75.0
        )
        db.add(story)
        db.commit()
    db.close()

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"

def test_api_stats():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["sources_total"] >= 1
    assert data["stories_discovered_total"] >= 1

def test_api_sources():
    res = client.get("/api/sources")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(s["url"] == "https://test.ai/feed" for s in data)

def test_api_radar_feed():
    res = client.get("/api/radar")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if data:
        assert "headline" in data[0]
        assert "final_score" in data[0]

def test_api_save_and_unsave():
    # 1. Save story #1
    res = client.post("/api/stories/1/save")
    assert res.status_code == 200
    assert res.json()["saved"] is True

    # 2. Verify in /api/saved
    res_saved = client.get("/api/saved")
    assert res_saved.status_code == 200
    assert any(s["id"] == 1 for s in res_saved.json())

    # 3. Unsave
    res_unsave = client.delete("/api/stories/1/save")
    assert res_unsave.status_code == 200
    assert res_unsave.json()["saved"] is False

def test_api_interaction():
    res = client.post("/api/stories/1/interactions", json={"interaction_type": "swipe_right"})
    assert res.status_code == 200
    assert res.json()["success"] is True

from unittest.mock import patch, AsyncMock

def test_api_scan_trigger():
    with patch("app.main.execute_scan_cycle", new_callable=AsyncMock) as mock_scan:
        res = client.post("/api/scans/run")
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert data["status"] in ("running", "completed")
