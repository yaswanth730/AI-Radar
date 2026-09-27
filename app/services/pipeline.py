import datetime
import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import (
    Source, Story, StoryTopic, StoryCompany, StoryTechnology, ScanRun
)
from app.services.sources import seed_default_sources
from app.services.ingestion import run_source_ingestion
from app.services.normalization import normalize_url, normalize_title, compute_content_hash
from app.services.deduplication import check_story_duplicate
from app.services.ai_classifier import get_ai_classifier

logger = logging.getLogger("ai_radar.pipeline")

async def execute_scan_cycle(db: Session, existing_scan_id: Optional[int] = None) -> ScanRun:
    """
    Executes a complete autonomous scan cycle across all active sources:
    FETCH -> EXTRACT -> NORMALIZE -> DEDUPLICATE -> CLASSIFY -> SCORE -> SUMMARIZE -> STORE
    """
    if existing_scan_id:
        scan = db.query(ScanRun).filter(ScanRun.id == existing_scan_id).first()
    else:
        scan = None

    if not scan:
        scan = ScanRun(
            started_at=datetime.datetime.utcnow(),
            status="running",
            sources_scanned=0,
            failures_count=0,
            stories_discovered=0,
            duplicates_removed=0,
            important_stories_count=0
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

    logger.info(f"Scan run #{scan.id} started.")

    try:
        # Step 1 & 2: FETCH & EXTRACT
        raw_candidates, sources_scanned, failures_count = await run_source_ingestion(db)
        scan.sources_scanned = sources_scanned
        scan.failures_count = failures_count
        db.commit()

        # Step 3 & 4: NORMALIZE & DEDUPLICATE
        # Fetch existing recent stories for fast deduplication check
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=14)
        existing_stories = db.query(Story).filter(Story.discovered_at >= cutoff).all()

        classifier = get_ai_classifier()
        new_stories_count = 0
        duplicates_count = 0
        important_count = 0
        # Sort candidates: highest priority first (1 < 2 < 3), then by publication date desc
        sorted_candidates = sorted(
            raw_candidates,
            key=lambda c: (c.source_priority, -(c.published_at.timestamp() if c.published_at else 0))
        )
        # Process up to 35 high-signal candidates per cycle for optimal latency
        batch_candidates = sorted_candidates[:35]

        for candidate in batch_candidates:
            canonical_url = normalize_url(candidate.url)
            clean_title = normalize_title(candidate.title)

            # Check duplication
            dedup_res = check_story_duplicate(
                canonical_url=canonical_url,
                title=clean_title,
                content=candidate.content,
                source_priority=candidate.source_priority,
                published_at=candidate.published_at,
                existing_stories=existing_stories
            )

            if dedup_res.is_duplicate:
                duplicates_count += 1
                continue

            # Step 5, 6, 7: CLASSIFY, SCORE, SUMMARIZE
            classification = await classifier.classify_and_summarize(
                title=clean_title,
                text=candidate.content or candidate.summary,
                source_name=candidate.source_name
            )

            c_hash = compute_content_hash(candidate.content)

            # Step 8: STORE
            new_story = Story(
                canonical_url=canonical_url,
                original_url=candidate.url,
                title=clean_title,
                normalized_title=clean_title.lower(),
                headline=classification.headline or clean_title,
                summary=classification.summary,
                why_it_matters=classification.why_it_matters,
                raw_content=candidate.content[:2000],
                content_hash=c_hash,
                source_id=candidate.source_id,
                published_at=candidate.published_at or datetime.datetime.utcnow(),
                discovered_at=datetime.datetime.utcnow(),
                category=classification.category,
                sub_category=classification.sub_category,
                importance_score=classification.importance_score,
                novelty_score=classification.novelty_score,
                technical_score=classification.technical_score,
                is_ai_related=classification.is_ai_related,
                is_breaking=classification.is_breaking,
                status="downranked" if classification.is_downranked else "published"
            )
            db.add(new_story)
            db.flush()  # assign ID

            # Add tags
            for comp in classification.companies:
                db.add(StoryCompany(story_id=new_story.id, company=comp))
            for tech in classification.technologies:
                db.add(StoryTechnology(story_id=new_story.id, technology=tech))
            for top in classification.topics:
                db.add(StoryTopic(story_id=new_story.id, topic=top))

            new_stories_count += 1
            if classification.importance_score >= 70.0:
                important_count += 1

            # Keep in-memory cache updated so successive items in the same batch don't duplicate
            existing_stories.append(new_story)

        db.commit()

        scan.status = "completed"
        scan.completed_at = datetime.datetime.utcnow()
        scan.stories_discovered = new_stories_count
        scan.duplicates_removed = duplicates_count
        scan.important_stories_count = important_count
        scan.log_summary = f"Indexed {new_stories_count} new AI stories, filtered {duplicates_count} duplicates."
        db.commit()

        logger.info(f"Scan run #{scan.id} completed: {new_stories_count} new, {duplicates_count} duplicates.")
        return scan

    except Exception as exc:
        db.rollback()
        scan.status = "failed"
        scan.completed_at = datetime.datetime.utcnow()
        scan.log_summary = f"Scan failed: {type(exc).__name__}: {str(exc)}"
        db.commit()
        logger.error(f"Scan run #{scan.id} failed: {exc}", exc_info=True)
        return scan
