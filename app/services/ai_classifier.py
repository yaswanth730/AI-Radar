import json
import logging
import re
import time
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.config import settings

logger = logging.getLogger("ai_radar.ai_classifier")

CATEGORIES = [
    "AI Models", "AI Agents", "APIs", "Research", "Open Source",
    "Developer Tools", "Robotics", "Infrastructure", "Security",
    "AI Regulation", "Pricing/API Changes"
]

DOWNRANK_KEYWORDS = [
    "how to use chatgpt", "beginner guide", "tutorial: how to",
    "top 10 ai tools to make money", "earn with ai", "affiliate", "promo code",
    "unsupported rumors", "sponsored post"
]

class ClassificationResult(BaseModel):
    is_ai_related: bool = True
    category: str = "AI Models"
    sub_category: Optional[str] = None
    companies: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    importance_score: float = Field(default=50.0, ge=0.0, le=100.0)
    novelty_score: float = Field(default=50.0, ge=0.0, le=100.0)
    technical_score: float = Field(default=50.0, ge=0.0, le=100.0)
    is_breaking: bool = False
    headline: str = Field(default="")
    summary: str = Field(default="")
    why_it_matters: str = Field(default="")
    is_downranked: bool = False

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        for cat in CATEGORIES:
            if cat.lower() in v.lower():
                return cat
        return "AI Models"


class BaseAIClassifier:
    async def classify_and_summarize(self, title: str, text: str, source_name: str) -> ClassificationResult:
        raise NotImplementedError


class HeuristicClassifier(BaseAIClassifier):
    """
    Offline deterministic NLP heuristic classifier.
    Extracts entities, determines category, detects SEO down-ranking,
    and produces grounded summary without external API dependencies.
    """
    async def classify_and_summarize(self, title: str, text: str, source_name: str) -> ClassificationResult:
        combined = f"{title} {text}".lower()

        # Check for downranking
        is_downranked = any(kw in combined for kw in DOWNRANK_KEYWORDS)

        # Detect Companies
        companies = []
        company_patterns = [
            ("OpenAI", r"\bopenai\b"),
            ("Google DeepMind", r"\b(deepmind|google)\b"),
            ("Anthropic", r"\banthropic\b"),
            ("Meta", r"\b(meta|meta ai|facebook)\b"),
            ("Hugging Face", r"\bhugging\s*face\b"),
            ("Microsoft", r"\bmicrosoft\b"),
            ("NVIDIA", r"\bnvidia\b"),
            ("Apple", r"\bapple\b"),
            ("Mistral", r"\bmistral\b"),
        ]
        for name, pattern in company_patterns:
            if re.search(pattern, combined):
                companies.append(name)

        # Detect Technologies
        technologies = []
        tech_patterns = [
            ("Transformers", r"\btransformers?\b"),
            ("vLLM", r"\bvllm\b"),
            ("Ollama", r"\bollama\b"),
            ("PyTorch", r"\bpytorch\b"),
            ("Diffusion", r"\bdiffusion\b"),
            ("RLHF", r"\brlhf\b"),
            ("LoRA", r"\blora\b"),
            ("Quantization", r"\b(quantization|gguf|awq|fp8)\b"),
            ("RAG", r"\b(rag|retrieval\s+augmented)\b"),
            ("LLM", r"\b(llm|large\s+language\s+model)\b"),
        ]
        for name, pattern in tech_patterns:
            if re.search(pattern, combined):
                technologies.append(name)

        # Determine Category
        category = "AI Models"
        if any(w in combined for w in ["agent", "agents", "tool use", "autonomous"]):
            category = "AI Agents"
        elif any(w in combined for w in ["arxiv", "paper", "benchmark", "evaluation", "dataset"]):
            category = "Research"
        elif any(w in combined for w in ["release", "v0.", "github", "open source", "repository"]):
            category = "Open Source"
        elif any(w in combined for w in ["api", "endpoint", "sdk", "token rate"]):
            category = "APIs"
        elif any(w in combined for w in ["security", "jailbreak", "alignment", "safety"]):
            category = "Security"
        elif any(w in combined for w in ["law", "regulation", "eu ai act", "policy", "copyright"]):
            category = "AI Regulation"

        # Scores calculation
        importance = 65.0
        if "release" in combined or "announcing" in combined or "introducing" in combined:
            importance = 80.0
        if is_downranked:
            importance = 25.0

        novelty = 60.0
        if "state-of-the-art" in combined or "frontier" in combined:
            novelty = 75.0

        technical = 55.0
        if len(technologies) >= 2 or category in ("Research", "Open Source"):
            technical = 70.0

        is_breaking = ("breaking" in combined or "v0." in title) and importance >= 75.0

        # Grounded Headline: approx 15 words
        words = title.split()
        headline = " ".join(words[:15])

        # Grounded Summary: 1-3 sentences
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if len(s.strip()) > 20]
        if sentences:
            summary = ". ".join(sentences[:2]) + "."
        else:
            summary = f"{title} announced by {source_name}."

        why_it_matters = f"This update directly advances {source_name}'s developer ecosystem with improved operational capabilities."
        if category == "Open Source":
            why_it_matters = "Provides new tooling and architecture for modern AI workflows."
        elif category == "Research":
            why_it_matters = "Offers new empirical insights and methodologies for frontier intelligence systems."

        return ClassificationResult(
            is_ai_related=True,
            category=category,
            sub_category=category,
            companies=companies[:3],
            technologies=technologies[:3],
            topics=[category, "Machine Learning"],
            importance_score=importance,
            novelty_score=novelty,
            technical_score=technical,
            is_breaking=is_breaking,
            headline=headline,
            summary=summary[:400],
            why_it_matters=why_it_matters[:200],
            is_downranked=is_downranked
        )


