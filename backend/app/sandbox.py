"""Safe code preview. Allowlisted AST evaluation only — never exec/import/user I/O."""

from __future__ import annotations

import ast
import operator

MAX_STEPS = 10_000
MAX_LOOPS = 100
MAX_PRINTS = 50
MAX_OUTPUT = 5_000

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg, ast.Not: operator.not_}
_BOOLOPS = {ast.And: all, ast.Or: any}
_CMPOPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class SandboxError(ValueError):
    pass


class _Runner:
    def __init__(self) -> None:
        self.env: dict[str, object] = {}
        self.out: list[str] = []
        self.steps = 0

    def tick(self) -> None:
        self.steps += 1
        if self.steps > MAX_STEPS:
            raise SandboxError("step budget exceeded")

    def eval_expr(self, node: ast.AST) -> object:
        self.tick()
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int | float | str | bool) or node.value is None:
                return node.value
            raise SandboxError("unsupported literal")
        if isinstance(node, ast.Name):
            if node.id in self.env:
                return self.env[node.id]
            raise SandboxError(f"unknown name {node.id!r}")
        if isinstance(node, ast.BinOp):
            op = _BINOPS.get(type(node.op))
            if op is None:
                raise SandboxError("unsupported operator")
            left = self.eval_expr(node.operand if hasattr(node, "operand") else node.left)
            right = self.eval_expr(node.right)
            if isinstance(node.op, ast.Pow):
                if isinstance(right, int) and abs(right) > 10:
                    raise SandboxError("exponent too large")
            try:
                return op(left, right)  # type: ignore[operator]
            except ZeroDivisionError:
                raise SandboxError("division by zero") from None
        if isinstance(node, ast.UnaryOp):
            op = _UNARYOPS.get(type(node.op))
            if op is None:
                raise SandboxError("unsupported operator")
            return op(self.eval_expr(node.operand))  # type: ignore[operator]
        if isinstance(node, ast.BoolOp):
            vals = [bool(self.eval_expr(v)) for v in node.values]
            fn = _BOOLOPS.get(type(node.op))
            if fn is None:
                raise SandboxError("unsupported operator")
            return fn(vals)
        if isinstance(node, ast.Compare):
            left = self.eval_expr(node.left)
            for op_node, comp in zip(node.ops, node.comparators, strict=True):
                fn = _CMPOPS.get(type(op_node))
                if fn is None:
                    raise SandboxError("unsupported comparison")
                right = self.eval_expr(comp)
                if not fn(left, right):  # type: ignore[operator]
                    return False
                left = right
            return True
        if isinstance(node, ast.IfExp):
            return (
                self.eval_expr(node.body)
                if self.eval_expr(node.test)
                else self.eval_expr(node.orelse)
            )
        if isinstance(node, ast.List | ast.Tuple):
            return [self.eval_expr(e) for e in node.elts]
        if isinstance(node, ast.Call):
            return self.eval_call(node)
        raise SandboxError(f"unsupported expression {type(node).__name__}")

    def eval_call(self, node: ast.Call) -> object:
        if not isinstance(node.func, ast.Name):
            raise SandboxError("only print/range/len/str/int/float calls allowed")
        if node.keywords:
            raise SandboxError("keyword args not allowed")
        if node.func.id == "range":
            args = [self.eval_expr(a) for a in node.args]
            if not all(isinstance(a, int) for a in args) or not 1 <= len(args) <= 3:
                raise SandboxError("range() needs 1-3 ints")
            if any(abs(a) > MAX_LOOPS for a in args if isinstance(a, int)):
                raise SandboxError("range() too large")
            return list(range(*args))  # type: ignore[arg-type]
        if node.func.id == "len":
            if len(node.args) != 1:
                raise SandboxError("len() takes one arg")
            val = self.eval_expr(node.args[0])
            if isinstance(val, list | str):
                return len(val)
            raise SandboxError("len() of unsupported type")
        if node.func.id in ("str", "int", "float"):
            if len(node.args) != 1:
                raise SandboxError(f"{node.func.id}() takes one arg")
            val = self.eval_expr(node.args[0])
            try:
                return {"str": str, "int": int, "float": float}[node.func.id](val)
            except (ValueError, TypeError):
                raise SandboxError(f"bad {node.func.id}() cast") from None
        raise SandboxError(f"call {node.func.id}() not allowed — use print() at top level")

    def do_print(self, node: ast.Call, lineno: int) -> None:
        if len(self.out) >= MAX_PRINTS:
            raise SandboxError("print limit exceeded")
        parts = []
        for a in node.args:
            if isinstance(a, ast.Starred):
                raise SandboxError("*args not allowed")
            val = self.eval_expr(a)
            parts.append(str(val))
        self.out.append(" ".join(parts))

    def exec_body(self, stmts: list[ast.stmt]) -> None:
        for stmt in stmts:
            self.exec_stmt(stmt)

    def exec_stmt(self, stmt: ast.stmt) -> None:  # noqa: C901, PLR0912
        self.tick()
        if isinstance(stmt, ast.Expr):
            if not isinstance(stmt.value, ast.Call):
                raise SandboxError("only print() calls allowed as statements")
            call = stmt.value
            if not isinstance(call.func, ast.Name) or call.func.id != "print":
                raise SandboxError("only print() allowed")
            if call.keywords:
                raise SandboxError("print() keywords not allowed")
            self.do_print(call, stmt.lineno)
        elif isinstance(stmt, ast.Assign):
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise SandboxError("simple x = ... assignments only")
            self.env[stmt.targets[0].id] = self.eval_expr(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if stmt.value is None or not isinstance(stmt.target, ast.Name):
                raise SandboxError("simple x: T = ... assignments only")
            self.env[stmt.target.id] = self.eval_expr(stmt.value)
        elif isinstance(stmt, ast.AugAssign):
            if not isinstance(stmt.target, ast.Name):
                raise SandboxError("simple x += ... only")
            op = _BINOPS.get(type(stmt.op))
            if op is None:
                raise SandboxError("unsupported operator")
            cur = self.env.get(stmt.target.id, 0)
            self.env[stmt.target.id] = op(cur, self.eval_expr(stmt.value))  # type: ignore[operator]
        elif isinstance(stmt, ast.For):
            if not isinstance(stmt.target, ast.Name):
                raise SandboxError("for x in ... only")
            if stmt.orelse:
                raise SandboxError("for/else not allowed")
            iter_val = self.eval_expr(stmt.iter)
            if not isinstance(iter_val, list):
                raise SandboxError("for loops need range()/list only")
            for i, item in enumerate(iter_val):
                if i >= MAX_LOOPS:
                    raise SandboxError("loop limit exceeded")
                self.env[stmt.target.id] = item
                self.exec_body(stmt.body)
        elif isinstance(stmt, ast.While):
            if stmt.orelse:
                raise SandboxError("while/else not allowed")
            for _ in range(MAX_LOOPS):
                if not self.eval_expr(stmt.test):
                    break
                self.exec_body(stmt.body)
            else:
                raise SandboxError("loop limit exceeded")
        elif isinstance(stmt, ast.If):
            branch = stmt.body if self.eval_expr(stmt.test) else stmt.orelse
            self.exec_body(branch)
        elif isinstance(stmt, ast.Pass):
            return
        elif isinstance(stmt, ast.Break | ast.Continue):
            raise SandboxError("break/continue outside loop context")
        else:
            raise SandboxError(f"statement {type(stmt).__name__} not allowed")


def run_python(code: str) -> dict:
    """Evaluate allowlisted Python (print/assign/range/loops). No imports, no I/O."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"language": "python", "output": f"SyntaxError: {e.msg} (line {e.lineno})"}
    runner = _Runner()
    try:
        runner.exec_body(tree.body)
    except SandboxError as e:
        note = f"Stopped: {e}"
        body = "\n".join(runner.out)
        output = f"{body}\n{note}" if body else note
        return {"language": "python", "output": output[:MAX_OUTPUT]}
    body = "\n".join(runner.out) if runner.out else "(no output — use print(...))"
    return {"language": "python", "output": body[:MAX_OUTPUT]}


def run_javascript(code: str) -> dict:
    """Static preview only — real JS runs in the browser Coding Lab."""
    logs: list[str] = []
    for line in code.splitlines():
        stripped = line.strip()
        if "console.log" in stripped:
            start = stripped.find("(")
            end = stripped.rfind(")")
            arg = stripped[start + 1 : end].strip() if start >= 0 and end > start else ""
            logs.append(arg[:200] if arg else "(empty)")
            if len(logs) >= MAX_PRINTS:
                break
    lines = len(code.splitlines())
    if logs:
        shown = "\n".join(f"log: {a}" for a in logs)
        output = (
            f"JavaScript preview: {lines} lines, {len(logs)} console.log call(s).\n"
            f"{shown}\nRun full JS in the Coding Lab (browser) — server never executes JS."
        )
    else:
        output = (
            f"JavaScript preview: {lines} lines, no console.log found.\n"
            "Add console.log(...) and run it in the Coding Lab (browser)."
        )
    return {"language": "javascript", "output": output[:MAX_OUTPUT]}


def run_rust(code: str) -> dict:
    """Static analysis only — compile with cargo locally."""
    lines = len(code.splitlines())
    has_main = "fn main" in code
    has_unsafe = "unsafe" in code
    prints = code.count("println!")
    parts = [f"Rust analysis: {lines} lines, {prints} println! call(s)."]
    parts.append("Has fn main." if has_main else "No fn main found.")
    parts.append(
        "Contains `unsafe` — review ownership rules." if has_unsafe else "No `unsafe` detected."
    )
    parts.append("Compile with `cargo run` locally or paste into the Rust Playground.")
    return {"language": "rust", "output": "\n".join(parts)[:MAX_OUTPUT]}


def run_code_for(language: str, code: str) -> dict:
    if language == "python":
        return run_python(code)
    if language == "javascript":
        return run_javascript(code)
    return run_rust(code)


class _Return(Exception):
    """Internal control flow for `return` inside interpreted lab functions."""

    def __init__(self, value: object) -> None:
        super().__init__("return")
        self.value = value


_LAB_BUILTINS = ("range", "len", "str", "int", "float", "abs", "bool")
_LAB_MAX_DEPTH = 50
_LAB_MAX_CODE = 10_000
_LAB_MAX_TEST_EXPR = 500
_LAB_MAX_TESTS = 20


class _LabRunner(_Runner):
    """Interprets user-defined functions from AST. No exec/eval/import/attribute."""

    def __init__(self) -> None:
        super().__init__()
        self.funcs: dict[str, ast.FunctionDef] = {}
        self.depth = 0

    def load(self, tree: ast.Module) -> None:
        for stmt in tree.body:
            self.tick()
            if isinstance(stmt, ast.FunctionDef):
                if not stmt.name.isidentifier() or stmt.name.startswith("_"):
                    raise SandboxError(f"bad function name {stmt.name!r}")
                if stmt.decorator_list:
                    raise SandboxError("decorators not allowed")
                if stmt.args.vararg or stmt.args.kwarg or stmt.args.kwonlyargs:
                    raise SandboxError("*args/**kwargs not allowed")
                if stmt.args.defaults or stmt.args.kw_defaults:
                    raise SandboxError("default args not allowed")
                for a in stmt.args.args:
                    if not a.arg.isidentifier() or a.arg.startswith("_"):
                        raise SandboxError(f"bad arg name {a.arg!r}")
                if stmt.name in self.funcs:
                    raise SandboxError(f"duplicate function {stmt.name!r}")
                self.funcs[stmt.name] = stmt
            elif isinstance(stmt, ast.Assign | ast.AnnAssign | ast.Pass):
                # Module-level constants allowed; reuse statement logic.
                self.exec_stmt(stmt)
            else:
                raise SandboxError(
                    f"only def/assign allowed at top level, got {type(stmt).__name__}"
                )
        if not self.funcs:
            raise SandboxError("no function defined — define the requested function")

    def exec_func_body(self, stmts: list[ast.stmt], env: dict[str, object]) -> object:
        saved = self.env
        self.env = env
        try:
            for stmt in stmts:
                self.exec_lab_stmt(stmt)
            return None
        except _Return as r:
            return r.value
        finally:
            self.env = saved

    def exec_lab_stmt(self, stmt: ast.stmt) -> None:
        self.tick()
        if isinstance(stmt, ast.Return):
            raise _Return(self.eval_expr(stmt.value) if stmt.value is not None else None)
        if isinstance(stmt, ast.Expr):
            # Allow print(...) as a no-op besides existing output cap; ignore otherwise.
            if (
                isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and stmt.value.func.id == "print"
            ):
                if len(self.out) < MAX_PRINTS:
                    self.do_print(stmt.value, stmt.lineno)
                return
            raise SandboxError("expression statements not allowed in functions")
        if isinstance(stmt, ast.If | ast.For | ast.While):
            self.exec_lab_block(stmt)
            return
        # Assign / AugAssign / Pass share logic with the print-runner.
        self.exec_stmt(stmt)

    def exec_lab_block(self, stmt: ast.If | ast.For | ast.While) -> None:
        if isinstance(stmt, ast.If):
            branch = stmt.body if self.eval_expr(stmt.test) else stmt.orelse
            for s in branch:
                self.exec_lab_stmt(s)
            return
        if isinstance(stmt, ast.For):
            if not isinstance(stmt.target, ast.Name):
                raise SandboxError("for x in ... only")
            if stmt.orelse:
                raise SandboxError("for/else not allowed")
            iter_val = self.eval_expr(stmt.iter)
            if not isinstance(iter_val, list | str):
                raise SandboxError("for loops need range()/list/str only")
            for i, item in enumerate(iter_val):
                if i >= MAX_LOOPS:
                    raise SandboxError("loop limit exceeded")
                self.env[stmt.target.id] = item
                for s in stmt.body:
                    self.exec_lab_stmt(s)
            return
        if stmt.orelse:
            raise SandboxError("while/else not allowed")
        for _ in range(MAX_LOOPS):
            if not self.eval_expr(stmt.test):
                break
            for s in stmt.body:
                self.exec_lab_stmt(s)
        else:
            raise SandboxError("loop limit exceeded")

    def eval_expr(self, node: ast.AST) -> object:  # noqa: C901, PLR0912
        self.tick()
        if isinstance(node, ast.Subscript):
            target = self.eval_expr(node.value)
            sl = node.slice
            if isinstance(sl, ast.Slice):
                lo = self.eval_expr(sl.lower) if sl.lower else None
                hi = self.eval_expr(sl.upper) if sl.upper else None
                st = self.eval_expr(sl.step) if sl.step else None
                for v in (lo, hi, st):
                    if v is not None and not isinstance(v, int):
                        raise SandboxError("slice indices must be ints")
                    if isinstance(v, int) and abs(v) > MAX_LOOPS:
                        raise SandboxError("slice index too large")
                try:
                    if isinstance(target, list | str):
                        return target[slice(lo, hi, st)]
                except (IndexError, ValueError):
                    raise SandboxError("slice out of range") from None
                raise SandboxError("slicing lists/strings only")
            idx = self.eval_expr(sl)
            if not isinstance(idx, int) or abs(idx) > MAX_LOOPS:
                raise SandboxError("index must be a small int")
            try:
                if isinstance(target, list | str):
                    return target[idx]
            except IndexError:
                raise SandboxError("index out of range") from None
            raise SandboxError("indexing lists/strings only")
        if isinstance(node, ast.Dict):
            return {
                self.eval_expr(k): self.eval_expr(v)
                for k, v in zip(node.keys, node.values, strict=True)
                if k is not None
            }
        if isinstance(node, ast.Call):
            return self.eval_lab_call(node)
        return super().eval_expr(node)

    def eval_lab_call(self, node: ast.Call) -> object:
        if not isinstance(node.func, ast.Name):
            raise SandboxError("method/attribute calls not allowed")
        if node.keywords:
            raise SandboxError("keyword args not allowed")
        name = node.func.id
        if name in self.funcs:
            if self.depth >= _LAB_MAX_DEPTH:
                raise SandboxError("recursion limit exceeded")
            fn = self.funcs[name]
            params = [a.arg for a in fn.args.args]
            if len(node.args) != len(params):
                raise SandboxError(f"{name}() takes {len(params)} args")
            args = [self.eval_expr(a) for a in node.args]
            self.depth += 1
            try:
                return self.exec_func_body(list(fn.body), dict(zip(params, args, strict=True)))
            finally:
                self.depth -= 1
        if name in _LAB_BUILTINS:
            if name == "abs":
                if len(node.args) != 1:
                    raise SandboxError("abs() takes one arg")
                val = self.eval_expr(node.args[0])
                if not isinstance(val, int | float):
                    raise SandboxError("abs() of unsupported type")
                return abs(val)
            if name == "bool":
                if len(node.args) != 1:
                    raise SandboxError("bool() takes one arg")
                return bool(self.eval_expr(node.args[0]))
            return self.eval_call(node)
        raise SandboxError(f"call {name}() not allowed")


def run_lab(code: str, test_cases: list[dict]) -> dict:
    """Safely run lab test cases against user code. AST-interpreted, never exec.

    Returns {"ok": True, "results": [...]} or {"ok": False, "error": ...}.
    Per-test failures are reported inside results with passed=False.
    """
    if len(code) > _LAB_MAX_CODE:
        return {"ok": False, "error": "code too large (max 10000 chars)"}
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"ok": False, "error": f"SyntaxError: {e.msg} (line {e.lineno})"}
    runner = _LabRunner()
    try:
        runner.load(tree)
    except SandboxError as e:
        return {"ok": False, "error": f"Stopped: {e}"}
    results: list[dict] = []
    for test in test_cases[:_LAB_MAX_TESTS]:
        expr = test["input"]
        expected = test["expected"]
        if not isinstance(expr, str) or len(expr) > _LAB_MAX_TEST_EXPR:
            results.append(
                {
                    "input": str(expr)[:100],
                    "expected": expected,
                    "passed": False,
                    "error": "bad test: expression too large",
                }
            )
            continue
        try:
            test_tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            results.append(
                {
                    "input": expr,
                    "expected": expected,
                    "passed": False,
                    "error": f"bad test: {e.msg}",
                }
            )
            continue
        try:
            actual = runner.eval_expr(test_tree.body)
        except SandboxError as e:
            results.append(
                {"input": expr, "expected": expected, "passed": False, "error": f"Stopped: {e}"}
            )
            continue
        except Exception as e:  # noqa: BLE001 — surface logic errors as test failures
            err = f"{type(e).__name__}: {e}"[:500]
            results.append(
                {"input": expr, "expected": expected, "passed": False, "error": err}
            )
            continue
        # Equality with one exception: int/float interchange (4 == 4.0).
        # Bools stay strict since isinstance(True, int) is True in Python.
        if isinstance(expected, bool) or isinstance(actual, bool):
            passed = type(actual) is type(expected) and actual == expected
        elif isinstance(expected, int | float) and isinstance(actual, int | float):
            passed = actual == expected
        else:
            passed = type(actual) is type(expected) and actual == expected
        entry: dict = {"input": expr, "expected": expected, "passed": passed, "actual": actual}
        try:
            import json as _json

            _json.dumps(entry)
        except (TypeError, ValueError):
            entry["actual"] = str(actual)[:500]
        results.append(entry)
    return {"ok": True, "results": results}
