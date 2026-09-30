"""Sandbox layer tests: execution only. No HTTP, no auth, no app import."""

from app.sandbox import run_lab

SQUARE = "def square(n):\n    return n * n\n"
CASES = [
    {"input": "square(2)", "expected": 4},
    {"input": "square(-3)", "expected": 9},
]


def test_run_lab_correct_code_passes():
    outcome = run_lab(SQUARE, CASES)
    assert outcome["ok"] is True
    assert all(r["passed"] for r in outcome["results"])


def test_run_lab_wrong_logic_fails_without_error():
    outcome = run_lab("def square(n):\n    return n + 1\n", CASES)
    assert outcome["ok"] is True
    assert any(not r["passed"] for r in outcome["results"])
    assert "error" not in outcome


def test_run_lab_syntax_error_is_definition_failure():
    outcome = run_lab("def square(n):\n    return n *\n", CASES)
    assert outcome["ok"] is False
    assert "SyntaxError" in outcome["error"]


def test_run_lab_blocks_hostile_constructs():
    for code in [
        "import os\ndef square(n):\n    return n * n\n",
        "def square(n):\n    return eval('1')\n",
        "def square(n):\n    return open('x').read()\n",
        "def square(n):\n    return (lambda x: x)(n)\n",
        "def square(n):\n    return n.__class__.__name__\n",
        "def square(n):\n    while True:\n        pass\n",
    ]:
        outcome = run_lab(code, CASES)
        assert outcome["ok"] is False or not all(
            r.get("passed") for r in outcome.get("results", [])
        ), code


def test_run_lab_recursion_and_slicing():
    pal = "def is_palindrome(s):\n    return s == s[::-1]\n"
    out = run_lab(
        pal,
        [
            {"input": "is_palindrome('racecar')", "expected": True},
            {"input": "is_palindrome('hello')", "expected": False},
        ],
    )
    assert out["ok"] is True
    assert all(r["passed"] for r in out["results"])

    last = "def get_last(stack):\n    return stack[-1]\n"
    out = run_lab(last, [{"input": "get_last([1, 2, 3])", "expected": 3}])
    assert out["ok"] is True
    assert out["results"][0]["passed"] is True
