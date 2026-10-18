"""What every activity records about itself: when, by whom, with which code, in which environment."""

from __future__ import annotations

import hashlib
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import __version__

AGENT_SOFTWARE = "agent:channelscope"
AGENT_LUMEN = "agent:lumen"

PACKAGE_DIR = Path(__file__).resolve().parent


def now() -> str:
    """The current time, UTC, ISO 8601 with milliseconds: the only timestamp form the schema accepts."""
    t = datetime.now(UTC)  # one reading of the clock; two could straddle a second
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def code_digest(package_dir: Path = PACKAGE_DIR) -> str:
    """SHA-256 over the package's source files, so a run names the exact code that made it.

    Each file contributes its path relative to the package and its bytes with CRLF normalised to LF, so the digest
    is the same on a checkout whose line endings git has converted.
    """
    h = hashlib.sha256()
    for path in sorted(package_dir.rglob("*.py")):
        rel = path.relative_to(package_dir).as_posix()
        h.update(rel.encode("utf-8") + b"\0")
        h.update(path.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return "sha256:" + h.hexdigest()


def software() -> dict:
    return {"name": "channelscope", "version": __version__, "code_digest": code_digest()}


def environment() -> dict:
    return {"python": sys.version.split()[0], "platform": platform.platform()}
