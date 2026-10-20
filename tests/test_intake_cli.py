import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from axiomlint.adapters import capabilities
from axiomlint.cli import main
from axiomlint.intake.static import MAX_SOURCE_BYTES, inventory
from axiomlint.runner import ExecutionDisabled, execute_subject


class IntakeAndCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "subject.py"

    def tearDown(self):
        self.tmp.cleanup()

    def test_static_function_locations(self):
        self.source.write_text("def add(x: int, y: int) -> int:\n    return x + y\n")
        result = inventory(self.source)
        self.assertEqual(result["functions"][0]["name"], "add")
        self.assertEqual(result["functions"][0]["line"], 1)
        self.assertEqual(result["verdict"], "NOT_REVIEWED")
        self.assertEqual(result["execution"], "DISABLED")

    def test_top_level_source_is_never_executed(self):
        marker = self.root / "would-have-run"
        self.source.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
            "def f(x: int) -> int:\n    return x\n"
        )
        inventory(self.source)
        self.assertFalse(marker.exists())

    def test_invalid_source_reported_not_clean(self):
        self.source.write_text("def broken(:\n")
        report = inventory(self.source)
        self.assertEqual(report["diagnostics"][0]["kind"], "PARSE_ERROR")
        self.assertNotEqual(report["verdict"], "NO_FINDING")

    def test_ast_parse_success_is_not_compile_success(self):
        self.source.write_text("return 42\n")
        self.assertTrue(inventory(self.source)["diagnostics"])

    def test_invalid_encoding_and_null_are_preserved_errors(self):
        for value in (b"\xff", b"x = '\x00'\n"):
            self.source.write_bytes(value)
            self.assertTrue(inventory(self.source)["diagnostics"])

    def test_input_byte_limit(self):
        self.source.write_bytes(b"#" * (MAX_SOURCE_BYTES + 1))
        with self.assertRaises(ValueError):
            inventory(self.source)

    def test_final_source_symlink_rejected(self):
        target = self.root / "target"
        target.write_text("pass\n")
        self.source.symlink_to(target)
        with self.assertRaises(OSError):
            inventory(self.source)

    def test_fifo_source_rejected_without_blocking(self):
        os.mkfifo(self.source)
        with self.assertRaises(ValueError):
            inventory(self.source)

    def test_execution_always_refuses(self):
        with self.assertRaises(ExecutionDisabled):
            execute_subject(["python3", "subject.py"], unsafe=True)

    def test_all_backends_honestly_unavailable(self):
        states = capabilities()
        self.assertGreaterEqual(len(states), 10)
        self.assertEqual(set(states.values()), {"NOT_IMPLEMENTED"})

    def test_cli_status_no_successful_backend_claims(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["status"])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["subject_execution"], "DISABLED")
        self.assertEqual(report["hosted_ci"], "PROHIBITED")

    def test_inventory_cli_parse_error_exit(self):
        self.source.write_text("def invalid(:\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["inventory", str(self.source)]), 2)

    def test_inventory_cli_missing_file_exit(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["inventory", str(self.source)]), 2)

    def test_cli_malformed_schema_error_is_actionable(self):
        record = self.root / "record.json"
        schema = self.root / "schema.json"
        record.write_text("{}")
        schema.write_text('{"$ref":"https://invalid.example/schema"}')
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["validate", str(record), "--schema", str(schema)])
        self.assertEqual(code, 2)
        self.assertIn("Unsupported schema keywords", err.getvalue())

