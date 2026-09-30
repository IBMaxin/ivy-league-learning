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
    {
        "id": "maths",
        "title": "Mathematics",
        "level": "beginner",
        "description": "Algebra and statistics foundations.",
        "lessons": [
            {
                "id": "maths-101",
                "title": "Algebra Basics",
                "language": "python",
                "duration_min": 45,
                "objectives": ["equations", "functions", "graphs"],
                "source": "See /api/library entries for open links",
            },
            {
                "id": "stats-101",
                "title": "Statistics Basics",
                "language": "python",
                "duration_min": 45,
                "objectives": ["mean", "distributions", "sampling"],
                "source": "See /api/library entries for open links",
            },
        ],
    },
    {
        "id": "humanities",
        "title": "Humanities",
        "level": "beginner",
        "description": "Critical reading and academic writing.",
        "lessons": [
            {
                "id": "hum-101",
                "title": "Critical Reading",
                "language": "javascript",
                "duration_min": 45,
                "objectives": ["thesis", "evidence", "context"],
                "source": "See /api/library entries for open links",
            },
            {
                "id": "writing-101",
                "title": "Academic Writing",
                "language": "javascript",
                "duration_min": 45,
                "objectives": ["structure", "citation", "revision"],
                "source": "See /api/library entries for open links",
            },
        ],
    },
    {
        "id": "algorithms",
        "title": "Algorithms & Data Structures",
        "level": "intermediate",
        "description": "Complexity, sorting, and core data structures.",
        "lessons": [
            {
                "id": "algs-101",
                "title": "Algorithm Complexity & Sorting",
                "language": "python",
                "duration_min": 60,
                "objectives": ["big-o", "sorting", "search"],
                "source": "See /api/library entries for open links",
            },
            {
                "id": "ds-101",
                "title": "Data Structures",
                "language": "python",
                "duration_min": 60,
                "objectives": ["arrays", "hash-maps", "queues-stacks"],
                "source": "See /api/library entries for open links",
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
    {"id": "maths-101", "track": "maths", "title": "Algebra Basics"},
    {"id": "stats-101", "track": "maths", "title": "Statistics Basics"},
    {"id": "hum-101", "track": "humanities", "title": "Critical Reading"},
    {"id": "writing-101", "track": "humanities", "title": "Academic Writing"},
    {"id": "algs-101", "track": "algorithms", "title": "Algorithm Complexity & Sorting"},
    {"id": "ds-101", "track": "algorithms", "title": "Data Structures"},
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
    {
        "id": "khan-algebra",
        "title": "Algebra 1",
        "university": "Khan Academy (Open)",
        "type": "course",
        "level": "beginner",
        "url": "https://www.khanacademy.org/math/algebra",
    },
    {
        "id": "khan-stats",
        "title": "Statistics and Probability",
        "university": "Khan Academy (Open)",
        "type": "course",
        "level": "beginner",
        "url": "https://www.khanacademy.org/math/statistics-probability",
    },
    {
        "id": "gutenberg",
        "title": "Project Gutenberg Ebooks",
        "university": "Open (Public Domain)",
        "type": "collection",
        "level": "all",
        "url": "https://www.gutenberg.org/",
    },
    {
        "id": "visualgo",
        "title": "Visualising Data Structures and Algorithms",
        "university": "Open (National University of Singapore)",
        "type": "interactive",
        "level": "intermediate",
        "url": "https://visualgo.net/",
    },
    {
        "id": "khan-algorithms",
        "title": "Algorithms",
        "university": "Khan Academy (Open)",
        "type": "course",
        "level": "intermediate",
        "url": "https://www.khanacademy.org/computing/computer-science/algorithms",
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
    "maths-101": [
        _qa("Solve for x: 2x + 3 = 11.", ["x = 2", "x = 4", "x = 5", "x = 8"], 1),
        _qa(
            "Which is a function?",
            ["x² + y² = 1", "y = 2x + 1", "x = 5", "|x| + |y| = 1"],
            1,
        ),
        _qa("Slope of y = 3x − 2 is…", ["2", "3", "−2", "0"], 1),
    ],
    "stats-101": [
        _qa("Mean of [2, 4, 6] is…", ["3", "4", "5", "6"], 1),
        _qa(
            "A random sample should be…",
            ["hand-picked", "representative", "largest first", "sorted"],
            1,
        ),
        _qa(
            "Which plot shows distribution shape?",
            ["pie chart", "histogram", "timeline", "org chart"],
            1,
        ),
    ],
    "hum-101": [
        _qa(
            "A thesis statement should…",
            ["list facts", "make a claim", "ask no question", "summarize the ending"],
            1,
        ),
        _qa(
            "Strong evidence is…",
            ["anecdote only", "relevant and sourced", "longest quote", "first result"],
            1,
        ),
        _qa(
            "Context in analysis means…",
            ["word count", "historical/cultural background", "font choice", "page size"],
            1,
        ),
    ],
    "writing-101": [
        _qa(
            "An academic paragraph usually has…",
            ["one idea, structured", "five topics", "no evidence", "only quotes"],
            0,
        ),
        _qa(
            "Citations exist to…",
            ["pad length", "credit sources", "hide ideas", "avoid conclusions"],
            1,
        ),
        _qa(
            "Revision focuses on…",
            ["fonts first", "ideas, structure, clarity", "file names", "word count only"],
            1,
        ),
    ],
    "algs-101": [
        _qa(
            "Big-O of linear search over n items is…",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            2,
        ),
        _qa(
            "Which sort averages O(n log n)?",
            ["bubble sort", "insertion sort", "merge sort", "selection sort"],
            2,
        ),
        _qa(
            "O(log n) time typically comes from…",
            ["scanning every item", "halving the problem", "nested loops", "random sampling"],
            1,
        ),
    ],
    "ds-101": [
        _qa(
            "Hash map lookup averages…",
            ["O(1)", "O(n)", "O(log n)", "O(n²)"],
            0,
        ),
        _qa(
            "A stack is…",
            ["FIFO", "LIFO", "sorted", "random"],
            1,
        ),
        _qa(
            "Array index access by position is…",
            ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            0,
        ),
    ],
}
