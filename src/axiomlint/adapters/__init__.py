"""Adapter capabilities are explicitly unavailable, not successful no-ops."""

BACKENDS = (
    "ruff", "mypy", "bandit", "semgrep", "gitleaks", "syft", "grype",
    "hypothesis", "crosshair", "z3", "cvc5", "sympy", "sage", "lean", "llm",
)


def capabilities() -> dict[str, str]:
    return {name: "NOT_IMPLEMENTED" for name in BACKENDS}

