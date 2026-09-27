import datetime
import logging
import asyncio
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import Source
from app.services.sources import seed_default_sources
from app.services.fetcher import fetch_source_content
from app.services.extractor import (
    RawCandidate, extract_from_feed, extract_from_github_releases
)

logger = logging.getLogger("ai_radar.ingestion")

async def ingest_source(source: Source) -> Tuple[List[RawCandidate], Optional[str]]:
    """Fetches and parses a single source safely, returning discovered candidates."""
    logger.info(f"Fetching source: {source.name} ({source.url})")
    content, final_url, error = await fetch_source_content(source.url)

    if error or not content:
        return [], error

    try:
        if source.type == "GITHUB":
            candidates = extract_from_github_releases(
                content=content,
                source_id=source.id,
                source_priority=source.priority,
                source_name=source.name
            )
        else:
            candidates = extract_from_feed(
                content=content,
                source_id=source.id,
                source_priority=source.priority,
                source_name=source.name,
                source_type=source.type
            )
        return candidates, None
    except Exception as exc:
        err_msg = f"Extraction failed: {type(exc).__name__}: {str(exc)}"
        logger.error(f"Error parsing content for {source.name}: {err_msg}")
        return [], err_msg

async def run_source_ingestion(db: Session) -> Tuple[List[RawCandidate], int, int]:
    """
    Ingests all active sources registered in the database.
    Returns: (all_candidates, sources_scanned, failures_count)
    """
    seed_default_sources(db)
    sources = db.query(Source).filter(Source.status == "active").all()
    logger.info(f"Beginning source ingestion cycle across {len(sources)} active sources...")

    all_candidates: List[RawCandidate] = []
    sources_scanned = 0
    failures_count = 0

    for source in sources:
        sources_scanned += 1
        candidates, error = await ingest_source(source)

        if error:
            failures_count += 1
            source.last_failure_at = datetime.datetime.utcnow()
            source.last_error_message = error[:500]
        else:
            source.last_successful_scan = datetime.datetime.utcnow()
            source.last_error_message = None
            source.stories_discovered_count += len(candidates)
            all_candidates.extend(candidates)
            logger.info(f"Discovered {len(candidates)} items from '{source.name}'")

        db.add(source)

    db.commit()
    logger.info(f"Ingestion complete: {len(all_candidates)} candidates collected from {sources_scanned} sources ({failures_count} failures).")
    return all_candidates, sources_scanned, failures_count
