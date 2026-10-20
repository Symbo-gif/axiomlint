"""Local-only source-bound development gate; no hosted operations or resolvers.

Executes trusted repository tooling/tests. It is not a hostile-code sandbox.
"""

import argparse
import hashlib
import os
import platform
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.evidence.store import canonical_json, sha256  # noqa: E402
from axiomlint.schema import load_json, validate  # noqa: E402


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def source_identity(root: Path) -> tuple[str, bool, str]:
    commit = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    if git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root.resolve()):
        raise ValueError("Project root must be its own Git worktree")
    dirty = bool(git(root, "status", "--porcelain=v1", "--untracked-files=all"))
    names = sorted(set(git(root, "ls-files", "-c", "-o", "--exclude-standard", "-z").split(b"\0")) - {b""})
    if not names:
        raise ValueError("No source files")
    digest = hashlib.sha256()
    for name in names:
        path = root / os.fsdecode(name)
        if path.is_symlink():
            raise ValueError(f"Source symlink prohibited: {name!r}")
        if not path.is_file():
            raise ValueError(f"Source missing/nonregular: {name!r}")
        # Git source mode tracks user-executable status, not umask-dependent read/write bits.
        # Full host access permissions belong to environment/security evidence, not source identity.
        content = path.read_bytes()
        mode = 0o100755 if path.stat().st_mode & 0o100 else 0o100644
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(mode.to_bytes(4, "big"))
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(hashlib.sha256(content).digest())
    return commit, dirty, digest.hexdigest()


def child_environment(root: Path) -> dict[str, str]:
    # No HOME, token, credential, proxy, API key or model endpoint inheritance.
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8", "TZ": "UTC", "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(root / "src"),
    }


def command_inventory(python: str) -> list[tuple[str, list[str]]]:
    return [
        ("governance", [python, "-m", "axiomlint", "governance", "check", "--root", "."]),
        ("hygiene", [python, "tools/hygiene_check.py"]),
        ("syntax", [python, "tools/hygiene_check.py", "--syntax"]),
        ("tests", [python, "tools/run_tests.py"]),
    ]


def invoke(name: str, argv: list[str], root: Path, directory: Path | None,
           timeout: float = 120) -> dict:
    started = time.monotonic()
    try:
        result = subprocess.run(
            argv, cwd=root, env=child_environment(root), capture_output=True,
            timeout=timeout, check=False,
        )
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
        status = "PASS" if code == 0 else "FAIL"
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b"", exc.stderr or b"", 124
        status = "TIMEOUT"
    except OSError as exc:
        stdout, stderr, code = b"", str(exc).encode(), 127
        status = "ERROR"
    elapsed = time.monotonic() - started
    if directory is not None:
        (directory / f"{name}.stdout.log").write_bytes(stdout)
        (directory / f"{name}.stderr.log").write_bytes(stderr)
    print(f"{name}: {status} exit={code} ({elapsed:.3f}s)")
    # Relay raw outputs so the local operator sees failures and actual test counts.
    if stdout:
        print(stdout.decode("utf-8", errors="replace"), end="")
    if stderr:
        print(stderr.decode("utf-8", errors="replace"), end="", file=sys.stderr)
    return {
        "name": name, "argv": argv, "exit_code": code, "status": status,
        "wall_seconds": elapsed, "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr), "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--no-record", action="store_true", help="Development only, no acceptance")
    args = parser.parse_args(argv)
    if args.require_clean and args.no_record:
        parser.error("Acceptance candidate must retain a run record")
    started = datetime.now(timezone.utc).isoformat()
    try:
        commit, dirty, tree = source_identity(ROOT)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FAIL: cannot establish source identity: {exc}", file=sys.stderr)
        return 1
    if args.require_clean and dirty:
        print("FAIL: acceptance requires clean Git worktree", file=sys.stderr)
        return 1
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12]
    directory = None if args.no_record else ROOT / "artifacts" / "gates" / run_id
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=False)
    commands = [
        invoke(name, command, ROOT, directory)
        for name, command in command_inventory(sys.executable)
    ]
    try:
        after_commit, after_dirty, after_tree = source_identity(ROOT)
        unchanged = (commit, dirty, tree) == (after_commit, after_dirty, after_tree)
    except (OSError, ValueError, subprocess.SubprocessError):
        after_tree, unchanged = "0" * 64, False
    passed = unchanged and all(command["status"] == "PASS" for command in commands)
    schema_path = ROOT / "schemas/local-run.schema.json"
    schema_bytes = schema_path.read_bytes()
    manifest = {
        "schema_version": "0.2", "run_id": run_id,
        "source_identity_algorithm": "sha256-path-bytes-gitmode-v1",
        "manifest_schema_sha256": sha256(schema_bytes),
        "kind": "ACCEPTANCE_CANDIDATE" if args.require_clean else "DEVELOPMENT",
        "status": "PASS" if passed else "FAIL", "commit": commit, "dirty": dirty,
        "source_tree_sha256": tree, "source_tree_after_sha256": after_tree,
        "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "environment_policy": "ALLOWLIST_NO_CREDENTIALS", "started_utc": started,
        "commands": commands,
        "limitations": [
            "Not independent S2, maintainer approval, package closure or security certification",
            "Trusted repository tests only; no subject-code sandbox or memory/PID/output isolation",
            "No hosted checks, network clients, dependency resolvers or model/solver calls invoked",
            "Child allowlist is hygiene, not enforcement preventing trusted tests from networking",
            "Ruff/mypy/coverage/SCA/SBOM/Nix/OCI/Windows/formal backends deferred",
            "Local unsigned digests do not provide authenticated malicious-host protection",
        ],
    }
    validate(manifest, load_json(schema_path))
    if directory is not None:
        content = canonical_json(manifest)
        (directory / "manifest.json").write_bytes(content)
        (directory / "manifest.schema.json").write_bytes(schema_bytes)
        (directory / "manifest.sha256").write_text(sha256(content) + "\n", encoding="ascii")
        print(f"RUN_DIRECTORY={directory}")
        print(f"MANIFEST_SHA256={sha256(content)}")
    print(f"LOCAL_GATE={'PASS' if passed else 'FAIL'} source_unchanged={unchanged} commit={commit} dirty={dirty}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
