"""Static learning content. Links only, no copied course material."""

from __future__ import annotations

TRACKS: list[dict] = [
    {
        "id": "cs-fundamentals",
        "title": "Computer Science Fundamentals",
        "level": "beginner",
        "description": "Foundations: Python, JS, Rust.",
        "lessons": [
            {
                "id": "py-101",
                "title": "Python Basics",
                "language": "python",
                "duration_min": 45,
                "objectives": ["variables", "loops", "functions"],
                "source": "See /api/library entries for open links",
            },
            {
                "id": "rust-101",
                "title": "Rust Basics",
                "language": "rust",
                "duration_min": 60,
                "objectives": ["ownership", "mutability", "cargo"],
                "source": "The Rust Book (open)",
            },
            {
                "id": "js-101",
                "title": "JS Basics",
                "language": "javascript",
                "duration_min": 45,
                "objectives": ["types", "functions", "JSON"],
                "source": "MDN Web Docs (open)",
            },
        ],
    },
    {
        "id": "fullstack",
        "title": "Full-Stack Development",
        "level": "intermediate",
        "description": "FastAPI + React studio with guided projects.",
        "lessons": [
            {
                "id": "api-101",
                "title": "FastAPI Intro",
                "language": "python",
                "duration_min": 60,
                "objectives": ["routes", "validation", "auth"],
                "source": "FastAPI docs (open)",
            },
            {
                "id": "react-101",
                "title": "React + TypeScript",
                "language": "javascript",
                "duration_min": 60,
                "objectives": ["components", "hooks", "fetch"],
                "source": "React + MDN (open)",
            },
        ],
    },
]

LESSON_ORDER: list[dict] = [
    {"id": "py-101", "track": "cs-fundamentals", "title": "Python Basics"},
    {"id": "js-101", "track": "cs-fundamentals", "title": "JS Basics"},
    {"id": "rust-101", "track": "cs-fundamentals", "title": "Rust Basics"},
    {"id": "api-101", "track": "fullstack", "title": "FastAPI Intro"},
    {"id": "react-101", "track": "fullstack", "title": "React + TypeScript"},
]

LIBRARY: list[dict] = [
    {
        "id": "cs50",
        "title": "CS50: Introduction to Computer Science",
        "university": "Harvard",
        "type": "course",
        "level": "beginner",
        "url": "https://cs50.harvard.edu/x/",
    },
    {
        "id": "mit-60001",
        "title": "Intro to CS and Programming in Python",
        "university": "MIT OCW",
        "type": "course",
        "level": "beginner",
        "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",  # noqa: E501
    },
    {
        "id": "yale-oyc",
        "title": "Open Yale Courses",
        "university": "Yale",
        "type": "collection",
        "level": "all",
        "url": "https://oyc.yale.edu/",
    },
    {
        "id": "stanford-online",
        "title": "Stanford Online",
        "university": "Stanford",
        "type": "collection",
        "level": "all",
        "url": "https://online.stanford.edu/",
    },
    {
        "id": "princeton-algs",
        "title": "Algorithms, Part I",
        "university": "Princeton",
        "type": "course",
        "level": "intermediate",
        "url": "https://www.coursera.org/learn/algorithms-part1",
    },
    {
        "id": "rust-book",
        "title": "The Rust Programming Language",
        "university": "Open (Rust Project)",
        "type": "book",
        "level": "beginner",
        "url": "https://doc.rust-lang.org/book/",
    },
    {
        "id": "mdn-web",
        "title": "MDN Web Docs",
        "university": "Open (Mozilla)",
        "type": "reference",
        "level": "all",
        "url": "https://developer.mozilla.org/",
    },
    {
        "id": "fastapi-docs",
        "title": "FastAPI Documentation",
        "university": "Open",
        "type": "reference",
        "level": "intermediate",
        "url": "https://fastapi.tiangolo.com/",
    },
    {
        "id": "mit-6006",
        "title": "Introduction to Algorithms",
        "university": "MIT OCW",
        "type": "course",
        "level": "intermediate",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/",
    },
    {
        "id": "harvard-open",
        "title": "Harvard Online Learning",
        "university": "Harvard / Open",
        "type": "collection",
        "level": "all",
        "url": "https://online-learning.harvard.edu/",
    },
    {
        "id": "yale-finmarkets",
        "title": "Financial Markets",
        "university": "Yale",
        "type": "course",
        "level": "beginner",
        "url": "https://oyc.yale.edu/economics/econ-252-11",
    },
    {
        "id": "python-docs",
        "title": "Python Tutorial",
        "university": "Open (Python Software Foundation)",
        "type": "reference",
        "level": "beginner",
        "url": "https://docs.python.org/3/tutorial/",
    },
]


def _qa(q: str, choices: list[str], answer: int) -> dict:
    return {"q": q, "choices": choices, "answer": answer}


QUIZZES: dict[str, list[dict]] = {
    "py-101": [
        _qa("What does print(2 + 3 * 2) output?", ["10", "8", "12", "7"], 1),
        _qa(
            "Which keyword defines a function in Python?",
            ["func", "def", "function", "lambda-only"],
            1,
        ),
        _qa("What is the type of [] in Python?", ["dict", "tuple", "list", "set"], 2),
    ],
    "js-101": [
        _qa(
            "What does '2' + 2 evaluate to in JavaScript?",
            ["4", "'22'", "NaN", "TypeError"],
            1,
        ),
        _qa(
            "Which keyword declares a block-scoped variable?",
            ["var", "let", "def", "dim"],
            1,
        ),
        _qa("JSON.parse('{\"a\":1}').a equals…", ["1", "'1'", "undefined", "null"], 0),
    ],
    "rust-101": [
        _qa(
            "By default, variables in Rust are…",
            ["mutable", "immutable", "global", "dynamic"],
            1,
        ),
        _qa(
            "Which keyword makes a variable mutable?",
            ["mut", "letmut", "var", "mutable"],
            0,
        ),
        _qa(
            "What does cargo do?",
            ["formats disks", "builds/manages Rust projects", "runs SQL", "edits video"],
            1,
        ),
    ],
    "api-101": [
        _qa(
            "FastAPI is a framework for…",
            ["databases only", "building APIs in Python", "CSS styling", "mobile apps"],
            1,
        ),
        _qa(
            "Which library validates FastAPI request bodies?",
            ["Pydantic", "NumPy", "Pandas", "Requests"],
            0,
        ),
        _qa(
            "HTTP 201 means…",
            ["redirect", "server error", "created", "unauthorized"],
            2,
        ),
    ],
    "react-101": [
        _qa(
            "React components return…",
            ["SQL", "UI descriptions (JSX/elements)", "binary", "CSS files only"],
            1,
        ),
        _qa(
            "useState is a…",
            ["router", "hook for local state", "build tool", "test runner"],
            1,
        ),
        _qa(
            "Keys in a list help React…",
            ["encrypt data", "identify items efficiently", "style pages", "fetch APIs"],
            1,
        ),
    ],
}
