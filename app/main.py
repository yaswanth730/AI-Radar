import datetime
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.config import settings
from app.database import engine, Base, get_db, SessionLocal
from app.models import Source, Story, SavedStory, UserInteraction, ScanRun, UserPreference
from app.schemas import (
    HealthResponse, StatsResponse, StoryResponse, InteractionCreate,
    InteractionResponse, SourceResponse, SourceCreate, PreferencesResponse,
    PreferencesUpdate, ScanRunResponse
)
from app.services.sources import seed_default_sources
from app.services.scheduler import start_scheduler, stop_scheduler, scheduler
from app.services.personalization import record_user_signal, get_user_preference_map
from app.services.ranking import (
    calculate_recency_score, calculate_personal_relevance, compute_final_rank_score
)
from app.services.pipeline import execute_scan_cycle

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_radar.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing AI RADAR database models...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_default_sources(db)
    finally:
        db.close()

    logger.info("Starting background scan scheduler...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Stopping background scheduler and shutting down...")
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous Personal AI Intelligence Platform API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Formatting & Ranking Helpers ---

def format_story_response(
    story: Story,
    is_saved: bool = False,
    preference_map: Optional[dict] = None
) -> StoryResponse:
    topics = [t.topic for t in story.topics] if story.topics else []
    companies = [c.company for c in story.companies] if story.companies else []
    technologies = [t.technology for t in story.technologies] if story.technologies else []

    # Calculate real ranking signals
    recency = calculate_recency_score(story.published_at or story.discovered_at)
    personal = calculate_personal_relevance(
        category=story.category,
        topics=topics,
        companies=companies,
        technologies=technologies,
        preference_map=preference_map or {}
    )

    final_score = compute_final_rank_score(
        importance=story.importance_score,
        personal_relevance=personal,
        recency=recency,
        novelty=story.novelty_score
    )

    return StoryResponse(
        id=story.id,
        title=story.title,
        headline=story.headline or story.title,
        summary=story.summary or "",
        why_it_matters=story.why_it_matters or "",
        canonical_url=story.canonical_url,
        original_url=story.original_url,
        category=story.category,
        sub_category=story.sub_category,
        published_at=story.published_at,
        discovered_at=story.discovered_at,
        importance_score=story.importance_score,
        novelty_score=story.novelty_score,
        technical_score=story.technical_score,
        is_breaking=story.is_breaking,
        source_id=story.source_id,
        source_name=story.source.name if story.source else "Primary Source",
        source_type=story.source.type if story.source else "RSS",
        final_score=final_score,
        is_saved=is_saved,
        topics=topics,
        companies=companies,
        technologies=technologies
    )

# --- System & Telemetry ---

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health(db: Session = Depends(get_db)):
    try:
        db.execute(func.now())
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health DB ping error: {e}")
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="ok",
        project=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        database=db_status,
        scheduler_active=scheduler.running if hasattr(scheduler, "running") else False,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

@app.get("/api/stats", response_model=StatsResponse, tags=["System"])
def get_stats(db: Session = Depends(get_db)):
    sources_total = db.query(Source).count()
    sources_active = db.query(Source).filter(Source.status == "active").count()
    stories_discovered = db.query(Story).count()
    saved_count = db.query(SavedStory).count()
    important_count = db.query(Story).filter(Story.importance_score >= 70.0).count()
    
    last_scan = db.query(ScanRun).order_by(desc(ScanRun.started_at)).first()
    dup_sum = db.query(func.sum(ScanRun.duplicates_removed)).scalar() or 0

    duration = None
    if last_scan and last_scan.completed_at and last_scan.started_at:
        duration = (last_scan.completed_at - last_scan.started_at).total_seconds()

    return StatsResponse(
        sources_total=sources_total,
        sources_active=sources_active,
        stories_discovered_total=stories_discovered,
        duplicates_filtered_total=int(dup_sum),
        important_stories_total=important_count,
        saved_stories_total=saved_count,
        last_scan_time=last_scan.started_at if last_scan else None,
        last_scan_status=last_scan.status if last_scan else "No scans yet",
        last_scan_duration_seconds=duration
    )

