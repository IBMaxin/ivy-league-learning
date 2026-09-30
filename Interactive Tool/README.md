# Interactive Tool

Zero-install single-file apps. Double-click to open in a browser.

| File | Concern |
|---|---|
| `ivy-demo.html` | Minimal demo: curriculum, JS lab, one quiz, links |
| `ivy-full.html` | Full offline app: dashboard + adaptive engine, coding lab + validated challenges (via live backend), studio, 14 quizzes, searchable library, community board |

State persists in `localStorage` (`ivy-scores`, `ivy-posts`, `ivy-done`).
The Studio backend tester and the Coding Lab validated challenges expect the
FastAPI backend at `http://localhost:8000` but everything else works fully offline.
