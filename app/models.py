import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # RSS, ATOM, WEB, GITHUB, RESEARCH
    url = Column(String(1024), nullable=False, unique=True, index=True)
    status = Column(String(50), default="active", nullable=False)  # active, inactive, failing
    priority = Column(Integer, default=2, nullable=False)  # 1 = highest (first-party official), 2 = github, 3 = research, 4 = secondary
    last_successful_scan = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    stories_discovered_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    stories = relationship("Story", back_populates="source", cascade="all, delete-orphan")


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    canonical_url = Column(String(1024), nullable=False, unique=True, index=True)
    original_url = Column(String(1024), nullable=False)
    title = Column(String(512), nullable=False)
    normalized_title = Column(String(512), nullable=False, index=True)
    headline = Column(String(255), nullable=True)  # ~15 words structured headline
    summary = Column(Text, nullable=True)  # 1-3 concise sentences
    why_it_matters = Column(Text, nullable=True)  # Exactly 1 strong sentence
    raw_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    category = Column(String(100), default="AI Models", nullable=False, index=True)
    sub_category = Column(String(100), nullable=True)
    
    # AI Scoring (0.0 to 100.0)
    importance_score = Column(Float, default=50.0, nullable=False)
    novelty_score = Column(Float, default=50.0, nullable=False)
    technical_score = Column(Float, default=50.0, nullable=False)
    
    # Flags & Status
    is_ai_related = Column(Boolean, default=True, nullable=False)
    is_breaking = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="published", nullable=False)  # published, archived, downranked
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    source = relationship("Source", back_populates="stories")
    topics = relationship("StoryTopic", back_populates="story", cascade="all, delete-orphan")
    companies = relationship("StoryCompany", back_populates="story", cascade="all, delete-orphan")
    technologies = relationship("StoryTechnology", back_populates="story", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="story", cascade="all, delete-orphan")
    saved_entries = relationship("SavedStory", back_populates="story", cascade="all, delete-orphan")


class StoryTopic(Base):
    __tablename__ = "story_topics"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)

    story = relationship("Story", back_populates="topics")


class StoryCompany(Base):
    __tablename__ = "story_companies"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)

    story = relationship("Story", back_populates="companies")


class StoryTechnology(Base):
    __tablename__ = "story_technologies"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    technology = Column(String(100), nullable=False, index=True)

    story = relationship("Story", back_populates="technologies")


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    # Interaction types: swipe_right (interested), swipe_left (skip), save, unsave, open_source, detail_view
    interaction_type = Column(String(50), nullable=False, index=True)
    weight = Column(Float, default=1.0, nullable=False)  # positive or negative signal strength
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    story = relationship("Story", back_populates="interactions")


class UserPreference(Base):
    """
    Learned preferences across topics, categories, companies, and technologies.
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # category, topic, company, technology
    entity_name = Column(String(150), nullable=False, index=True)
    score = Column(Float, default=0.0, nullable=False)  # Learned affinity (-10.0 to +50.0)
    interaction_count = Column(Integer, default=0, nullable=False)
    last_interacted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class SavedStory(Base):
    __tablename__ = "saved_stories"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    story = relationship("Story", back_populates="saved_entries")


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running", nullable=False)  # running, completed, failed
    sources_scanned = Column(Integer, default=0, nullable=False)
    failures_count = Column(Integer, default=0, nullable=False)
    stories_discovered = Column(Integer, default=0, nullable=False)
    duplicates_removed = Column(Integer, default=0, nullable=False)
    important_stories_count = Column(Integer, default=0, nullable=False)
    log_summary = Column(Text, nullable=True)
