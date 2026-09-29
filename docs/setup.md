# Setup

## Prereqs

| Tool | Check | Notes |
|---|---|---|
| Git | `git --version` | |
| Python via `uv` | `uv --version` | Backend dep manager |
| Node 22 | `node --version` | Frontend |
| Rust | `cargo --version` | `rust-core` |
| Docker + WSL 2 | `docker --version` | Full stack via compose |

Docker Desktop: enable the WSL 2 backend and integrate your distro
(Settings → Resources → WSL Integration, Ubuntu recommended).

## Full stack (Postgres + API)

From the repo root:

```powershell
docker compose up --build
```

- API: http://localhost:8000/health
- Postgres: `localhost:5432`, user/password/db = `ivy`

## Backend only (SQLite file, zero config)

```powershell
cd backend
uv sync --extra dev --frozen
uv run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Point at Postgres instead with `IVY_DATABASE_URL`
(see `backend/.env.example`). Tests always use isolated
in-memory SQLite — no database needed:

```powershell
uv run --frozen pytest -q
uv run --frozen ruff check .
```

## Frontend

```powershell
cd frontend
npm install
npm run dev     # :5173, talks to VITE_API_BASE (default http://localhost:8000)
npm run build
```

## Rust core

```powershell
cd rust-core
cargo test
cargo clippy --all-targets -- -D warnings
cargo fmt --check
```

Windows MSVC target needs VS Build Tools with the C++ workload;
otherwise use `cargo +stable-x86_64-pc-windows-gnu test` with MinGW GCC on `PATH`.

## Standalone demos

No toolchain needed — open in a browser:

- `Interactive Tool/ivy-demo.html` — minimal demo
- `Interactive Tool/ivy-full.html` — full offline app (optional live backend at `:8000`)
