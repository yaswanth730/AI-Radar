# AI RADAR 📡⚡

> **Autonomous Personal AI Intelligence Platform**  
> First-party primary source discovery, multi-signal deduplication, grounded Gemini intelligence analysis, transparent mathematical ranking, and mobile-first Tinder-style radar feed.

---

## 🚀 Overview

**AI RADAR** eliminates noise, SEO content farms, and repetitive hype by connecting directly to first-party primary AI feeds:
- Official Company Engineering & Research Blogs (Google DeepMind, OpenAI, Meta AI, Anthropic)
- Machine Learning Repositories & Release Feeds (Hugging Face, vLLM, Ollama, Transformers)
- Peer-Reviewed Preprints (arXiv cs.AI)

### The Core Ingestion Pipeline
```
FETCH ➔ EXTRACT ➔ NORMALIZE ➔ DEDUPLICATE ➔ CLASSIFY ➔ SCORE ➔ SUMMARIZE ➔ STORE ➔ RANK ➔ DISPLAY
```

Unlike basic AI search wrappers, **AI RADAR never asks an LLM to hallucinate news**. Content is scraped and normalized from real sources first, then deduplicated using canonical URL heuristics and token-sort fuzzy matching before being analyzed and grounded by Google Gemini (`gemini-3.8-flash`) with automatic offline heuristic fallback.

---

## ✨ Features

- **Radar Swipe Deck (Mobile-First)**: Interactive card stack with physics-based gesture swiping (Swipe Right to Like, Swipe Left to Pass, Bookmark, Expand Deep Details).
- **Radar Sweep Canvas**: Real-time rotating radar HUD with telemetry indicators and active signal count.
- **For You Feed**: Dynamically personalized feed adapting in real time to your company, topic, and technology engagement history.
- **Trending Feed**: Real-time momentum ranking highlighting breaking breakthroughs.
- **Saved Bookmarks**: Full-text offline-accessible archive of bookmarked stories.
- **Source Health Monitor**: Primary source status telemetry, latency tracking, and one-click manual scan triggering.
- **Settings & Intelligence Tuner**: Configurable automated scan intervals (5m / 10m / 30m / 60m) and transparency viewer into learned preference affinities.
- **Transparent Mathematical Ranking**: Every story score is computed deterministically:
  $$\text{Score} = 0.40 \cdot \text{Imp} + 0.30 \cdot \text{Personal} + 0.20 \cdot \text{Recency} + 0.10 \cdot \text{Novelty}$$
  with exponential 48-hour half-life recency decay.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, high-performance async Python web framework.
- **SQLAlchemy & SQLite (WAL Mode)**: Ultra-reliable local storage configured with write-ahead logging and 5000ms busy timeout.
- **Google GenAI SDK (`gemini-3.8-flash`)**: Structured JSON schema extraction for grounded headlines, 1–3 sentence summaries, and single-sentence impact statements with quota-aware circuit breaker.
- **APScheduler**: Autonomous 10-minute background ingestion runner.
- **RapidFuzz**: High-performance C++ accelerated token-sort string similarity matching.
- **Trafilatura & Feedparser**: Robust HTML sanitization and RSS/Atom extraction.

### Frontend
- **React 19 & TypeScript**: Type-safe component architecture.
- **Vite**: Sub-second Hot Module Replacement (HMR) and optimized production bundle.
- **Tailwind CSS**: Sleek cyber-terminal dark mode aesthetic (`#08090C`, `#0D0F14`, neon emerald `#00FFA3`, accent yellow `#CCFF00`).
- **Framer Motion**: Gesture-driven mobile swiping physics and transition animations.
- **Lucide Icons**: Crisp vector UI iconography.

---

## 🚦 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Gemini API Key

### 1. Run the Backend Server
```bash
cd backend

# Create virtual environment & install dependencies
python -m venv .venv
.\.venv\Scripts\activate      # Windows (or 'source .venv/bin/activate' on Linux/macOS)
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example or edit backend/.env:
# GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-3.8-flash

# Start the API server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend will start at `http://127.0.0.1:8000`.  
Interactive API docs are available at `http://127.0.0.1:8000/docs`.

### 2. Run the Frontend Dev Server
```bash
cd frontend

# Install packages
npm install

# Start Vite server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing

The backend includes a comprehensive pytest suite covering API routes, canonical URL normalization, deduplication arbitration, classification fallbacks, and ranking decay:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```
All 35 unit and integration tests pass with 100% success.

---

## 🛡️ Security & Privacy
- **Zero API Keys in Frontend**: All LLM interactions are isolated server-side.
- **Strict Grounding**: Summaries are generated strictly from the collected text snippet; no hallucinated claims.
- **Local Sovereignty**: User preferences and interaction histories reside on the local SQLite database.
