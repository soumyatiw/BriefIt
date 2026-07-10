# BriefIt

BriefIt is an AI-powered multilingual news digest pipeline. It scrapes 10–15 RSS/web sources, deduplicates and clusters articles into coherent stories using sentence embeddings, then summarises and translates each story into English, Hindi, Tamil, and Telugu. The entire pipeline is orchestrated as a LangGraph graph, persisting state in SQLite, and exposed through a FastAPI backend with a React frontend.

## How to run

### Setup
```bash
# 1. Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install backend dependencies (no AI packages yet)
pip install -r requirements-backend.txt

# 3. Configure environment
cp .env.example .env   # then open .env and set a real JWT_SECRET_KEY
```

### Day 1 — verify the environment
```bash
# Initialise the database (creates data/briefit.db with 0 tables — expected)
python -m scripts.init_db

# Smoke-test config loading
python -c "from api.config import settings; print(settings.database_url, settings.jwt_algorithm)"

# Smoke-test DB imports
python -c "from api.database import engine, SessionLocal, Base; print(engine)"

# Confirm the DB file was created
ls data/
```

[Day 2 commands land here: python -m scripts.seed_sources, etc.]

[Day 4 commands land here: uvicorn api.main:app --reload]

[Day 10 commands land here: cd frontend && npm install && npm run dev]
