import argparse
import json
import sys
from pathlib import Path

from axiomlint.adapters import capabilities
from axiomlint.governance import check
from axiomlint.intake.static import inventory
from axiomlint.schema import InvalidRecord, load_json, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AxiomLint governed local foundation")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Report capabilities, never assurance")
    gov = commands.add_parser("governance")
    gov.add_argument("action", choices=["check"])
    gov.add_argument("--root", type=Path, default=Path("."))
    inv = commands.add_parser("inventory", help="Trusted-input static inventory, not a review")
    inv.add_argument("path", type=Path)
    val = commands.add_parser("validate", help="Validate supported foundation schema vocabulary")
    val.add_argument("record", type=Path)
    val.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps({
                "phase": "FOUNDATION", "hosted_ci": "PROHIBITED",
                "subject_execution": "DISABLED", "backends": capabilities(),
            }, indent=2, sort_keys=True))
        elif args.command == "governance":
            errors = check(args.root.resolve())
            print(json.dumps({"structural_check": "FAIL" if errors else "PASS", "errors": errors,
                              "approval_or_closure": False}, indent=2))
            return 1 if errors else 0
        elif args.command == "inventory":
            report = inventory(args.path)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2 if report["diagnostics"] else 0
        else:
            validate(load_json(args.record), load_json(args.schema))
            print("VALID: foundation vocabulary only; semantic acceptance not implied")
        return 0
    except (InvalidRecord, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

