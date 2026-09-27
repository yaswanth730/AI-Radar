import logging
import asyncio
from typing import Optional, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("ai_radar.fetcher")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (AI-Radar/1.0; +https://airadar.local)"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/atom+xml, text/xml, application/xml, text/html;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError)),
    reraise=True
)
async def _fetch_with_retry(client: httpx.AsyncClient, url: str) -> httpx.Response:
    return await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)

async def fetch_source_content(url: str) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Safely fetches content from a remote source.
    Returns: (content_bytes, final_url, error_message)
    """
    try:
        async with httpx.AsyncClient(verify=False) as client:
            resp = await _fetch_with_retry(client, url)
            if resp.status_code >= 400:
                err = f"HTTP {resp.status_code}: {resp.reason_phrase}"
                logger.warning(f"Fetch failure for {url}: {err}")
                return None, None, err
            return resp.content, str(resp.url), None
    except Exception as exc:
        err = f"{type(exc).__name__}: {str(exc)}"
        logger.warning(f"Error fetching {url}: {err}")
        return None, None, err
