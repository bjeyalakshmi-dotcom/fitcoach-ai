# FitCoach AI 🏋️
**AI-based Exercise & Diet Planning — Multi-Agent System**

Built with OpenAI GPT-4o · FastAPI · Streamlit · SQLite

---

## Live Demo
Deploy your own → see **Deploy to Streamlit Cloud** below.

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/fitcoach-ai.git
cd fitcoach-ai/fitagent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-proj-...

# 4. Start the API
uvicorn main:app --reload --port 8080

# 5. Start the UI (new terminal)
streamlit run ui.py --server.port 9000
```

Open `http://localhost:9000`

---

## Deploy to Streamlit Community Cloud (Free)

1. **Push this repo to GitHub** (see steps below)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app**
4. Select your repo → Branch: `main` → Main file: `fitagent/ui.py`
5. Click **Advanced settings → Secrets** and add:
```toml
OPENAI_API_KEY = "sk-proj-your-key-here"
DB_PATH = "fitagent.db"
```
6. Click **Deploy**

Your app will be live at:
`https://your-username-fitcoach-ai.streamlit.app`

> The FastAPI backend starts automatically in a background thread — no separate server needed on Streamlit Cloud.

---

## Architecture

```
Streamlit UI (port 9000 / Streamlit Cloud)
        ↓  HTTP
FastAPI Orchestrator (port 8080 / background thread on cloud)
        ↓  tool-use loop
OpenAI GPT-4o
        ↓
5 Specialist Agents:
  PlannerAgent · NutritionAgent · ProgressTrackerAgent
  CoachAgent · LearningLoopAgent
        ↓
SQLite (auto-created on startup)
```

---

## API Docs
`http://localhost:8080/docs` (local) — Interactive Swagger UI

---

## Tech Stack
| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database | SQLite |
| Validation | Pydantic v2 |
