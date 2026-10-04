# SAMA Agent — The Clothing Atelier AI Assistant

An AI-powered assistant for SAMA boutique. Plan collections, analyze fabrics, evaluate designs, generate Instagram content, and plan launches — all in one place.

## Stack
- **Frontend:** React + Vite + Tailwind CSS (port 3000)
- **Backend:** FastAPI + LangGraph + OpenAI (port 8000)
- **Database:** SQLite (persisted via Docker volume)
- **Container:** Docker Compose

---

## Quick Start (for your friend)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An OpenAI API key

### Steps

1. **Get the project**
   ```bash
   # Either clone or unzip the project folder
   cd sama_agent
   ```

2. **Add your API key**
   ```bash
   cp .env.example .env
   # Open .env and replace sk-your-key-here with your actual OpenAI API key
   ```

3. **Run**
   ```bash
   docker compose up --build
   ```
   First build takes ~3 minutes. After that, open **http://localhost:3000** in your browser.

4. **Stop**
   ```bash
   docker compose down
   ```
   Your saved items are preserved in a Docker volume.

---

## Features

| Feature | What it does |
|---|---|
| Collection Planner | Full 8-section collection plan from a single prompt |
| Fabric Analyzer | Analyze fabric photos or descriptions, get garment concepts |
| Design Evaluator | Score designs 1–10 across 11 criteria with honest critique |
| Collection Expander | Turn one garment into a full mini collection |
| Content Generator | Reels, photos, stories, captions with tone checking |
| Launch Planner | Day-by-day T-21 to T+7 timeline with CSV export |
| Pricing Calculator | Pure Python cost breakdown and price tiers |
| Saved Items | All approved outputs with feedback memory |

---

## Development Setup (without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env  # add your key
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # runs on http://localhost:3000
```

### Tests
```bash
cd backend
pip install pytest
pytest ../tests/ -v
```

---

## Configuration

All config is in `.env`:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | required | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Main model (vision-capable) |
| `OPENAI_MODEL_FAST` | `gpt-4o-mini` | Fast model for router and tone checker |

---

## Project Structure

```
sama_agent/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py
│   ├── schemas.py           # All Pydantic models
│   ├── knowledge_loader.py
│   ├── knowledge/           # Brand knowledge markdown files
│   ├── graphs/              # LangGraph workflows
│   ├── tools/               # Pricing, tone checker, guardrails
│   └── memory/              # SQLite database
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/           # One page per feature
│   │   ├── components/      # Shared UI components
│   │   └── api/             # API client
│   └── Dockerfile
└── tests/
    ├── test_pricing.py
    └── test_schemas.py
```
