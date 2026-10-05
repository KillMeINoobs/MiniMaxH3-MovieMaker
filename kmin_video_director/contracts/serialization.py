"""Canonical UTF-8 JSON, bounded parsing and content digests."""
import hashlib
import json

from ..errors import ContractError, fail
from .validation import validate_json

MAX_PROJECT_BYTES = 8 * 1024 * 1024


def canonical_bytes(value):
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    validate_json(value)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, UnicodeError, RecursionError):
        fail("INVALID_JSON", "JSON must contain valid finite UTF-8 data.")


def digest_bytes(value):
    return {"algorithm": "sha256", "hex": hashlib.sha256(value).hexdigest()}


def digest_json(value):
    return digest_bytes(canonical_bytes(value))


def parse_json(text):
    def pairs(entries):
        result = {}
        for key, value in entries:
            if key in result:
                fail("INVALID_JSON", "Duplicate JSON object keys are not accepted.")
            result[key] = value
        return result
    try:
        if type(text) is bytes:
            text = text.decode("utf-8")
        if type(text) is not str:
            fail("INVALID_JSON", "Expected UTF-8 JSON text.")
        if len(text.encode("utf-8")) > MAX_PROJECT_BYTES:
            fail("RESOURCE_LIMIT", "Project JSON exceeds the 8 MiB limit.")
        value = json.loads(text, object_pairs_hook=pairs,
                           parse_constant=lambda _: fail("INVALID_JSON", "Nonfinite JSON is not accepted."))
        validate_json(value)
        return value
    except ContractError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        fail("INVALID_JSON", "Malformed UTF-8 JSON.")


def dumps(record):
    return canonical_bytes(record).decode("utf-8")


def loads(text):
    from .records import RECORD_TYPES
    data = parse_json(text)
    if type(data) is not dict:
        fail("INVALID_RECORD", "Expected a standalone record.")
    kind = data.get("kind")
    if type(kind) is not str:
        fail("INVALID_RECORD", "Record kind must be a string.")
    name = kind.removeprefix("kmin.")
    if name not in RECORD_TYPES:
        fail("UNSUPPORTED_CAPABILITY", "This record kind is not supported.")
    return RECORD_TYPES[name].from_dict(data)
