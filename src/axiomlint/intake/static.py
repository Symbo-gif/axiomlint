"""Bounded static inventory for maintainer-controlled local inputs only."""

import ast
import os
import stat
from pathlib import Path
from typing import Any

MAX_SOURCE_BYTES = 65_536


def inventory(path: Path) -> dict[str, Any]:
    """No source execution; not a hostile-input resource-isolated parser."""
    from axiomlint.evidence.store import sha256

    # O_NOFOLLOW rejects the final symlink. Parent directories must be trusted.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Only regular files are accepted")
        source = stream.read(MAX_SOURCE_BYTES + 1)
    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds foundation parser byte limit")
    report: dict[str, Any] = {
        "mode": "STATIC_INVENTORY", "source_sha256": sha256(source),
        "execution": "DISABLED", "verdict": "NOT_REVIEWED",
        "correspondence": "UNSUPPORTED", "functions": [], "diagnostics": [],
    }
    try:
        tree = ast.parse(source.decode("utf-8"), filename=str(path))
        # Compile AST to check scope validity; this creates a code object but never runs it.
        compile(tree, str(path), "exec")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        report["diagnostics"].append({"kind": "PARSE_ERROR", "message": str(exc)})
        return report
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            report["functions"].append({
                "name": node.name, "line": node.lineno, "end_line": node.end_lineno,
                "annotated_return": node.returns is not None,
                "async": isinstance(node, ast.AsyncFunctionDef),
            })
    return report

