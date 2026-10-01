# FutBud

FutBud is a football analytics application with player and team dashboards,
match data, search, rankings, and the frozen FutBud Rating v1 role-relative
rating system.

## Live application

- Frontend: https://futbud.vercel.app
- API: https://futbud-api.onrender.com
- API health: https://futbud-api.onrender.com/health
- API documentation: https://futbud-api.onrender.com/docs

## Production architecture

```text
API-Football
    |
FutBud refresh pipeline
    |
Neon PostgreSQL
    |
Render FastAPI
    |
Vercel React/Vite
    |
Public user
```

- Frontend: React, TypeScript, and Vite on Vercel
- Backend: FastAPI on Render
- Database: managed PostgreSQL on Neon
- Data: API-Football, fetched only by server-side Python code
- ML: frozen FutBud v1 archetype and role-relative rating system

## Local development

Copy the safe environment templates and provide your own local values. Never
commit the resulting `.env` files.

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Start the API from `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend from `frontend/`:

```bash
npm install
npm run dev
```

The backend uses `DATABASE_URL` when present. For local development it can
instead use the `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`
variables documented in `backend/.env.example`. The frontend reads its API
origin from `VITE_API_URL`.

## Refreshing production data

From `backend/`, with `DATABASE_URL` pointing to the intended database and
`API_FOOTBALL_KEY` set in the environment:

```bash
python -m scripts.update_current_data
```

The default run checks yesterday and today plus stale or incomplete current-
season fixtures. A controlled range can be supplied explicitly:

```bash
python -m scripts.update_current_data 2026-09-20 2026-09-20
```

The pipeline refreshes fixtures, details and lineups, player and team match
statistics, standings, current-season aggregates, and then applies the frozen
FutBud v1 inference artifacts before importing ratings into PostgreSQL.

Production refreshes are scheduled daily at 09:17 UTC by
`.github/workflows/update-current-data.yml`. They can also be started manually
from the repository's **Actions** tab. The workflow requires repository secrets
named `DATABASE_URL` and `API_FOOTBALL_KEY`.
