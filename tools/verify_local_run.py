"""Verify a local gate's schema, raw logs, checksums and anti-false-green rules.

Verifying bytes is not authenticating their author or performing an S2 audit.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.evidence.store import sha256  # noqa: E402
from axiomlint.schema import InvalidRecord, load_json, validate  # noqa: E402
from local_check import command_inventory, source_identity  # noqa: E402


def verify(directory: Path, root: Path = ROOT, check_current: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        for path in (directory, *directory.parents):
            if path.is_symlink():
                raise InvalidRecord("Symlink in run directory")
        manifest_path = directory / "manifest.json"
        checksum_path = directory / "manifest.sha256"
        if manifest_path.is_symlink() or checksum_path.is_symlink():
            raise InvalidRecord("Symlink manifest/checksum")
        content = manifest_path.read_bytes()
        checksum = checksum_path.read_text(encoding="ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{64}", checksum) or sha256(content) != checksum:
            errors.append("Manifest checksum mismatch")
        manifest = load_json(manifest_path)
        validate(manifest, load_json(root / "schemas/local-run.schema.json"))
        if manifest["status"] != "PASS":
            errors.append("Run did not pass")
        if manifest["source_tree_sha256"] != manifest["source_tree_after_sha256"]:
            errors.append("Source changed during run")
        if manifest["kind"] == "ACCEPTANCE_CANDIDATE" and manifest["dirty"]:
            errors.append("Dirty acceptance candidate")
        if not re.fullmatch(r"[0-9a-f]{40}", manifest["commit"]):
            errors.append("Invalid Git source commit")
        commands = manifest["commands"]
        expected_names = [name for name, _ in command_inventory(sys.executable)]
        if [row["name"] for row in commands] != expected_names:
            raise InvalidRecord("Mandatory command inventory mismatch")
        executables = {row["argv"][0] for row in commands}
        if len(executables) != 1:
            errors.append("Commands used inconsistent Python executables")
        expected_argv = dict(command_inventory(commands[0]["argv"][0]))
        for command in commands:
            name = command["name"]
            if command["argv"] != expected_argv[name]:
                errors.append(f"{name}: command argv mismatch")
            if command["exit_code"] != 0 or command["status"] != "PASS":
                errors.append(f"{name}: unsuccessful command")
            for stream in ("stdout", "stderr"):
                path = directory / f"{name}.{stream}.log"
                if path.is_symlink() or not path.is_file():
                    raise InvalidRecord(f"{name}: missing or symlink log")
                data = path.read_bytes()
                if sha256(data) != command[f"{stream}_sha256"] or len(data) != command[f"{stream}_bytes"]:
                    errors.append(f"{name}.{stream}: digest/size mismatch")
            if name == "tests":
                output = (directory / "tests.stdout.log").read_text(encoding="utf-8")
                counts = re.findall(r"^COUNTS discovered=(\d+) executed=(\d+) skipped=(\d+)$", output, re.M)
                if len(counts) != 1:
                    errors.append("Missing/ambiguous test counts")
                else:
                    discovered, executed, skipped = map(int, counts[0])
                    if discovered <= 0 or executed != discovered or skipped >= executed:
                        errors.append("Empty, incomplete or all-skipped test execution")
        if check_current:
            commit, dirty, tree = source_identity(root)
            if (commit, dirty, tree) != (
                manifest["commit"], manifest["dirty"], manifest["source_tree_sha256"],
            ):
                errors.append("Current source does not match run identity")
    except (InvalidRecord, OSError, UnicodeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--check-current-source", action="store_true")
    args = parser.parse_args()
    problems = verify(args.directory, check_current=args.check_current_source)
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"LOCAL_EVIDENCE={'FAIL' if problems else 'PASS'}; not independent approval")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

