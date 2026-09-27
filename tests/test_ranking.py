import pytest
import datetime
from app.services.ranking import (
    calculate_recency_score,
    calculate_personal_relevance,
    compute_final_rank_score
)

def test_compute_final_rank_score_default_weights():
    # Formula: 0.40 * imp + 0.30 * pers + 0.20 * rec + 0.10 * nov
    # 0.40*80 + 0.30*50 + 0.20*100 + 0.10*60 = 32 + 15 + 20 + 6 = 73.0
    score = compute_final_rank_score(
        importance=80.0,
        personal_relevance=50.0,
        recency=100.0,
        novelty=60.0
    )
    assert score == 73.0

def test_compute_final_rank_score_custom_weights():
    # Custom weights: 50% importance, 50% recency, others 0%
    custom = {"importance": 0.5, "personal": 0.0, "recency": 0.5, "novelty": 0.0}
    score = compute_final_rank_score(
        importance=90.0,
        personal_relevance=20.0,
        recency=70.0,
        novelty=30.0,
        custom_weights=custom
    )
    assert score == 80.0

def test_calculate_recency_decay():
    now = datetime.datetime.utcnow()
    # Story just published
    rec_fresh = calculate_recency_score(now, reference_time=now)
    assert rec_fresh >= 99.0

    # Story published 48 hours ago (approx half-life = 50.0)
    past_48h = now - datetime.timedelta(hours=48)
    rec_48h = calculate_recency_score(past_48h, reference_time=now)
    assert 48.0 <= rec_48h <= 52.0

    # Story published 14 days ago
    past_14d = now - datetime.timedelta(days=14)
    rec_old = calculate_recency_score(past_14d, reference_time=now)
    assert rec_old <= 15.0

def test_calculate_personal_relevance_affinity():
    # Neutral baseline with empty preferences
    baseline = calculate_personal_relevance("AI Models", [], [], [], {})
    assert baseline == 50.0

    # Preference map showing interest in AI Agents and Anthropic
    prefs = {
        "category:ai agents": 10.0,
        "company:anthropic": 8.0,
    }

    relevant_score = calculate_personal_relevance(
        category="AI Agents",
        topics=["Autonomous Workflows"],
        companies=["Anthropic"],
        technologies=[],
        preference_map=prefs
    )
    assert relevant_score > baseline
    assert relevant_score > 70.0