# --- Feeds & Discovery ---

@app.get("/api/radar", response_model=List[StoryResponse], tags=["Feeds"])
def get_radar_stories(limit: int = 15, db: Session = Depends(get_db)):
    """Card stack discovery stories for the primary RADAR screen."""
    # Exclude stories user has already swiped on in recent days
    swiped_ids = db.query(UserInteraction.story_id).filter(
        UserInteraction.interaction_type.in_(["swipe_right", "swipe_left"])
    ).subquery()

    unswiped = db.query(Story).filter(
        ~Story.id.in_(swiped_ids),
        Story.status != "downranked"
    ).order_by(desc(Story.discovered_at)).limit(limit * 2).all()

    # If unswiped list is depleted, fallback to all stories
    if len(unswiped) < 5:
        unswiped = db.query(Story).filter(Story.status != "downranked").order_by(desc(Story.discovered_at)).limit(limit).all()

    pref_map = get_user_preference_map(db)
    saved_ids = {s.story_id for s in db.query(SavedStory.story_id).all()}

    formatted = [format_story_response(s, is_saved=(s.id in saved_ids), preference_map=pref_map) for s in unswiped]
    formatted.sort(key=lambda x: x.final_score, reverse=True)
    return formatted[:limit]

@app.get("/api/for-you", response_model=List[StoryResponse], tags=["Feeds"])
def get_for_you_stories(limit: int = 25, db: Session = Depends(get_db)):
    """Personalized feed ranked by learned topic/company affinities."""
    stories = db.query(Story).filter(Story.status != "downranked").order_by(desc(Story.discovered_at)).limit(100).all()
    pref_map = get_user_preference_map(db)
    saved_ids = {s.story_id for s in db.query(SavedStory.story_id).all()}

    formatted = [format_story_response(s, is_saved=(s.id in saved_ids), preference_map=pref_map) for s in stories]
    formatted.sort(key=lambda x: x.final_score, reverse=True)
    return formatted[:limit]

@app.get("/api/trending", response_model=List[StoryResponse], tags=["Feeds"])
def get_trending_stories(limit: int = 25, db: Session = Depends(get_db)):
    """Top trending stories ranked by importance and recency."""
    stories = db.query(Story).filter(Story.status != "downranked").order_by(
        desc(Story.importance_score), desc(Story.discovered_at)
    ).limit(limit).all()
    saved_ids = {s.story_id for s in db.query(SavedStory.story_id).all()}
    return [format_story_response(s, is_saved=(s.id in saved_ids)) for s in stories]

@app.get("/api/saved", response_model=List[StoryResponse], tags=["Feeds"])
def get_saved_stories(db: Session = Depends(get_db)):
    """Bookmarked stories archive."""
    saved_entries = db.query(SavedStory).order_by(desc(SavedStory.created_at)).all()
    pref_map = get_user_preference_map(db)
    result = []
    for entry in saved_entries:
        if entry.story:
            result.append(format_story_response(entry.story, is_saved=True, preference_map=pref_map))
    return result

