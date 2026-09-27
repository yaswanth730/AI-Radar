import datetime
import logging
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models import Story, UserInteraction, UserPreference

logger = logging.getLogger("ai_radar.personalization")

# Interaction signal weights
SIGNAL_WEIGHTS = {
    "swipe_right": 3.0,     # Interested in topic / company
    "swipe_left": -0.8,     # Gentle decay (never starve topic after one skip)
    "save": 6.0,            # Strong positive signal
    "unsave": -3.0,
    "open_source": 2.5,     # Positive interest signal
    "detail_view": 1.0,     # Mild engagement
}

def get_user_preference_map(db: Session) -> Dict[str, float]:
    """
    Returns map of entity keys to learned preference score:
    {"category:ai agents": 12.0, "company:anthropic": 8.5, ...}
    """
    preferences = db.query(UserPreference).all()
    res = {}
    for p in preferences:
        key = f"{p.entity_type.lower()}:{p.entity_name.lower()}"
        res[key] = p.score
    return res

def update_preference_entity(db: Session, entity_type: str, entity_name: str, delta: float):
    """Updates or inserts a preference weight with safety clamping between -15.0 and +60.0."""
    normalized_name = entity_name.strip()
    if not normalized_name:
        return

    pref = db.query(UserPreference).filter(
        UserPreference.entity_type == entity_type,
        UserPreference.entity_name == normalized_name
    ).first()

    now = datetime.datetime.utcnow()
    if not pref:
        new_score = max(-15.0, min(60.0, delta))
        pref = UserPreference(
            entity_type=entity_type,
            entity_name=normalized_name,
            score=new_score,
            interaction_count=1,
            last_interacted_at=now
        )
        db.add(pref)
    else:
        # Incremental update with decay on extreme values
        updated_score = pref.score + delta
        pref.score = max(-15.0, min(60.0, updated_score))
        pref.interaction_count += 1
        pref.last_interacted_at = now

def record_user_signal(db: Session, story_id: int, interaction_type: str):
    """
    Records an interaction and updates multi-entity preference signals.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        return

    delta = SIGNAL_WEIGHTS.get(interaction_type, 1.0)

    # 1. Record the explicit interaction audit entry
    interaction = UserInteraction(
        story_id=story_id,
        interaction_type=interaction_type,
        weight=delta,
        created_at=datetime.datetime.utcnow()
    )
    db.add(interaction)

    # 2. Update category preference
    if story.category:
        update_preference_entity(db, "category", story.category, delta * 0.8)

    # 3. Update companies preferences
    if story.companies:
        for c in story.companies:
            update_preference_entity(db, "company", c.company, delta * 1.0)

    # 4. Update technologies preferences
    if story.technologies:
        for t in story.technologies:
            update_preference_entity(db, "technology", t.technology, delta * 1.0)

    # 5. Update topics preferences
    if story.topics:
        for top in story.topics:
            update_preference_entity(db, "topic", top.topic, delta * 0.7)

    db.commit()
    logger.info(f"Recorded '{interaction_type}' on story #{story_id} (delta: {delta})")
