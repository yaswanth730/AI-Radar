import pytest
import datetime
from app.services.normalization import normalize_url, compute_content_hash
from app.services.deduplication import check_story_duplicate

def test_dedup_exact_canonical_url():
    existing = [
        {
            "id": 101,
            "canonical_url": "https://openai.com/index/gpt-5",
            "title": "Introducing GPT-5",
            "content_hash": "hash1",
            "source_priority": 1,
            "published_at": datetime.datetime(2026, 9, 20, 10, 0),
        }
    ]

    # Incoming variant with tracking query
    incoming_url = normalize_url("https://www.openai.com/index/gpt-5/?utm_source=twitter")
    res = check_story_duplicate(
        canonical_url=incoming_url,
        title="Introducing GPT-5",
        content="",
        source_priority=1,
        published_at=datetime.datetime(2026, 9, 20, 10, 30),
        existing_stories=existing
    )

    assert res.is_duplicate is True
    assert res.matched_story_id == 101
    assert "Exact canonical URL match" in res.reason

def test_dedup_exact_content_hash():
    sample_body = "Meta AI announced Llama 3.3 70B offering state-of-the-art open source reasoning at competitive inference latency."
    c_hash = compute_content_hash(sample_body)

    existing = [
        {
            "id": 102,
            "canonical_url": "https://ai.meta.com/blog/llama-3-3",
            "title": "Llama 3.3 Announced",
            "content_hash": c_hash,
            "source_priority": 1,
            "published_at": datetime.datetime(2026, 9, 18, 12, 0),
        }
    ]

    res = check_story_duplicate(
        canonical_url="https://mirror.ai.meta.com/post/123",
        title="Different Mirror Title",
        content=sample_body,
        source_priority=2,
        published_at=datetime.datetime(2026, 9, 18, 13, 0),
        existing_stories=existing
    )

    assert res.is_duplicate is True
    assert res.matched_story_id == 102
    assert "Exact content hash match" in res.reason

def test_dedup_fuzzy_title_with_priority_arbitration():
    now = datetime.datetime.utcnow()
    existing = [
        {
            "id": 103,
            "canonical_url": "https://tech-aggregator.com/news/claude-3-5-sonnet",
            "title": "Anthropic Introduces Claude 3.5 Sonnet With Computer Use",
            "content_hash": "other_hash",
            "source_priority": 4,  # Secondary aggregator
            "published_at": now - datetime.timedelta(hours=2),
        }
    ]

    # Incoming official announcement from Anthropic (Priority 1)
    res = check_story_duplicate(
        canonical_url="https://anthropic.com/news/claude-3-5-sonnet",
        title="Introducing Claude 3.5 Sonnet and Computer Use - Anthropic",
        content="Official release notes text.",
        source_priority=1,  # Primary official
        published_at=now,
        existing_stories=existing,
        title_threshold=80.0
    )

    assert res.is_duplicate is True
    assert res.matched_story_id == 103
    # Official source must signal replacing the lower-priority source
    assert res.should_replace_source is True

def test_dedup_does_not_merge_different_stories_on_same_model():
    now = datetime.datetime.utcnow()
    existing = [
        {
            "id": 104,
            "canonical_url": "https://deepmind.google/blog/gemini-2-5-launch",
            "title": "Gemini 2.5: Flash Thinking Mode Launched",
            "content_hash": "h_launch",
            "source_priority": 1,
            "published_at": now,
        }
    ]

    # Distinct article: not a launch, but a security audit or evaluation paper
    res = check_story_duplicate(
        canonical_url="https://arxiv.org/abs/2609.12345",
        title="Evaluating Adversarial Robustness and Alignment in Gemini 2.5",
        content="Research paper studying safety jailbreaks and jailbreak resistance in Gemini 2.5.",
        source_priority=3,
        published_at=now,
        existing_stories=existing
    )

    assert res.is_duplicate is False
