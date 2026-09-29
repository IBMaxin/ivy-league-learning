# Ivy Frontend

React + Vite SPA. Network, execution, data, and UI live in separate places.

## Layout

| Path | Concern |
|---|---|
| `src/main.tsx` | Entry, mounts `App` |
| `src/App.tsx` | View switching only |
| `src/api/client.ts` | All HTTP, no UI |
| `src/api/runner.ts` | Local code execution/analysis, no network |
| `src/hooks/useCurriculum.ts` | Curriculum loading state |
| `src/components/Curriculum.tsx` | Track/lesson list + completion |
| `src/components/CodingLab.tsx` | Editor + local runner + server sandbox send |
| `src/components/Quiz.tsx` | Quiz load/submit UI (login required for submit) |
| `src/components/Progress.tsx` | Per-user progress list + adaptive recommendation |
| `src/components/Login.tsx` | User ID login/logout, JWT stored as `ivy-token` + `ivy-user` |
| `src/hooks/useAuth.ts` | Auth state (user/token), storage sync |
| `src/components/Library.tsx` | Library, Community (track filter), Studio (API tester) |

## Commands (run in `frontend/`)

```powershell
npm install
npm run dev      # vite, :5173
npm run build    # tsc + vite build
```

Backend URL via `.env`: `VITE_API_BASE=http://localhost:8000` (see `.env.example`).
