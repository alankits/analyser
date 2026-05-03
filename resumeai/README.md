# ResumeAI

> **AI-Powered Resume Analysis** — Upload your resume, get an ATS score, section rewrites, career matches, and a personalised learning roadmap in one click.

---

## Features

| Feature | Description |
|--------|-------------|
| **ATS Scorer** | Keyword matching against job description, section completeness scoring, grade (A–F) |
| **Resume Fixer** | Section-by-section BEFORE/AFTER rewrites in STAR format with reasons |
| **Career Matcher** | 3 role recommendations with match %, skill gaps, and recommended projects |
| **Learning Roadmap** | 3-phase personalised plan with skills, resources, hours, and milestones |
| **PDF Report** | Multi-page downloadable report with dark navy theme |

---

## Tech Stack

**Frontend:** Next.js 14 (App Router) · TypeScript · Tailwind CSS · Framer Motion · React Query · React Hook Form + Zod · Axios

**Backend:** Python 3.11 · FastAPI · Pydantic v2 · SQLAlchemy (async) · pdfplumber · python-docx · pytesseract · ReportLab

**LLM:** Mistral-7B-Instruct via HuggingFace Inference API · zephyr-7b-beta fallback

**Database:** SQLite (local dev) → PostgreSQL (Railway production)

**Cache:** Redis (optional — app runs without it)

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A HuggingFace account and API token ([get one here](https://huggingface.co/settings/tokens))

### 1. Clone the repository

```bash
git clone https://github.com/your-username/resumeai.git
cd resumeai
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env and set HF_API_TOKEN=hf_your_token_here

# Start the API server
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive API docs.

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.local.example .env.local

# Start the dev server
npm run dev
```

The frontend will be running at `http://localhost:3000`.

---

## HuggingFace Token Setup

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **New Token** → select **Read** access
3. Copy the token (starts with `hf_`)
4. Add it to `backend/.env` as `HF_API_TOKEN=hf_your_token`

**Models used:**
- Primary: `mistralai/Mistral-7B-Instruct-v0.3`
- Fallback: `HuggingFaceH4/zephyr-7b-beta`

> **Note:** Both models require accepting their license on HuggingFace before the API will serve them. Visit each model's page and click **Agree and access repository**.

---

## Deployment Guide

### Frontend → Vercel

1. Push the `frontend/` directory to a GitHub repository
2. Go to [vercel.com](https://vercel.com) → **New Project** → import the repo
3. Set **Root Directory** to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app`
5. Deploy

### Backend → Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
2. Select your repo and set the **Root Directory** to `backend`
3. Add all environment variables from `backend/.env.example` in Railway's Variables tab
4. To use PostgreSQL: add a PostgreSQL plugin in Railway, then set `DATABASE_URL` to the provided connection string (replace `postgresql://` with `postgresql+asyncpg://`)
5. Deploy — Railway will use `railway.toml` for build/start commands

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (Next.js 14)                                           │
│  Landing → Analyze → Results (ATS / Fixes / Careers / Roadmap) │
└────────────────────────────┬────────────────────────────────────┘
                             │ POST /api/v1/analyze (multipart)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ file_handler │  │ text_extract │  │    text_cleaner      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         └─────────────────┴─────────────────────┘              │
│                           │ cleaned_text                        │
│          ┌────────────────┼────────────────────┐               │
│          ▼                ▼                    ▼               │
│     ats_scorer      resume_fixer         career_matcher        │
│          └────────────────┬────────────────────┘               │
│                           │ skill_gaps                          │
│                           ▼                                    │
│                    roadmap_generator                            │
│                           │                                    │
│                    SQLite / PostgreSQL                          │
│                    Redis cache (optional)                       │
└─────────────────────────────────────────────────────────────────┘
                             │ GET /api/v1/report/{id}
                             ▼
                       reportlab PDF
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/analyze` | Upload resume, run full analysis |
| `GET` | `/api/v1/analysis/{id}` | Retrieve stored analysis by ID |
| `GET` | `/api/v1/report/{id}` | Download PDF report |
| `GET` | `/health` | Health check (DB, Redis, HF API) |

---

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example` for all required variables.

---

## License

MIT