class GeminiClassifier(BaseAIClassifier):
    """
    Primary LLM Classifier using Google Gemini with structured JSON output and Pydantic validation.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-3.8-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.heuristic = HeuristicClassifier()
        self.client = None
        self.cooldown_until = 0.0
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI Client: {e}")

    async def classify_and_summarize(self, title: str, text: str, source_name: str) -> ClassificationResult:
        if not self.client:
            return await self.heuristic.classify_and_summarize(title, text, source_name)

        if time.time() < self.cooldown_until:
            return await self.heuristic.classify_and_summarize(title, text, source_name)

        prompt = f"""You are the AI RADAR intelligence analyst.
Analyze the following collected AI news item from primary source '{source_name}'.
Return ONLY a valid JSON object matching the requested schema.

Title: {title}
Content snippet: {text[:2000]}

Categories permitted: {', '.join(CATEGORIES)}

JSON Schema requirements:
{{
  "is_ai_related": true,
  "category": "one of the permitted categories",
  "sub_category": "specific field or architecture",
  "companies": ["company1", "company2"],
  "technologies": ["tech1", "tech2"],
  "topics": ["topic1", "topic2"],
  "importance_score": 0.0 to 100.0,
  "novelty_score": 0.0 to 100.0,
  "technical_score": 0.0 to 100.0,
  "is_breaking": boolean,
  "headline": "concise headline <= 15 words",
  "summary": "1 to 3 concise grounded factual sentences",
  "why_it_matters": "exactly one strong sentence explaining why this matters",
  "is_downranked": boolean (true if marketing filler, low-signal tutorial, or SEO spam)
}}
"""
        def _call_gemini():
            from google.genai import types
            return self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )

        try:
            response = await asyncio.to_thread(_call_gemini)

            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed_data = json.loads(raw_text.strip())
            return ClassificationResult.model_validate(parsed_data)
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                logger.info("Gemini Free Tier request quota reached; engaging 60s cooldown and seamlessly routing to heuristic.")
                self.cooldown_until = time.time() + 60.0
            elif "NOT_FOUND" in err_str or "API_KEY_INVALID" in err_str or "404" in err_str or "400" in err_str:
                logger.info("Deactivating remote Gemini client for current process session; using high-grade heuristic.")
                self.client = None
            else:
                logger.warning(f"Gemini classification error ({err_str}); falling back to heuristic.")
            return await self.heuristic.classify_and_summarize(title, text, source_name)


def get_ai_classifier() -> BaseAIClassifier:
    """Factory creating configured AI classifier with fallback."""
    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GeminiClassifier(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    return HeuristicClassifier()
