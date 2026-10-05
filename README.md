# GitVia
## 🚧🚧 Under Development 🚧🚧
> From what you build to where you go next.

GitVia is an evidence-based career copilot for developers. It OAuths GitHub, scores repositories with a documented heuristic rubric (README, layout, tests, Docker, CI), compares that evidence to a resume and job description, then generates a week-by-week plan.

Scores are **deterministic**. The assistant answers from stored analysis — it does not invent a 92/100.

## Stack

- **Frontend:** Next.js 16, React 19, Tailwind 4
- **API:** FastAPI, SQLAlchemy 2
- **DB:** SQLite (local default) or PostgreSQL 17
- **Auth:** GitHub OAuth, HttpOnly JWT cookie, encrypted GitHub tokens at rest

## Local setup

### 1. Postgres (optional)

```bash
docker compose up postgres -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
```

Fill in `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `JWT_SECRET`.

Generate a Fernet key (recommended in production):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Put it in `ENCRYPTION_KEY`. If omitted, GitVia derives a key from `JWT_SECRET`.

GitHub OAuth app callback:

`http://localhost:8000/api/auth/github/callback`

```bash
uvicorn app.main:app --reload --port 8000
```

Health: `http://localhost:8000/api/health`

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000` and continue with GitHub.

### Docker API + Postgres

Copy `backend/.env.example` to `backend/.env`, then:

```bash
docker compose up --build
```

## Scoring rubric (abbreviated)

Each repo is scored 0–100 from **file tree + README**, not full source AST:

| Dimension | Evidence examples |
|---|---|
| Documentation | README exists, length, architecture/setup sections |
| Architecture | `app/`, `src/`, services/models layering |
| Code quality | Structured files, typed/backend languages |
| Testing | `tests/`, `spec`, pytest/jest paths |
| DevOps | Dockerfile, docker-compose, `.github/workflows` |
| Scalability | postgres/redis/celery/queue hints |

Overall = weighted mix of those six. Profile, job match, and roadmap **read the cached profile** unless you pass `?refresh=true`.

## API

| Method | Path | Notes |
|---|---|---|
| GET | `/api/auth/github` | Start OAuth |
| GET | `/api/auth/me` | Current user |
| POST | `/api/auth/logout` | Clear session |
| GET | `/api/profile` | Cached profile; `?refresh=true` re-analyzes |
| GET | `/api/repos` | Cached repos; `?refresh=true` re-analyzes |
| POST | `/api/career/resume/upload` | Persist resume + mismatches |
| POST | `/api/career/jobs/analyze` | Persist JD + match |
| GET | `/api/roadmap` | Cached by target role |
| GET/POST | `/api/chat` | History + reply from stored analysis |

## Tests

```bash
cd backend
pytest
```

## Production notes

- Set `COOKIE_SECURE=true`, a strong `JWT_SECRET`, `ENCRYPTION_KEY`, `FRONTEND_URL`, and `CORS_ORIGINS`.
- Use PostgreSQL (`DATABASE_URL`).
- GitHub tokens are encrypted at rest. Session JWTs expire (`JWT_EXPIRE_HOURS`, default 7 days).
- OAuth scope includes `public_repo` so public repository trees can be read.
- `AUTO_CREATE_TABLES=true` bootstraps schema (replace with Alembic before destructive schema changes).
- First analysis hits GitHub; later requests use Postgres/SQLite.

## Honest limitations

- Heuristics inspect README + paths (and detected manifests), not every source file.
- Chat is rule-based over stored scores, not a general LLM.
- Private repos need a `repo` OAuth scope (not the default).
