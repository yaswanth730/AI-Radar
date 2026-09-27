import datetime
import math
from typing import Optional, Dict

from app.config import settings

def calculate_recency_score(published_at: Optional[datetime.datetime], reference_time: Optional[datetime.datetime] = None) -> float:
    """
    Computes recency score between 0.0 and 100.0 based on publication age.
    Stories < 6 hours old score near 100.
    Half-life decay is approximately 48 hours.
    """
    if not published_at:
        return 50.0

    ref = reference_time or datetime.datetime.utcnow()
    # Normalize naive/aware timestamps if needed
    if published_at.tzinfo is not None and ref.tzinfo is None:
        published_at = published_at.replace(tzinfo=None)
    elif published_at.tzinfo is None and ref.tzinfo is not None:
        ref = ref.replace(tzinfo=None)

    delta_hours = max(0.0, (ref - published_at).total_seconds() / 3600.0)

    # 48-hour half-life exponential decay: 100 * (0.5 ^ (hours / 48))
    score = 100.0 * math.pow(0.5, delta_hours / 48.0)
    return max(5.0, min(100.0, score))


def calculate_personal_relevance(
    category: str,
    topics: list,
    companies: list,
    technologies: list,
    preference_map: Dict[str, float]
) -> float:
    """
    Calculates personal relevance score (0.0 to 100.0) from learned preference weights.
    Neutral baseline is 50.0.
    Positive interactions increase score up to 100.0.
    Skipped topics gently reduce score down to a floor of 15.0.
    """
    accumulated_delta = 0.0

    # Category signal
    cat_key = f"category:{category.lower()}"
    if cat_key in preference_map:
        accumulated_delta += preference_map[cat_key] * 1.5

    # Company signals
    for c in companies:
        c_key = f"company:{c.lower()}"
        if c_key in preference_map:
            accumulated_delta += preference_map[c_key] * 1.2

    # Technology signals
    for t in technologies:
        t_key = f"technology:{t.lower()}"
        if t_key in preference_map:
            accumulated_delta += preference_map[t_key] * 1.2

    # Topic signals
    for top in topics:
        top_key = f"topic:{top.lower()}"
        if top_key in preference_map:
            accumulated_delta += preference_map[top_key] * 1.0

    # Scale delta onto baseline of 50.0
    # Clamped between 15.0 and 100.0
    score = 50.0 + accumulated_delta
    return max(15.0, min(100.0, score))


def compute_final_rank_score(
    importance: float,
    personal_relevance: float,
    recency: float,
    novelty: float,
    custom_weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Computes transparent multi-signal composite rank score:
    final_score = 0.40 * importance + 0.30 * personal_relevance + 0.20 * recency + 0.10 * novelty
    """
    w_imp = custom_weights.get("importance", settings.WEIGHT_IMPORTANCE) if custom_weights else settings.WEIGHT_IMPORTANCE
    w_pers = custom_weights.get("personal", settings.WEIGHT_PERSONAL) if custom_weights else settings.WEIGHT_PERSONAL
    w_rec = custom_weights.get("recency", settings.WEIGHT_RECENCY) if custom_weights else settings.WEIGHT_RECENCY
    w_nov = custom_weights.get("novelty", settings.WEIGHT_NOVELTY) if custom_weights else settings.WEIGHT_NOVELTY

    # Normalize weights so they sum to 1.0
    total_w = w_imp + w_pers + w_rec + w_nov
    if total_w > 0:
        w_imp /= total_w
        w_pers /= total_w
        w_rec /= total_w
        w_nov /= total_w

    raw_score = (
        (importance * w_imp) +
        (personal_relevance * w_pers) +
        (recency * w_rec) +
        (novelty * w_nov)
    )

    return round(max(0.0, min(100.0, raw_score)), 1)
