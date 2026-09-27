import datetime
import logging
from typing import Optional, List
from rapidfuzz import fuzz

from app.services.normalization import (
    normalize_title, compute_content_hash
)

logger = logging.getLogger("ai_radar.deduplication")

class DeduplicationResult:
    def __init__(
        self,
        is_duplicate: bool,
        matched_story_id: Optional[int] = None,
        reason: str = "",
        should_replace_source: bool = False
    ):
        self.is_duplicate = is_duplicate
        self.matched_story_id = matched_story_id
        self.reason = reason
        self.should_replace_source = should_replace_source

def check_story_duplicate(
    canonical_url: str,
    title: str,
    content: str,
    source_priority: int,
    published_at: Optional[datetime.datetime],
    existing_stories: list,  # list of existing Story OR dicts
    title_threshold: float = 88.0
) -> DeduplicationResult:
    """
    Multi-signal deduplication engine:
    1. Exact canonical URL match -> Definite duplicate.
    2. Exact content hash match (for non-trivial text) -> Definite duplicate.
    3. RapidFuzz Token Sort title matching + 48-hour publication window check.
    4. Source priority arbitration: if incoming story is from an official source
       (priority 1) and matches an existing lower-priority secondary story (priority > 1),
       we flag should_replace_source=True.
    """
    normalized_incoming_title = normalize_title(title).lower()
    incoming_hash = compute_content_hash(content) if content and len(content) > 50 else None

    for story in existing_stories:
        # Support both SQLAlchemy Story objects and dicts in tests
        story_id = getattr(story, "id", None) or (story.get("id") if isinstance(story, dict) else None)
        story_url = getattr(story, "canonical_url", "") or (story.get("canonical_url", "") if isinstance(story, dict) else "")
        story_title = getattr(story, "title", "") or (story.get("title", "") if isinstance(story, dict) else "")
        story_hash = getattr(story, "content_hash", None) or (story.get("content_hash") if isinstance(story, dict) else None)
        story_priority = getattr(story, "source", None)
        story_source_priority = getattr(story_priority, "priority", 2) if story_priority else (story.get("source_priority", 2) if isinstance(story, dict) else 2)
        story_pub_at = getattr(story, "published_at", None) or (story.get("published_at") if isinstance(story, dict) else None)

        # Check 1: Canonical URL exact match
        if story_url == canonical_url:
            return DeduplicationResult(
                is_duplicate=True,
                matched_story_id=story_id,
                reason="Exact canonical URL match"
            )

        # Check 2: Content hash match
        if incoming_hash and story_hash and incoming_hash == story_hash:
            return DeduplicationResult(
                is_duplicate=True,
                matched_story_id=story_id,
                reason="Exact content hash match"
            )

        # Check 3: Fuzzy title match with time window validation
        normalized_existing_title = normalize_title(story_title).lower()
        sim_ratio = fuzz.token_sort_ratio(normalized_incoming_title, normalized_existing_title)

        if sim_ratio >= title_threshold:
            # Check publication time proximity (within 48 hours)
            time_compatible = True
            if published_at and story_pub_at:
                delta = abs((published_at - story_pub_at).total_seconds())
                if delta > (48 * 3600):
                    time_compatible = False

            if time_compatible:
                # Source priority arbitration: smaller priority number = higher priority
                should_replace = (source_priority < story_source_priority)
                return DeduplicationResult(
                    is_duplicate=True,
                    matched_story_id=story_id,
                    reason=f"Fuzzy title match ({sim_ratio:.1f}% similarity)",
                    should_replace_source=should_replace
                )

    return DeduplicationResult(is_duplicate=False)
