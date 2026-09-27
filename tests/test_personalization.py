import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Source, Story, StoryTopic, StoryCompany, StoryTechnology, UserPreference
from app.services.personalization import record_user_signal, get_user_preference_map

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)

def test_swipe_right_elevates_preference(test_db):
    src = Source(name="OpenAI News", type="RSS", url="https://example.com/rss", priority=1)
    test_db.add(src)
    test_db.commit()

    story = Story(
        canonical_url="https://example.com/story-1",
        original_url="https://example.com/story-1",
        title="OpenAI Unveils Agent System",
        normalized_title="OpenAI Unveils Agent System",
        category="AI Agents",
        source_id=src.id,
    )
    test_db.add(story)
    test_db.commit()

    test_db.add(StoryCompany(story_id=story.id, company="OpenAI"))
    test_db.add(StoryTechnology(story_id=story.id, technology="Agents"))
    test_db.commit()

    # Record swipe right
    record_user_signal(test_db, story.id, "swipe_right")

    pref_map = get_user_preference_map(test_db)
    assert pref_map.get("category:ai agents", 0) > 0
    assert pref_map.get("company:openai", 0) > 0
    assert pref_map.get("technology:agents", 0) > 0

def test_swipe_left_gentle_decay(test_db):
    src = Source(name="Test Source", type="RSS", url="https://example.com/rss2", priority=2)
    test_db.add(src)
    test_db.commit()

    story = Story(
        canonical_url="https://example.com/story-2",
        original_url="https://example.com/story-2",
        title="Introductory AI Tutorial",
        normalized_title="Introductory AI Tutorial",
        category="Developer Tools",
        source_id=src.id,
    )
    test_db.add(story)
    test_db.commit()

    # Record swipe left
    record_user_signal(test_db, story.id, "swipe_left")

    pref_map = get_user_preference_map(test_db)
    # Must decrease, but not completely starve
    val = pref_map.get("category:developer tools", 0)
    assert val < 0
    assert val >= -1.0
