"""Read and validate the bounded, explicit native object-info handoff envelope."""
import json
from pathlib import Path

from .profile import incompatible, validate_schema_numbers


def read_handoff(context):
    context.cancellation.check()
    try:
        path = Path(context.versions['native_schema_file'])
        if not path.is_file() or path.stat().st_size > 1048576:
            raise ValueError
        capture = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(capture, dict):
            raise ValueError
        schemas, runtime = capture.get('schemas'), capture.get('runtime')
        if not isinstance(schemas, dict) or not isinstance(runtime, dict):
            raise ValueError
        core = runtime.get('core_commit')
        if not isinstance(core, str) or len(core) != 40 or any(c not in '0123456789abcdef' for c in core):
            raise ValueError
        for name, schema in schemas.items():
            if not isinstance(name, str) or not isinstance(schema, dict):
                raise ValueError
            inputs, outputs = schema.get('input'), schema.get('output')
            if not isinstance(inputs, dict) or not isinstance(inputs.get('required'), dict):
                raise ValueError
            if not isinstance(outputs, list) or any(not isinstance(v, str) for v in outputs):
                raise ValueError
            for group in ('required', 'optional'):
                ports = inputs.get(group, {})
                if not isinstance(ports, dict):
                    raise ValueError
                for key, port in ports.items():
                    if (not isinstance(key, str) or not isinstance(port, list) or not 1 <= len(port) <= 2 or
                        not isinstance(port[0], (str, list)) or
                        isinstance(port[0], list) and any(not isinstance(v, str) for v in port[0]) or
                        len(port) == 2 and not isinstance(port[1], dict)):
                        raise ValueError
    except (KeyError, ValueError, OSError, TypeError, UnicodeError):
        incompatible('Select a valid native schema handoff with schemas, typed ports and runtime.core_commit.')
    validate_schema_numbers(schemas)
    context.cancellation.check()
    return schemas, core
