"""The evidence graph on disk (ADR-001 §10). Paths are relative to the graph's root, `what/evidence_graph/`:

    records/<type>.jsonl    one record per line, RFC 8785 canonical JSON; appended, never rewritten
    tables/                 TSV files; never edited (a correction is a new table)
    raw/                    small raw snapshots, committed
    cache/                  large raw snapshots, git-ignored; each is re-fetched by replaying its retrieval
    schema/v<M.m>/          the JSON Schema generated from the models, and the worked fixture
    curation/               per-protein curation files and fetch plans (human-reviewed)
    releases/<version>/     RO-Crate releases

Records are written only through `Graph.append`, which computes the record's id from its content, validates it
against its model, and writes the canonical line. Writing the same record twice is a no-op, so a re-run under the
same method and inputs adds nothing.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from .ids import canonical_json, record_id, sha256_hex
from .models import AnyRecord, Record

RECORD_ADAPTER: TypeAdapter = TypeAdapter(AnyRecord)


def find_vault_root(start: Path) -> Path:
    """Walk up from `start` to the directory holding MANIFEST.md (aDNA vault identity)."""
    for d in [start.resolve(), *start.resolve().parents]:
        if (d / "MANIFEST.md").is_file():
            return d
    raise FileNotFoundError(f"no MANIFEST.md at or above {start}: not inside a vault")


def default_graph_root(start: Path | None = None) -> Path:
    return find_vault_root(start or Path.cwd()) / "what" / "evidence_graph"


def canonical_line(record: dict[str, Any]) -> bytes:
    return canonical_json(record) + b"\n"


_PLACEHOLDER_DIGEST = "A" * 32


def normalise(record: dict[str, Any]) -> dict[str, Any]:
    """Validate a record against its model and return its canonical form: defaults filled in, null fields dropped,
    and `id` computed from that content (any `id` it arrived with is recomputed, never trusted).

    Validation goes through JSON because the models are strict: in Python mode, strict pydantic would refuse an
    enum's string value that JSON input legitimately carries."""
    body = {k: v for k, v in record.items() if k != "id"}
    placeholder = f"cs:{body.get('type')}.{_PLACEHOLDER_DIGEST}"
    parsed = RECORD_ADAPTER.validate_json(canonical_json({**body, "id": placeholder}))
    dumped = parsed.model_dump(mode="json", exclude_none=True)
    dumped.pop("id")
    return {**dumped, "id": record_id(dumped)}


@dataclass(frozen=True)
class Line:
    path: Path
    number: int
    raw: bytes


class Graph:
    def __init__(self, root: Path):
        self.root = Path(root)

    # --- locations -------------------------------------------------------------------------------------------------
    @property
    def records_dir(self) -> Path:
        return self.root / "records"

    def record_file(self, record_type: str) -> Path:
        return self.records_dir / f"{record_type}.jsonl"

    def path(self, relative: str) -> Path:
        """A graph-relative path (forward slashes) as a filesystem path, refusing anything that escapes the root."""
        p = (self.root / relative).resolve()
        if self.root.resolve() not in [p, *p.parents]:
            raise ValueError(f"{relative!r} escapes the graph root")
        return p

    def relative(self, p: Path) -> str:
        return p.resolve().relative_to(self.root.resolve()).as_posix()

    # --- reading ---------------------------------------------------------------------------------------------------
    def lines(self) -> Iterable[Line]:
        if not self.records_dir.is_dir():
            return
        for f in sorted(self.records_dir.glob("*.jsonl")):
            for n, raw in enumerate(f.read_bytes().splitlines(keepends=True), start=1):
                yield Line(f, n, raw)

    def records(self) -> list[Record]:
        """Every record, parsed and validated against its model. Raises on the first invalid line; use
        channelscope.validate for a full report."""
        return [RECORD_ADAPTER.validate_json(line.raw) for line in self.lines()]

    def by_id(self) -> dict[str, Record]:
        return {r.id: r for r in self.records()}

    # --- writing ---------------------------------------------------------------------------------------------------
    def append(self, record: dict[str, Any]) -> Record:
        """Validate a record, give it its content id, and append it; return the stored record.

        If a record with the same id is already stored, nothing is written and the stored record is returned."""
        full = normalise(record)
        target = self.record_file(full["type"])
        if target.is_file():
            for raw in target.read_bytes().splitlines():
                if raw and json.loads(raw).get("id") == full["id"]:
                    return RECORD_ADAPTER.validate_json(raw)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("ab") as fh:
            fh.write(canonical_line(full))
        return RECORD_ADAPTER.validate_json(canonical_json(full))

    def write_bytes(self, relative: str, data: bytes, overwrite: bool = False) -> str:
        """Write a file under the graph root and return `sha256:<hex>`. Existing files are never overwritten
        unless their bytes are identical (tables and raw snapshots are immutable)."""
        p = self.path(relative)
        digest = "sha256:" + sha256_hex(data)
        if p.exists():
            if p.read_bytes() == data:
                return digest
            if not overwrite:
                raise FileExistsError(f"{relative} exists with different content; tables and snapshots are "
                                      f"never edited, so write a new file")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return digest

    def file_digest(self, relative: str) -> str:
        return "sha256:" + sha256_hex(self.path(relative).read_bytes())


def tsv_bytes(header: list[str], rows: Iterable[Iterable[Any]]) -> bytes:
    """A TSV table as bytes: UTF-8, LF line endings, no quoting. None is written as an empty cell; booleans as
    `true`/`false`. A tab or newline inside a value is refused rather than escaped."""

    def cell(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, bool):
            return "true" if v else "false"
        s = str(v)
        if "\t" in s or "\n" in s or "\r" in s:
            raise ValueError(f"a TSV cell may not contain a tab or newline: {s!r}")
        return s

    out = ["\t".join(header)]
    out += ["\t".join(cell(v) for v in row) for row in rows]
    return ("\n".join(out) + "\n").encode("utf-8")
