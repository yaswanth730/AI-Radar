import logging
from sqlalchemy.orm import Session
from app.models import Source

logger = logging.getLogger("ai_radar.sources")

DEFAULT_SOURCES = [
    {
        "name": "OpenAI News & Research",
        "type": "RSS",
        "url": "https://openai.com/news/rss.xml",
        "priority": 1,
    },
    {
        "name": "Anthropic News & Announcements",
        "type": "RSS",
        "url": "https://www.anthropic.com/news/feed",
        "priority": 1,
    },
    {
        "name": "Google DeepMind Blog",
        "type": "RSS",
        "url": "https://deepmind.google/blog/rss.xml",
        "priority": 1,
    },
    {
        "name": "Meta AI Research",
        "type": "RSS",
        "url": "https://ai.meta.com/blog/rss.xml",
        "priority": 1,
    },
    {
        "name": "Hugging Face Blog",
        "type": "RSS",
        "url": "https://huggingface.co/blog/feed.xml",
        "priority": 1,
    },
    {
        "name": "arXiv: Artificial Intelligence (cs.AI)",
        "type": "RESEARCH",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "priority": 3,
    },
    {
        "name": "vLLM Releases",
        "type": "GITHUB",
        "url": "https://github.com/vllm-project/vllm/releases.atom",
        "priority": 2,
    },
    {
        "name": "Ollama Releases",
        "type": "GITHUB",
        "url": "https://github.com/ollama/ollama/releases.atom",
        "priority": 2,
    },
    {
        "name": "Transformers Releases",
        "type": "GITHUB",
        "url": "https://github.com/huggingface/transformers/releases.atom",
        "priority": 2,
    }
]

def seed_default_sources(db: Session):
    """Seed initial first-party reputable AI sources if not present in the database."""
    seeded_count = 0
    for src in DEFAULT_SOURCES:
        existing = db.query(Source).filter(Source.url == src["url"]).first()
        if not existing:
            new_source = Source(
                name=src["name"],
                type=src["type"],
                url=src["url"],
                priority=src["priority"],
                status="active"
            )
            db.add(new_source)
            seeded_count += 1
    if seeded_count > 0:
        db.commit()
        logger.info(f"Seeded {seeded_count} default AI primary sources into database.")
