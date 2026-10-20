"""Append-only by API, content-addressed, single-user local artifact storage.

The caller must own and trust the store parent. Not a malicious-host boundary.
"""

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any


class IntegrityError(ValueError):
    """Corrupt content, unsafe path, or invalid digest."""


def canonical_json(value: Any) -> bytes:
    """Project canonical JSON, not RFC 8785/JCS."""
    return (json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":"),
    ) + "\n").encode("utf-8")


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class ArtifactStore:
    def __init__(self, root: Path):
        root = root.absolute()
        for part in (root, *root.parents):
            if part.is_symlink():
                raise IntegrityError("Symlink in artifact store path")
        root.mkdir(parents=True, exist_ok=True)
        self.root = root

    def _path(self, digest: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise IntegrityError("Expected lowercase SHA-256")
        return self.root / digest

    def get(self, digest: str) -> bytes:
        path = self._path(digest)
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise IntegrityError("Artifact is not a regular file")
                content = stream.read()
        except OSError as exc:
            raise IntegrityError(f"Artifact unavailable: {digest}") from exc
        if sha256(content) != digest:
            raise IntegrityError(f"Digest mismatch: {digest}")
        return content

    def put(self, content: bytes) -> str:
        digest = sha256(content)
        path = self._path(digest)
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
        except FileExistsError:
            self.get(digest)
            return digest
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        self.get(digest)
        return digest

    def put_record(self, record: Any) -> str:
        return self.put(canonical_json(record))

