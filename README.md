# AI CV Assistant

A full-stack application that reviews CVs/resumes (PDF) using LLMs and a
deterministic scoring pipeline. It offers two analysis modes:

- **Candidate mode** — a job seeker uploads their CV and gets a structured review
  (strengths, problems, recommendations, an ATS-style score, and more).
- **HR / Recruiter mode** — a recruiter uploads a CV **and** a job description
  (text, URL, or PDF) and gets a candidate-fit analysis (matched / missing
  skills, fit score, interview questions).

A FastAPI backend does the work; a React (Vite) SPA is the UI. Auth is JWT-based,
and usage is gated by subscription plans (Free / Pro / Enterprise).

---

## Two ways to run the project

You can run everything **locally** (good for development) or with **Docker
Compose** (good for a one-command, reproducible stack). Pick one.

| | Variant 1 — Local development | Variant 2 — Docker Compose |
|---|---|---|
| Backend | `uvicorn app.main:app --reload` (port 8000) | `backend` service (port 8000) |
| Frontend | `npm run dev` (Vite, port 5173) | `frontend` service served by nginx (port 8081) |
| Database | A local PostgreSQL instance | `db` service (PostgreSQL 16) |
| LLM provider | Local Ollama **or** OpenAI API | Optional `ollama` service (GPU) **or** OpenAI API |
| Entry point | `http://localhost:5173` | `http://localhost:8081` |

The analysis engine supports two **LLM providers**, configurable per request:

- `local` — runs an **Ollama** model on your machine/container (default).
- `api` — calls the **OpenAI API** (requires a plan that allows it: Pro or
  Enterprise, plus `OPENAI_API_KEY`).

> The "two variants" above are about *how to run the project*. The `local` /
> `api` choice is about *which LLM does the analysis*. You can mix freely — e.g.
> run with Docker Compose and still call OpenAI, or run locally and use Ollama.

---

## Project structure

```
AI CV assistant/
├── app/                       # FastAPI backend
│   ├── main.py                # app factory, CORS, router wiring, startup
│   ├── api/v1/                # HTTP routers (versioned)
│   │   ├── auth.py            #   register / login / refresh / me
│   │   ├── resume_analysis.py #   POST /analyze-resume  (Candidate mode)
│   │   ├── hr_analysis.py     #   POST /hr/analyze-candidate (HR mode)
│   │   ├── subscriptions.py   #   plans / me / subscribe / cancel
│   │   └── usage.py           #   GET /usage/me
│   ├── core/                  # config, DB session, security (JWT/bcrypt), deps
│   ├── llm/                   # LLM integration (Ollama + OpenAI) + prompt templates
│   │   ├── llm_analyzer.py
│   │   └── prompts/
│   ├── processing/            # deterministic CV text pipeline (no ML here)
│   │   ├── pdf_extractor.py   #   PDF -> text (PyMuPDF)
│   │   ├── cleaner.py         #   whitespace / punctuation / line cleanup
│   │   ├── resume_features.py #   feature extraction (email, phones, counts, ...)
│   │   └── scoring.py         #   heuristic scoring (sections, bullets, achievements)
│   ├── models/                # SQLAlchemy ORM (User, SubscriptionPlan, ...)
│   ├── schemas/               # Pydantic request/response models
│   └── services/              # business logic (auth, analysis, subscription, usage)
├── frontend/                  # React + Vite SPA (see frontend/README.md)
│   ├── src/                   #   pages, components, context, api client
│   ├── Dockerfile / nginx.conf
│   └── vite.config.js         #   proxies /api -> backend in dev
├── db/schema.sql              # reference PostgreSQL schema + seed plans
├── scripts/                   # standalone demo scripts (not pytest tests)
│   ├── demo_pdf_extractor.py
│   ├── demo_llm_analyzer.py
│   ├── demo_openai_analyzer.py
│   └── demo_hr_analyzer.py
├── datasets/                  # gitignored — sample PDFs used by the demos
├── storage/                   # gitignored — runtime upload / report dirs
├── Dockerfile                 # backend image
├── docker-compose.yml         # db + backend + frontend (+ optional ollama)
├── requirements.txt
├── .env.example               # copy to .env and fill in
└── README.md
```

Notes on the layout:

- `app/processing/` holds the **deterministic** text pipeline (PDF extraction,
  cleaning, feature extraction, heuristic scoring). It is deliberately separate
  from `app/llm/`, which holds the **model** calls (Ollama / OpenAI).
- `scripts/demo_*.py` are manual scratch scripts that import from `app` and
  print results. They are named `demo_` (not `test_`) on purpose — they are not
  pytest tests.

---