@app.get("/api/stories/{story_id}", response_model=StoryResponse, tags=["Stories"])
def get_story_detail(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    is_saved = db.query(SavedStory).filter(SavedStory.story_id == story_id).first() is not None
    pref_map = get_user_preference_map(db)
    return format_story_response(story, is_saved=is_saved, preference_map=pref_map)

# --- Interactions & Bookmarks ---

@app.post("/api/stories/{story_id}/interactions", response_model=InteractionResponse, tags=["Interactions"])
def record_interaction_endpoint(story_id: int, payload: InteractionCreate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    record_user_signal(db, story_id, payload.interaction_type)

    return InteractionResponse(
        success=True,
        story_id=story_id,
        interaction_type=payload.interaction_type,
        message="Interaction recorded and preference weights updated"
    )

@app.post("/api/stories/{story_id}/save", tags=["Bookmarks"])
def save_story_endpoint(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    existing = db.query(SavedStory).filter(SavedStory.story_id == story_id).first()
    if not existing:
        saved = SavedStory(story_id=story_id)
        db.add(saved)
        record_user_signal(db, story_id, "save")
        db.commit()
    return {"success": True, "story_id": story_id, "saved": True}

@app.delete("/api/stories/{story_id}/save", tags=["Bookmarks"])
def unsave_story_endpoint(story_id: int, db: Session = Depends(get_db)):
    existing = db.query(SavedStory).filter(SavedStory.story_id == story_id).first()
    if existing:
        db.delete(existing)
        record_user_signal(db, story_id, "unsave")
        db.commit()
    return {"success": True, "story_id": story_id, "saved": False}

# --- Sources & Scans ---

@app.get("/api/sources", response_model=List[SourceResponse], tags=["Sources"])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.priority, Source.name).all()

@app.post("/api/sources", response_model=SourceResponse, tags=["Sources"])
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.url == payload.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source URL already exists")
    
    source = Source(
        name=payload.name,
        type=payload.type,
        url=payload.url,
        priority=payload.priority,
        status="active"
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source

@app.post("/api/scans/run", response_model=ScanRunResponse, tags=["Scans"])
def trigger_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers an immediate autonomous radar scan in the background."""
    scan = ScanRun(
        started_at=datetime.datetime.utcnow(),
        status="running",
        sources_scanned=0,
        failures_count=0,
        stories_discovered=0,
        duplicates_removed=0,
        important_stories_count=0,
        log_summary="Scan initiated via API trigger."
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    async def _run_bg(scan_id: int):
        s_db = SessionLocal()
        try:
            await execute_scan_cycle(s_db, existing_scan_id=scan_id)
        finally:
            s_db.close()

    background_tasks.add_task(_run_bg, scan.id)
    return scan

@app.get("/api/scans/latest", response_model=Optional[ScanRunResponse], tags=["Scans"])
def get_latest_scan(db: Session = Depends(get_db)):
    return db.query(ScanRun).order_by(desc(ScanRun.started_at)).first()

# --- Preferences ---

@app.get("/api/preferences", response_model=PreferencesResponse, tags=["Preferences"])
def get_preferences(db: Session = Depends(get_db)):
    prefs = db.query(UserPreference).order_by(desc(UserPreference.score)).all()
    
    topics = [
        {"entity_type": p.entity_type, "entity_name": p.entity_name, "score": p.score, "interaction_count": p.interaction_count}
        for p in prefs if p.entity_type == "topic"
    ][:10]
    
    companies = [
        {"entity_type": p.entity_type, "entity_name": p.entity_name, "score": p.score, "interaction_count": p.interaction_count}
        for p in prefs if p.entity_type == "company"
    ][:10]

    technologies = [
        {"entity_type": p.entity_type, "entity_name": p.entity_name, "score": p.score, "interaction_count": p.interaction_count}
        for p in prefs if p.entity_type == "technology"
    ][:10]

    return PreferencesResponse(
        scan_interval_minutes=settings.SCAN_INTERVAL_MINUTES,
        ai_provider=settings.AI_PROVIDER,
        categories={
            "AI Models": 1.0,
            "AI Agents": 1.0,
            "APIs": 1.0,
            "Research": 1.0,
            "Open Source": 1.0,
            "Developer Tools": 1.0,
            "Robotics": 1.0,
            "Infrastructure": 1.0,
            "Security": 1.0,
            "AI Regulation": 1.0,
        },
        top_topics=topics,
        top_companies=companies,
        top_technologies=technologies
    )
