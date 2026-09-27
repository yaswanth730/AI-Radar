import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- System & Health Schemas ---

class HealthResponse(BaseModel):
    status: str = "ok"
    project: str = "AI RADAR"
    version: str = "1.0.0"
    database: str = "healthy"
    scheduler_active: bool = False
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class StatsResponse(BaseModel):
    sources_total: int
    sources_active: int
    stories_discovered_total: int
    duplicates_filtered_total: int
    important_stories_total: int
    saved_stories_total: int
    last_scan_time: Optional[datetime.datetime] = None
    last_scan_status: Optional[str] = None
    last_scan_duration_seconds: Optional[float] = None

# --- Story Schemas ---

class StoryBase(BaseModel):
    title: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    canonical_url: str
    original_url: str
    category: str
    sub_category: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    importance_score: float = 50.0
    novelty_score: float = 50.0
    technical_score: float = 50.0
    is_breaking: bool = False

class StoryResponse(StoryBase):
    id: int
    source_id: int
    source_name: str
    source_type: str
    discovered_at: datetime.datetime
    final_score: float = 50.0
    is_saved: bool = False
    topics: List[str] = []
    companies: List[str] = []
    technologies: List[str] = []

    model_config = ConfigDict(from_attributes=True)

# --- Interaction & Preference Schemas ---

class InteractionCreate(BaseModel):
    interaction_type: str = Field(..., pattern="^(swipe_right|swipe_left|save|unsave|open_source|detail_view)$")

class InteractionResponse(BaseModel):
    success: bool = True
    story_id: int
    interaction_type: str
    message: str

class PreferenceItem(BaseModel):
    entity_type: str
    entity_name: str
    score: float
    interaction_count: int

class PreferencesResponse(BaseModel):
    scan_interval_minutes: int
    ai_provider: str
    categories: Dict[str, float]
    top_topics: List[PreferenceItem]
    top_companies: List[PreferenceItem]
    top_technologies: List[PreferenceItem]

class PreferencesUpdate(BaseModel):
    scan_interval_minutes: Optional[int] = None
    category_weights: Optional[Dict[str, float]] = None

# --- Source Schemas ---

class SourceBase(BaseModel):
    name: str
    type: str = Field(..., pattern="^(RSS|ATOM|WEB|GITHUB|RESEARCH)$")
    url: str
    priority: int = Field(default=2, ge=1, le=5)

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    priority: Optional[int] = Field(None, ge=1, le=5)

class SourceResponse(SourceBase):
    id: int
    status: str
    last_successful_scan: Optional[datetime.datetime] = None
    last_failure_at: Optional[datetime.datetime] = None
    last_error_message: Optional[str] = None
    stories_discovered_count: int = 0

    model_config = ConfigDict(from_attributes=True)

# --- Scan Schemas ---

class ScanRunResponse(BaseModel):
    id: int
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    status: str
    sources_scanned: int
    failures_count: int
    stories_discovered: int
    duplicates_removed: int
    important_stories_count: int
    log_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
