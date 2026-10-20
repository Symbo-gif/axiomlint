"""Deliberately small, closed JSON Schema vocabulary for foundation records.

Not a general Draft 2020-12 implementation. Unsupported keywords fail closed.
The schemas are portable to a full validator in WP-005.
"""

import json
import math
import re
from pathlib import Path
from typing import Any

KEYWORDS = {
    "$schema", "$id", "title", "description", "type", "enum", "const",
    "properties", "required", "additionalProperties", "items", "minItems",
    "minLength", "maxLength", "pattern", "minimum",
}
TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


class InvalidRecord(ValueError):
    """A malformed, unsupported, or invalid foundation record."""


def load_json(path: Path) -> Any:
    """Reject duplicate object keys and non-JSON numeric constants."""
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise InvalidRecord(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def bad_constant(value: str) -> None:
        raise InvalidRecord(f"Non-JSON numeric constant: {value}")

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=pairs, parse_constant=bad_constant,
        )
        check_json_value(value)
        return value
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidRecord(f"{path}: {exc}") from exc


def check_json_value(value: Any) -> None:
    """Reject values outside the JSON data model, including exponent overflow."""
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if isinstance(value, list):
        for item in value:
            check_json_value(item)
        return
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        for item in value.values():
            check_json_value(item)
        return
    raise InvalidRecord("Value is not finite, string-keyed JSON data")


def json_equal(a: Any, b: Any) -> bool:
    """JSON equality, distinguishing Booleans from numbers at every depth."""
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    return a == b


def check_schema(schema: Any) -> None:
    if not isinstance(schema, dict):
        raise InvalidRecord("Only object schemas are supported")
    check_json_value(schema)
    extra = set(schema) - KEYWORDS
    if extra:
        raise InvalidRecord(f"Unsupported schema keywords: {sorted(extra)}")
    if "type" in schema and (
        not isinstance(schema["type"], str) or schema["type"] not in TYPES
    ):
        raise InvalidRecord("Unsupported schema type")
    for key in ("$schema", "$id", "title", "description"):
        if key in schema and not isinstance(schema[key], str):
            raise InvalidRecord(f"{key} must be a string")
    if "$schema" in schema and schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
        raise InvalidRecord("Unsupported declared schema dialect")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise InvalidRecord("additionalProperties must be boolean in this vocabulary")
    for key in ("minItems", "minLength", "maxLength"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise InvalidRecord(f"Invalid {key}")
    if "minimum" in schema and type(schema["minimum"]) not in (int, float):
        raise InvalidRecord("Invalid minimum")
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        raise InvalidRecord("enum must be a nonempty array")
    if "enum" in schema:
        for i, item in enumerate(schema["enum"]):
            if any(json_equal(item, other) for other in schema["enum"][:i]):
                raise InvalidRecord("Duplicate enum value")
    required = schema.get("required", [])
    if not isinstance(required, list) or any(not isinstance(x, str) for x in required):
        raise InvalidRecord("required must contain strings")
    if len(required) != len(set(required)):
        raise InvalidRecord("Duplicate required property")
    props = schema.get("properties", {})
    if not isinstance(props, dict):
        raise InvalidRecord("properties must be an object")
    for child in props.values():
        check_schema(child)
    if "items" in schema:
        check_schema(schema["items"])
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise InvalidRecord("pattern must be a string")
        try:
            re.compile(schema["pattern"])
        except (re.error, TypeError) as exc:
            raise InvalidRecord("Invalid schema pattern") from exc


def validate(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    check_schema(schema)
    check_json_value(value)
    expected = schema.get("type")
    matches = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "integer": type(value) is int,
        "number": type(value) in (int, float), "boolean": type(value) is bool,
        "null": value is None,
    }
    if expected and not matches[expected]:
        raise InvalidRecord(f"{path}: expected {expected}")
    if "const" in schema and not json_equal(value, schema["const"]):
        raise InvalidRecord(f"{path}: wrong constant")
    if "enum" in schema and not any(json_equal(value, x) for x in schema["enum"]):
        raise InvalidRecord(f"{path}: outside enum")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        missing = set(schema.get("required", [])) - value.keys()
        if missing:
            raise InvalidRecord(f"{path}: missing {sorted(missing)}")
        if schema.get("additionalProperties") is False and set(value) - props.keys():
            raise InvalidRecord(f"{path}: additional properties")
        for key, child in value.items():
            if key in props:
                validate(child, props[key], f"{path}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise InvalidRecord(f"{path}: too few items")
        if "items" in schema:
            for i, child in enumerate(value):
                validate(child, schema["items"], f"{path}[{i}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise InvalidRecord(f"{path}: too short")
        if len(value) > schema.get("maxLength", len(value)):
            raise InvalidRecord(f"{path}: too long")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise InvalidRecord(f"{path}: pattern mismatch")
    if type(value) in (int, float) and "minimum" in schema and value < schema["minimum"]:
        raise InvalidRecord(f"{path}: below minimum")
