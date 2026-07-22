# BriefIt: Agentic News Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-AI_Agents-FF9900)
![Groq](https://img.shields.io/badge/Groq-Llama_3.1-f55036)

**BriefIt** is an autonomous, multi-agent AI news intelligence platform developed for the IGDTUW Summer Internship Program (SIP) 2026 under the Generative & Agentic AI Systems Development track.

The system ingests raw RSS news feeds, uses **DBSCAN** and **FastEmbed (MiniLM)** to semantically cluster related articles, and employs **LangGraph** agents backed by **Meta Llama 3.1 8B** (via Groq) to synthesise comprehensive, neutral summaries and perform sentiment analysis.

---

## Team Information
**Team Name:** Tarang | Team No. 68  
**Project Track:** Agentic AI Systems Development  
**Institution:** Indira Gandhi Delhi Technical University for Women (IGDTUW)  

**Team Members:**
- Soumya Tiwari (Leader)
- Jiya Sachan
- Anushka
- Bhavya Garg
- Saniya Khoba

---

## System Architecture

1. **Ingestion:** Scrapes live RSS feeds (The Hindu, Livemint, etc.).
2. **Embedding & Clustering:** Generates 384-dimensional multilingual embeddings. Uses DBSCAN ($\epsilon = 0.34$) for highly precise semantic deduplication.
3. **Agentic Pipeline (LangGraph):** Routes clustered stories through summarisation and sentiment analysis nodes.
4. **Data Storage:** Stores processed stories in Neon Serverless PostgreSQL with `pgvector` for semantic search.
5. **Frontend Application:** A responsive React UI for exploring categorised, synthesised news.

---

## Local Setup Instructions

Follow these steps to run BriefIt locally.

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL** (Local or Neon Cloud)
- **Groq API Keys** (Free tier)

### 2. Clone the Repository
```bash
git clone https://github.com/soumyatiw/BriefIt.git
cd BriefIt
```

### 3. Backend Setup (API & AI Pipeline)
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
```
Open the `.env` file and configure your variables:
```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost/briefit
GROQ_API_KEY_SUMMARIZE=gsk_...
GROQ_API_KEY_SENTIMENT=gsk_...
JWT_SECRET_KEY=your_secure_random_string
```

```bash
# Initialise the database schema (creates tables in PostgreSQL)
python -m scripts.init_db

# Seed the database with default RSS sources
python -m scripts.seed_sources

# Start the FastAPI backend server
uvicorn api.main:app --reload
```
*The backend API will be available at `http://localhost:8000`.*

### 4. Running the Agentic AI Pipeline
You can trigger the LangGraph ingestion and synthesis pipeline manually:
```bash
# While in the activated virtual environment:
python -m scripts.run_pipeline_once
```
*(Note: To prevent Groq rate limits, the pipeline is capped at 60 articles per run).*

### 5. Frontend Setup (React UI)
Open a **new terminal window** (keep the FastAPI server running).
```bash
cd frontend

# Install Node dependencies
npm install

# Configure Environment
cp .env.example .env.production
# Ensure VITE_API_URL is set to http://localhost:8000

# Start the React development server
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

---

## Evaluation & Metrics
A dedicated pipeline evaluation notebook is provided to demonstrate the clustering effectiveness on a hand-labelled dataset.
- **Location:** `notebooks/evaluation.ipynb`
- **Execution:** Run the notebook to compute the exact Precision and F1 scores mathematically via `scikit-learn` pairwise metrics.

## License
This project is submitted for academic evaluation. All rights reserved by the respective team members.
