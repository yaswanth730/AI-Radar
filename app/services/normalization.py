import re
import hashlib
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_term_id", "fbclid", "gclid", "gbraid", "wbraid",
    "ref", "source", "feature", "trk", "msclkid", "mc_eid", "soc_src", "soc_trk"
}

def normalize_url(raw_url: str) -> str:
    """
    Canonicalizes a URL by:
    1. Normalizing scheme to lowercase (defaulting to https).
    2. Lowercasing hostname and stripping default ports (:80, :443).
    3. Stripping 'www.' prefix.
    4. Removing tracking query parameters (utm_*, fbclid, gclid, etc.).
    5. Sorting remaining query parameters deterministically.
    6. Stripping anchor fragments.
    7. Standardizing trailing slashes and multiple slashes.
    """
    if not raw_url:
        return ""
    
    parsed = urlparse(raw_url.strip())
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()

    # Remove standard ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Remove www. prefix
    if netloc.startswith("www."):
        netloc = netloc[4:]

    # Normalize path
    path = parsed.path or "/"
    path = re.sub(r"/+", "/", path)
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Filter out tracking query parameters and sort remaining
    filtered_queries = []
    if parsed.query:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        for key, value in query_pairs:
            if key.lower() not in TRACKING_PARAMS:
                filtered_queries.append((key, value))
        filtered_queries.sort(key=lambda x: x[0])

    new_query = urlencode(filtered_queries)

    # Reconstruct without fragment
    return urlunparse((scheme, netloc, path, "", new_query, ""))

def normalize_title(raw_title: str) -> str:
    """
    Normalizes article titles by removing boilerplate site suffixes,
    normalizing unicode quotes/dashes, and cleaning extra whitespace.
    """
    if not raw_title:
        return ""
    
    t = raw_title.strip()

    # Replace common unicode dashes and quotes
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace("–", "-").replace("—", "-")

    # Strip common branding suffixes: " | OpenAI", " - DeepMind", " [cs.AI]"
    t = re.sub(r"\s*[\-\|\:]\s*(OpenAI|Google DeepMind|Anthropic|Hugging Face|Meta AI|arXiv).*$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*\[cs\.[a-zA-Z]+\]\s*$", "", t)

    return " ".join(t.split())

def compute_content_hash(text: str) -> str:
    """Computes a SHA-256 hash of normalized text for exact body deduplication."""
    if not text:
        return ""
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
