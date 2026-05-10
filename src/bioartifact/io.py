from __future__ import annotations

import gzip
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

GZIP_MAGIC = b"\x1f\x8b"


def is_gzip(path: str | Path) -> bool:
    with Path(path).open("rb") as handle:
        return handle.read(2) == GZIP_MAGIC


@contextmanager
def open_text(path: str | Path) -> Iterator[TextIO]:
    artifact_path = Path(path)
    if is_gzip(artifact_path):
        with gzip.open(artifact_path, "rt", encoding="utf-8", errors="replace") as handle:
            yield handle
    else:
        with artifact_path.open("rt", encoding="utf-8", errors="replace") as handle:
            yield handle


def strip_newline(line: str) -> str:
    return line.rstrip("\r\n")
