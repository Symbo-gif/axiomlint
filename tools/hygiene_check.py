"""Foundation hygiene, not a SAST/SCA/secret-scanning substitute."""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.schema import check_schema, load_json  # noqa: E402


def check(root: Path) -> list[str]:
    errors: list[str] = []
    forbidden = [
        root / ".github/workflows", root / ".gitlab-ci.yml",
        root / "azure-pipelines.yml", root / ".circleci/config.yml",
        root / "Jenkinsfile",
    ]
    for path in forbidden:
        if path.exists():
            errors.append(f"Hosted/pipeline configuration prohibited: {path.relative_to(root)}")
    schemas = list((root / "schemas").glob("*.schema.json"))
    if not schemas:
        errors.append("No schema files")
    for path in schemas:
        try:
            check_schema(load_json(path))
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
    # Verify simple local Markdown links. External links and code ticks are data.
    for base in ("README.md", "AGENTS.md", "docs", "governance"):
        item = root / base
        paths = item.rglob("*.md") if item.is_dir() else [item]
        for path in paths:
            if not path.exists() or "reference" in path.parts:
                continue
            content = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if "://" in target or target.startswith("#"):
                    continue
                local = target.split("#", 1)[0]
                if not (path.parent / local).exists():
                    errors.append(f"{path.relative_to(root)}: broken link {target}")
    return errors


def syntax_check(root: Path) -> int:
    count = 0
    for base in ("src", "tools", "tests", "examples"):
        for path in sorted((root / base).rglob("*.py")):
            content = path.read_text(encoding="utf-8")
            compile(ast.parse(content, filename=str(path)), str(path), "exec")
            count += 1
    print(f"Compiled {count} source files without executing them")
    return 0 if count else 1


if __name__ == "__main__":
    if "--syntax" in sys.argv:
        raise SystemExit(syntax_check(ROOT))
    problems = check(ROOT)
    for problem in problems:
        print(problem)
    print(f"Hygiene: {'FAIL' if problems else 'PASS'} (not security certification)")
    raise SystemExit(1 if problems else 0)

