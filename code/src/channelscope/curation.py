"""Curation files: the human-reviewed YAML that names which things to fetch, and registers sources.

A curation file is the one place a protein's constants live (the archive's node.yaml, renamed; ADR-001 §10). Code
reads identifiers from it and never hard-codes them. Seeding records the file's digest in a run, so each source
record says which version of the file it came from.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .graph import Graph
from .ids import sha256_hex
from .models import SCHEMA_VERSION, Record
from .provenance import AGENT_LUMEN, AGENT_SOFTWARE, code_digest, environment, now, software


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def method_record(name: str, description: str, parameters: dict | None = None) -> dict[str, Any]:
    """A method implemented by ChannelScope's own code at its current digest."""
    return {"schema_version": SCHEMA_VERSION, "type": "method", "synthetic": False, "name": name,
            "version": __version__, "description": description,
            "implementation": {"software": "channelscope", "version": __version__, "code_digest": code_digest()},
            "parameters": parameters or {}, "was_attributed_to": AGENT_LUMEN}


def run_record(method_id: str, started: str, used_files: list[dict] | None = None) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "type": "run", "synthetic": False, "method": method_id,
            "command": ["channelscope", *sys.argv[1:]] or ["channelscope"], "started_at_time": started,
            "ended_at_time": now(), "used_files": used_files or [], "software": software(),
            "environment": environment(), "was_associated_with": AGENT_SOFTWARE,
            "acted_on_behalf_of": AGENT_LUMEN}


def seed_sources(graph: Graph, curation_path: Path) -> list[Record]:
    """Register every source the curation file lists, under a run that names the file's digest."""
    started = now()
    data = curation_path.read_bytes()
    digest = "sha256:" + sha256_hex(data)
    rel = graph.relative(curation_path)  # FileRef paths are relative to the graph's root
    method = graph.append(method_record("channelscope.seed_sources",
                                        "Register sources from a human-reviewed curation file."))
    run = graph.append(run_record(method.id, started, [{"path": rel, "sha256": digest, "bytes": len(data)}]))
    out = []
    for s in yaml.safe_load(data)["sources"]:
        out.append(graph.append({
            "schema_version": SCHEMA_VERSION, "type": "source", "synthetic": False,
            "provenance": {"was_generated_by": run.id, "method": method.id, "used": [digest],
                           "was_attributed_to": AGENT_LUMEN},
            **s}))
    return out
