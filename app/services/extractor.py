import datetime
import logging
from typing import List, Optional
from dataclasses import dataclass
import feedparser
from bs4 import BeautifulSoup
import trafilatura

logger = logging.getLogger("ai_radar.extractor")

@dataclass
class RawCandidate:
    title: str
    url: str
    summary: str
    content: str
    published_at: Optional[datetime.datetime]
    source_id: int
    source_priority: int
    source_name: str
    source_type: str

def clean_html_text(raw_html: str) -> str:
    """Strips HTML markup and decodes entities cleanly."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

def parse_time_struct(time_struct) -> Optional[datetime.datetime]:
    if not time_struct:
        return None
    try:
        return datetime.datetime(*time_struct[:6])
    except Exception:
        return None

def extract_from_feed(content: bytes, source_id: int, source_priority: int, source_name: str, source_type: str) -> List[RawCandidate]:
    """
    Parses RSS or Atom feeds using feedparser.
    Extracts entries with title, clean link, summary and published timestamp.
    """
    feed = feedparser.parse(content)
    candidates: List[RawCandidate] = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        # Extract summary / description
        summary_raw = entry.get("summary") or entry.get("description") or ""
        summary_clean = clean_html_text(summary_raw)

        # Extract published or updated time
        time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        published_at = parse_time_struct(time_struct)

        # Extract full content if available
        content_text = ""
        if "content" in entry and entry.content:
            content_text = clean_html_text(entry.content[0].value)
        elif summary_clean:
            content_text = summary_clean

        candidates.append(
            RawCandidate(
                title=title,
                url=link,
                summary=summary_clean[:600],
                content=content_text[:3000],
                published_at=published_at,
                source_id=source_id,
                source_priority=source_priority,
                source_name=source_name,
                source_type=source_type
            )
        )

    return candidates

def extract_from_github_releases(content: bytes, source_id: int, source_priority: int, source_name: str) -> List[RawCandidate]:
    """
    Specialized parser for GitHub Release Atom feeds.
    Formats release tag and structured notes.
    """
    feed = feedparser.parse(content)
    candidates: List[RawCandidate] = []

    for entry in feed.entries:
        tag_title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not tag_title or not link:
            continue

        summary_raw = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
        summary_clean = clean_html_text(summary_raw)

        # Prepend repo context if title is just a version number like "v0.6.0"
        display_title = tag_title
        if not any(token in tag_title.lower() for token in ["release", "vllm", "ollama", "transformers"]):
            display_title = f"{source_name}: {tag_title}"

        time_struct = entry.get("updated_parsed") or entry.get("published_parsed")
        published_at = parse_time_struct(time_struct)

        candidates.append(
            RawCandidate(
                title=display_title,
                url=link,
                summary=summary_clean[:600],
                content=summary_clean[:3000],
                published_at=published_at,
                source_id=source_id,
                source_priority=source_priority,
                source_name=source_name,
                source_type="GITHUB"
            )
        )

    return candidates

def extract_web_article_body(html_content: str, url: str) -> str:
    """
    Extracts clean primary article body text using trafilatura with BeautifulSoup fallback.
    """
    try:
        extracted = trafilatura.extract(html_content, include_comments=False, include_tables=False)
        if extracted and len(extracted.strip()) > 100:
            return extracted.strip()
    except Exception as e:
        logger.debug(f"trafilatura extraction error for {url}: {e}")

    # Fallback to BeautifulSoup article container
    return clean_html_text(html_content)[:3000]
