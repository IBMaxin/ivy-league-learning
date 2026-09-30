# Coding Labs

Server-graded function-writing challenges (`py-101`, `algs-101`, `ds-101`).
Unlike `/api/code/run` (print-preview), labs validate that learner-defined
functions return the right values — and every attempt is recorded as progress,
so labs feed mastery and adaptive recommendations exactly like quizzes.

## API contract (auth required)

Mint a token first (`POST /api/auth/token` with `{"user_id": "..."}`),
then send `Authorization: Bearer <jwt>` on both calls.

```powershell
# Fetch a challenge (prompt + test inputs, no solutions to leak)
Invoke-RestMethod -Headers @{Authorization="Bearer $t"} `
  -Uri http://localhost:8000/api/lab/py-101

# Submit code (user_id comes from the token, never the body)
Invoke-RestMethod -Method Post -Headers @{Authorization="Bearer $t"} `
  -ContentType 'application/json' -Uri http://localhost:8000/api/lab/submit `
  -Body '{"lesson_id":"py-101","code":"def square(n):\n    return n * n\n"}'
```

| Call | Success | Errors |
|---|---|---|
| `GET /api/lab/{lesson_id}` | `200 {lesson_id, prompt, test_cases[]}` | `401` no/bad token, `400` bad id, `404` unknown lab |
| `POST /api/lab/submit` | `200 {success, score, correct, total, results[]}` | `401` no/bad token, `400` bad id, `404` unknown lab, `422` bad shape/oversize |

`score` is `round(correct / total * 100, 1)`; `success` means every test
passed. Definition failures (syntax errors, blocked constructs) score `0.0`
with `results: []` and an `error` string — still `200`, still recorded.
`results[]` entries carry `{input, expected, actual?, passed, error?}`.

## Safety model

User code is **interpreted from its AST, never `exec`'d** (`sandbox.run_lab`).
Allowed: `def` with positional args, `return`, assignment, `if`/`for`/`while`
(capped at 100 iterations), indexing/slicing of lists and strings, and calls
to `range`/`len`/`str`/`int`/`float`/`abs`/`bool` plus your own defined
functions (recursion depth 50). Rejected: imports, `eval`/`exec`/`open`,
lambdas, decorators, default/`*args`, attribute or method calls
(`s.lower()`, `n.__class__`, …), comprehensions, globals.

Budgets: code ≤ 10,000 chars, 10,000 interpreter steps, test expressions
≤ 500 chars, at most 20 cases per lab. Exceeding a budget fails the affected
test (or the submission for definition-phase violations) — the server never
runs anything outside the interpreter.

## Authoring a lab (`backend/app/content.py`)

```python
"my-101": {
    "prompt": "Write `double_all(xs)` that returns …",
    "test_cases": [
        {"input": "double_all([1, 2])", "expected": [2, 4]},
    ],
},
```

Rules:

1. Test `input` must be a single expression calling the requested function;
   keep each under 500 chars and the list at 20 or fewer.
2. `expected` values must be JSON-serializable (`int`/`float`/`str`/`bool`/
   `list`) — results are compared strictly, except `int`/`float` interchange
   (`4 == 4.0` passes; `True == 1` does not).
3. Write solutions using only the allowed subset above — if your reference
   solution needs a method call or comprehension, learners can't use it either.
4. Add the lesson id to a track's `lessons` so it appears in `/api/curriculum`,
   and mirror the scoring expectation in `rust-core` (`score_lab`) only if the
   offline demos need it — execution itself stays Python-side by design.

## Layer map

| Concern | Owner |
|---|---|
| Fixtures | `content.LABS` (static data) |
| Shape validation | `models.LabSubmit` (`lesson_id` 1–64 chars, `code` 1–10,000 chars, no extras) |
| Execution | `sandbox.run_lab` (AST only) |
| Scoring | `services.validate_lab` (pure; mirrors `grade_quiz` rounding) |
| HTTP + persistence | `routers/lab.py` (status codes, `repos.add_progress` for the token caller) |
| Offline scoring math | `rust-core` `mastery.score_lab` (pass-flag math only) |
| UI | `CodingLab.tsx` (challenges) + `ivy-full.html` lab section (demo token flow) |

Tests mirror the layers: `test_lab_sandbox.py` (execution, no HTTP),
`test_lab_services.py` (scoring, no HTTP), `test_lab_models.py`
(validation, no HTTP), `test_lab_router.py` (HTTP shape/auth/status only).
