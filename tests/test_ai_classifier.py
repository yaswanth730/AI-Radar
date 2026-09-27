import pytest
from app.services.ai_classifier import (
    ClassificationResult, HeuristicClassifier, GeminiClassifier, get_ai_classifier, CATEGORIES
)

def test_classification_result_validation():
    # Category should clamp to known category
    data = {
        "is_ai_related": True,
        "category": "Advanced AI Agents & Workflows",
        "companies": ["OpenAI"],
        "technologies": ["Agents"],
        "importance_score": 85.0,
        "novelty_score": 75.0,
        "technical_score": 60.0,
        "headline": "OpenAI Launches Autonomous Workflow Agents",
        "summary": "OpenAI has introduced new agent tools.",
        "why_it_matters": "Enables multi-step execution across APIs."
    }
    result = ClassificationResult.model_validate(data)
    assert result.category == "AI Agents"
    assert result.importance_score == 85.0
    assert result.is_ai_related is True

@pytest.mark.asyncio
async def test_heuristic_classifier_company_and_tech_detection():
    classifier = HeuristicClassifier()
    title = "vLLM v0.6.2 Released with LoRA Support on PyTorch"
    text = "The vLLM team announced high-throughput multi-LoRA inference and optimized kernels for modern GPUs."
    
    result = await classifier.classify_and_summarize(title, text, "vLLM Releases")
    assert result.category in ("Open Source", "Developer Tools")
    assert any("lora" in t.lower() or "vllm" in t.lower() for t in result.technologies)
    assert len(result.headline.split()) <= 15
    assert len(result.why_it_matters) > 10
    assert result.is_downranked is False

@pytest.mark.asyncio
async def test_heuristic_classifier_downranking():
    classifier = HeuristicClassifier()
    title = "Top 10 AI Tools to Make Money Online in 2026"
    text = "Beginner guide tutorial: how to earn with AI using affiliate promo codes."
    
    result = await classifier.classify_and_summarize(title, text, "Spam Blog")
    assert result.is_downranked is True
    assert result.importance_score < 40.0

@pytest.mark.asyncio
async def test_gemini_classifier_fallback_on_invalid_key():
    # If key is bad or offline, it must gracefully fallback to heuristic
    classifier = GeminiClassifier(api_key="invalid_fake_key", model_name="gemini-2.5-flash")
    title = "Google DeepMind Unveils AlphaGenome for Genomic Predictions"
    text = "Google DeepMind published new research in nature describing unified genome transformers."
    
    result = await classifier.classify_and_summarize(title, text, "DeepMind")
    assert result is not None
    assert result.is_ai_related is True
    assert "Google DeepMind" in result.companies or "Google" in result.companies
