import json
import tempfile
import unittest
from pathlib import Path

from axiomlint.schema import InvalidRecord, check_schema, load_json, validate

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_all_published_schemas_use_supported_vocabulary(self):
        paths = list((ROOT / "schemas").glob("*.schema.json"))
        self.assertGreaterEqual(len(paths), 7)
        for path in paths:
            check_schema(load_json(path))

    def test_valid_object(self):
        validate({"name": "value"}, {
            "type": "object", "properties": {"name": {"type": "string", "minLength": 1}},
            "required": ["name"], "additionalProperties": False,
        })

    def test_missing_required_rejected(self):
        with self.assertRaises(InvalidRecord):
            validate({}, {"type": "object", "required": ["name"]})

    def test_unknown_property_rejected(self):
        with self.assertRaises(InvalidRecord):
            validate({"surprise": 1}, {"type": "object", "additionalProperties": False})

    def test_boolean_is_not_integer(self):
        with self.assertRaises(InvalidRecord):
            validate(True, {"type": "integer"})

    def test_boolean_is_not_numeric_enum(self):
        with self.assertRaises(InvalidRecord):
            validate(True, {"enum": [1]})

    def test_false_is_not_zero_constant(self):
        with self.assertRaises(InvalidRecord):
            validate(0, {"const": False})

    def test_null_and_number(self):
        validate(None, {"type": "null"})
        validate(1.25, {"type": "number", "minimum": 0})
        with self.assertRaises(InvalidRecord):
            validate(-1, {"type": "number", "minimum": 0})

    def test_array_minimum_and_nested_types(self):
        schema = {"type": "array", "minItems": 1, "items": {"type": "string"}}
        validate(["ok"], schema)
        for value in ([], [4]):
            with self.assertRaises(InvalidRecord):
                validate(value, schema)

    def test_pattern_and_string_lengths(self):
        schema = {"type": "string", "minLength": 2, "maxLength": 3, "pattern": "^a"}
        validate("abc", schema)
        for value in ("a", "abcd", "bcd"):
            with self.assertRaises(InvalidRecord):
                validate(value, schema)

    def test_unsupported_keyword_fails_even_in_unused_branch(self):
        with self.assertRaises(InvalidRecord):
            validate({}, {"properties": {"unused": {"format": "date"}}})

    def test_external_reference_rejected_without_fetch(self):
        with self.assertRaises(InvalidRecord):
            check_schema({"$ref": "https://invalid.example/schema"})

    def test_invalid_schema_pattern(self):
        with self.assertRaises(InvalidRecord):
            check_schema({"pattern": "["})

    def test_duplicate_required(self):
        with self.assertRaises(InvalidRecord):
            check_schema({"required": ["x", "x"]})

    def test_schema_enums_and_additional_policy_are_checked(self):
        for schema in ({"enum": []}, {"additionalProperties": {}}, {"minLength": True}):
            with self.assertRaises(InvalidRecord):
                check_schema(schema)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text('{"approval": "PENDING", "approval": "APPROVED"}')
            with self.assertRaises(InvalidRecord):
                load_json(path)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            for value in ("NaN", "Infinity", "-Infinity"):
                path.write_text(f'{{"value": {value}}}')
                with self.assertRaises(InvalidRecord):
                    load_json(path)

    def test_malformed_json_and_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text("{not-json")
            with self.assertRaises(InvalidRecord):
                load_json(path)
            with self.assertRaises(InvalidRecord):
                load_json(Path(tmp) / "missing")

    def test_project_config_rejects_hosted_or_dynamic_enablement(self):
        schema = load_json(ROOT / "schemas/project.schema.json")
        config = load_json(ROOT / "config/project.json")
        validate(config, schema)
        for key in ("hosted_ci", "subject_execution", "telemetry", "network_during_checks"):
            modified = {**config, key: True}
            with self.assertRaises(InvalidRecord):
                validate(modified, schema)

    def test_session_unknown_state_rejected(self):
        schema = load_json(ROOT / "schemas/session.schema.json")
        session = load_json(ROOT / "governance/sessions/index.json")[0]
        with self.assertRaises(InvalidRecord):
            validate({**session, "status": "AUTO_APPROVED"}, schema)

    def test_strict_loading_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            value = {"unicode": "λ", "nested": [1, None, False]}
            path.write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(load_json(path), value)

    def test_exponent_overflow_is_not_finite_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text('{"value":1e9999}')
            with self.assertRaises(InvalidRecord):
                load_json(path)

    def test_nonfinite_native_values_rejected(self):
        for value in (float("nan"), float("inf"), {1: "nonstring-key"}):
            with self.assertRaises(InvalidRecord):
                validate(value, {})

    def test_nested_boolean_numeric_equality_not_conflated(self):
        for value, schema in (
            ([True], {"const": [1]}),
            ({"x": False}, {"enum": [{"x": 0}]}),
        ):
            with self.assertRaises(InvalidRecord):
                validate(value, schema)

    def test_malformed_supported_keyword_types_fail_cleanly(self):
        for schema in (
            {"type": ["string", "null"]}, {"pattern": 1},
            {"description": False}, {"$schema": "http://unsupported.invalid/dialect"},
        ):
            with self.assertRaises(InvalidRecord):
                check_schema(schema)

    def test_numeric_enum_duplicate_rejected_boolean_remains_distinct(self):
        with self.assertRaises(InvalidRecord):
            check_schema({"enum": [1, 1.0]})
        check_schema({"enum": [True, 1]})

    def test_scalar_keywords_require_compatible_declared_type(self):
        """FIND-S2-002: scalar-specific keywords need a matching declared type."""
        rejected = (
            {"minimum": 10},
            {"type": "string", "minimum": 10},
            {"type": "boolean", "minimum": 0},
            {"pattern": "^a"},
            {"type": "integer", "pattern": "^a"},
            {"minLength": 1},
            {"type": "number", "maxLength": 3},
            {"type": "object", "properties": {"x": {"minimum": 0}}},
        )
        for schema in rejected:
            with self.subTest(schema=schema), self.assertRaises(InvalidRecord):
                check_schema(schema)

    def test_scalar_keywords_with_compatible_type_accepted(self):
        for schema in (
            {"type": "integer", "minimum": 0},
            {"type": "number", "minimum": 0.5},
            {"type": "string", "pattern": "^a", "minLength": 1, "maxLength": 4},
        ):
            with self.subTest(schema=schema):
                check_schema(schema)

    def test_untyped_value_cannot_bypass_minimum_or_pattern(self):
        for value, schema in ("sample", {"minimum": 10}), (5, {"pattern": "^z"}):
            with self.subTest(schema=schema), self.assertRaises(InvalidRecord):
                validate(value, schema)
