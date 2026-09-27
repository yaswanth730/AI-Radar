import pytest
from app.services.normalization import (
    normalize_url, normalize_title, compute_content_hash
)

def test_normalize_url_strips_tracking_params():
    raw = "https://www.openai.com/index/gpt-5/?utm_source=twitter&utm_medium=social&utm_campaign=launch&fbclid=IwAR234#discussion"
    canonical = normalize_url(raw)
    assert canonical == "https://openai.com/index/gpt-5"
    assert "utm_source" not in canonical
    assert "fbclid" not in canonical
    assert "#discussion" not in canonical

def test_normalize_url_preserves_meaningful_params():
    raw = "https://github.com/vllm-project/vllm/releases?tag=v0.6.0&utm_source=newsletter"
    canonical = normalize_url(raw)
    assert canonical == "https://github.com/vllm-project/vllm/releases?tag=v0.6.0"

def test_normalize_url_deterministic_query_ordering():
    url1 = "https://example.com/api/model?b=beta&a=alpha"
    url2 = "https://example.com/api/model?a=alpha&b=beta"
    assert normalize_url(url1) == normalize_url(url2)

def test_normalize_url_standardizes_slashes_and_ports():
    raw1 = "http://www.deepmind.google:80/research//gemini-2/"
    canonical1 = normalize_url(raw1)
    assert canonical1 == "http://deepmind.google/research/gemini-2"

def test_normalize_title_strips_branding_suffixes():
    raw = "Gemini 2.5: Flash Thinking Mode - Google DeepMind"
    normalized = normalize_title(raw)
    assert normalized == "Gemini 2.5: Flash Thinking Mode"

def test_normalize_title_handles_unicode_and_quotes():
    raw = "“OpenAI’s New Agentic Workflow” – Next-Gen Tools [cs.AI]"
    normalized = normalize_title(raw)
    assert normalized == "\"OpenAI's New Agentic Workflow\" - Next-Gen Tools"

def test_compute_content_hash_consistency():
    text1 = "Anthropic released Claude 3.5 Sonnet with enhanced computer use."
    text2 = "  anthropic   released claude 3.5 sonnet with   enhanced computer use.  "
    assert compute_content_hash(text1) == compute_content_hash(text2)
    assert len(compute_content_hash(text1)) == 64
