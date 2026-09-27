import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Source
from app.services.sources import seed_default_sources, DEFAULT_SOURCES
from app.services.extractor import (
    extract_from_feed, extract_from_github_releases, clean_html_text
)

# Test in-memory database
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

def test_seed_default_sources(test_db):
    seed_default_sources(test_db)
    sources = test_db.query(Source).all()
    assert len(sources) == len(DEFAULT_SOURCES)
    
    # Verify OpenAI News & Research seeded
    openai_src = test_db.query(Source).filter(Source.name == "OpenAI News & Research").first()
    assert openai_src is not None
    assert openai_src.priority == 1
    assert openai_src.type == "RSS"
    assert openai_src.status == "active"

    # Re-seeding must be idempotent
    seed_default_sources(test_db)
    sources_after = test_db.query(Source).all()
    assert len(sources_after) == len(DEFAULT_SOURCES)

def test_clean_html_text():
    raw = "<p>OpenAI announced <strong>GPT-5</strong> with <a href='https://example.com'>agentic</a> capabilities.</p><script>alert('bad')</script>"
    clean = clean_html_text(raw)
    assert clean == "OpenAI announced GPT-5 with agentic capabilities."
    assert "script" not in clean
    assert "alert" not in clean

def test_extract_from_feed():
    sample_rss = b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>AI Lab Announcements</title>
        <link>https://example.com</link>
        <item>
          <title>Introducing Frontier Reasoning Engine</title>
          <link>https://example.com/news/frontier-reasoning?utm_source=twitter</link>
          <description><![CDATA[<p>A new frontier model optimized for coding, mathematics, and autonomous multi-agent tool use.</p>]]></description>
          <pubDate>Mon, 22 Sep 2026 14:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>"""

    candidates = extract_from_feed(
        content=sample_rss,
        source_id=1,
        source_priority=1,
        source_name="AI Lab",
        source_type="RSS"
    )

    assert len(candidates) == 1
    c = candidates[0]
    assert c.title == "Introducing Frontier Reasoning Engine"
    assert "https://example.com/news/frontier-reasoning" in c.url
    assert "A new frontier model optimized for coding" in c.summary
    assert c.source_priority == 1
    assert c.published_at is not None
    assert c.published_at.year == 2026

def test_extract_from_github_releases():
    sample_atom = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>Release notes from vLLM</title>
      <entry>
        <id>tag:github.com,2008:Repository/12345/v0.6.2</id>
        <updated>2026-09-20T10:15:30Z</updated>
        <link rel="alternate" type="text/html" href="https://github.com/vllm-project/vllm/releases/tag/v0.6.2"/>
        <title>v0.6.2</title>
        <content type="html">&lt;p&gt;High-throughput multi-LoRA inference and FP8 quantized kernel improvements.&lt;/p&gt;</content>
      </entry>
    </feed>"""

    candidates = extract_from_github_releases(
        content=sample_atom,
        source_id=2,
        source_priority=2,
        source_name="vLLM Releases"
    )

    assert len(candidates) == 1
    c = candidates[0]
    assert "vLLM Releases: v0.6.2" in c.title
    assert "v0.6.2" in c.url
    assert "High-throughput multi-LoRA inference" in c.summary
    assert c.source_type == "GITHUB"