## Variant 1 — Run locally (development)

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- A PostgreSQL database (or change `DATABASE_URL` to point at one)
- For the `local` LLM provider: [Ollama](https://ollama.com) running locally
  (default `http://localhost:11434`) with a pulled model, e.g.
  `ollama pull qwen2.5:3b`.
- For the `api` LLM provider: an OpenAI API key.

### 1. Backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env (see below)
```

Configure `.env` (key fields):

| Variable | Meaning | Example |
|---|---|---|
| `LLM_PROVIDER` | Default provider used by demos/analysis | `local` |
| `OLLAMA_MODEL` | Ollama model tag (provider `local`) | `qwen2.5:3b` |
| `OPENAI_MODEL` | OpenAI model (provider `api`) | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI key (only needed for provider `api`) | `sk-...` |
| `DATABASE_URL` | SQLAlchemy DB URL | `postgresql+psycopg2://postgres:postgres@localhost:5432/aicv` |
| `JWT_SECRET` | **Set a long random string in production** | `change-me-...` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173` |

Make sure the PostgreSQL database named in `DATABASE_URL` exists
(e.g. `createdb aicv`). On startup the app auto-creates the tables and seeds the
default plans. `db/schema.sql` is an optional reference script if you prefer to
create the schema manually:

```bash
psql "postgresql://postgres:postgres@localhost:5432/aicv" -f db/schema.sql
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000` (health check at `/health`).

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173`. In dev, Vite proxies `/api` requests
to the backend at `http://localhost:8000` (see `frontend/vite.config.js`).

### 3. Use it

Open `http://localhost:5173`, register an account, choose Candidate or HR mode,
upload a CV PDF (and a job description for HR mode), pick a provider, and
analyze.

---

## Variant 2 — Run with Docker Compose

### Prerequisites

- Docker and Docker Compose v2+

### Steps

1. (Optional) copy `.env.example` to `.env` and adjust. The compose file already
   provides sensible defaults for the database and CORS, so this is only needed
   if you want to change the model, the JWT secret, or use OpenAI.

2. Start the stack:

   ```bash
   docker compose up --build
   ```

   This starts:
   - `db` — PostgreSQL 16
   - `backend` — FastAPI on port **8000**
   - `frontend` — built React app served by nginx on port **8081**

   Open `http://localhost:8081`.

### Choosing the LLM provider with Docker

The default provider is `local` (Ollama). With Compose you have two options:

- **OpenAI (no GPU needed):** set `LLM_PROVIDER=api` and `OPENAI_API_KEY=sk-...`
  in `.env`, then `docker compose up --build`. (Your plan must allow OpenAI —
  Pro or Enterprise.)
- **Ollama in a GPU container:** use the `ollama` profile, which also starts a
  managed Ollama container and pulls the configured model:

  ```bash
  docker compose --profile ollama up --build
  ```

  This requires an NVIDIA GPU (the compose file reserves `count: all` GPU
  devices). With the profile active, `OLLAMA_HOST` is wired to the `ollama`
  service automatically. To point the backend at an Ollama instance you already
  run elsewhere, set `OLLAMA_HOST` in `.env` instead and don't use the profile.

### Ports

| Service | Host port | Container port |
|---|---|---|
| Frontend (nginx) | 8081 | 80 |
| Backend (uvicorn) | 8000 | 8000 |
| Postgres | (not published by default) | 5432 |
| Ollama (with profile) | 11434 | 11434 |

---

## API endpoints

All `/api/v1/...` routes are JSON. File uploads are multipart.

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET  | `/health` | — | Health check |
| POST | `/api/v1/auth/register` | — | Create account, returns token pair |
| POST | `/api/v1/auth/login` | — | Sign in, returns token pair |
| POST | `/api/v1/auth/refresh` | — | Refresh the token pair |
| GET  | `/api/v1/auth/me` | bearer | Current user |
| POST | `/api/v1/analyze-resume` | bearer | **Candidate** CV analysis (PDF) |
| POST | `/api/v1/hr/analyze-candidate` | bearer | **HR** CV analysis (PDF + job description: text / URL / PDF) |
| GET  | `/api/v1/subscriptions/plans` | — | Plan catalog |
| GET  | `/api/v1/subscriptions/me` | bearer | Current subscription |
| POST | `/api/v1/subscriptions/subscribe` | bearer | Subscribe to a plan (simulated) |
| POST | `/api/v1/subscriptions/cancel` | bearer | Cancel subscription |
| GET  | `/api/v1/usage/me` | bearer | Usage for the current billing period |

Limits: PDF uploads up to 10 MB. Job-description URLs must be public http(s)
and are capped at 10 MB / 50k chars of extracted text.

---

## Subscriptions and usage

| Plan | Analyses / month | OpenAI (`api`) | Notes |
|---|---|---|---|
| Free | 3 | ❌ | Local LLM only |
| Pro | 30 | ✅ | HR mode, PDF job-description upload |
| Enterprise | Unlimited | ✅ | Team accounts, API access, priority |

Usage is counted per billing period. The `api` (OpenAI) provider is only allowed
on Pro / Enterprise plans; attempting it on Free returns `403`.

---

## Demo scripts

The `scripts/demo_*.py` files run pieces of the pipeline standalone and print
the result. They add the project root to `sys.path` and import from `app`, so run
them from a venv that has `requirements.txt` installed:

```bash
python scripts/demo_pdf_extractor.py [path/to/cv.pdf]   # extract + clean + features
python scripts/demo_llm_analyzer.py                     # full Candidate analysis (local)
python scripts/demo_openai_analyzer.py                  # Candidate analysis via OpenAI
python scripts/demo_hr_analyzer.py                       # HR analysis (local, fake CV + JD)
```

`demo_pdf_extractor.py` accepts a PDF path as an argument and defaults to a
sample under `datasets/data/...` (the `datasets/` folder is gitignored).

---

## Notes & security

- `.env` is gitignored — never commit real secrets. Keep `JWT_SECRET` and
  `OPENAI_API_KEY` out of version control. **Rotate any API key that may have
  been exposed.**
- The backend validates that uploads are PDFs and under 10 MB. HR job
  description URLs are resolved and checked to point at public addresses;
  redirects are rejected.
- Frontend dev (Vite) runs on `5173`; the Dockerized frontend is served on
  `8081`. `CORS_ORIGINS` in `.env.example` allows both by default.
- `alembic` is listed in `requirements.txt` but migrations are not currently
  used — tables are created on startup via SQLAlchemy's `create_all()`.

## Tech stack

- Backend: FastAPI, SQLAlchemy 2, Pydantic v2, PyMuPDF, Ollama, OpenAI, JWT
- Frontend: React 18, Vite 4, react-router-dom 6, plain CSS
- Infra: Docker, Docker Compose, PostgreSQL 16, nginx

## License

MIT
