"""Sandbox unit tests: allowlist stays closed, budgets hold."""

from app.sandbox import run_code_for


def test_pow_capped():
    out = run_code_for("python", "print(2 ** 100)")["output"]
    assert "Stopped" in out


def test_unknown_name_blocked():
    out = run_code_for("python", "print(secret)")["output"]
    assert "Stopped" in out


def test_dunder_blocked():
    out = run_code_for("python", "print(__import__('os'))")["output"]
    assert "Stopped" in out


def test_syntax_reported():
    out = run_code_for("python", "print(")["output"]
    assert "SyntaxError" in out


def test_while_loop_runs():
    out = run_code_for("python", "i = 0\nwhile i < 3:\n    print(i)\n    i = i + 1")["output"]
    assert out == "0\n1\n2"


def test_infinite_loop_capped():
    out = run_code_for("python", "while True:\n    print(1)")["output"]
    assert "Stopped" in out
