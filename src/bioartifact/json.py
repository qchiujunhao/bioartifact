from __future__ import annotations

import json
from typing import Any


def dumps_json(payload: Any, *, indent: int = 2) -> str:
    return json.dumps(payload, indent=indent, sort_keys=True)
