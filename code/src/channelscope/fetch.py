"""Fetch plans: the calls to make, and how each is logged as a retrieval record with its raw snapshot.

A plan is a YAML list of calls (see `PlannedCall`). `fetch` takes the network function as an argument, so the
logic here is tested offline with a stand-in; only `channelscope.net.http` touches the network. A call that does
not return 200 raises with its status, URL and times, so a failure is reported exactly, never summarised.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import __version__
from .graph import Graph
from .ids import sha256_hex
from .models import SCHEMA_VERSION, DataAbsentReason, Retrieval
from .net import HttpResult
from .provenance import AGENT_LUMEN, AGENT_SOFTWARE, code_digest

HttpFn = Callable[..., HttpResult]


@dataclass(frozen=True)
class PlannedCall:
    name: str
    source: str
    url: str
    stored_at: str
    http_method: str = "GET"
    accept: str | None = None
    body: str | None = None
    content_type: str | None = None
    storage: str = "committed"
    release_header: str | None = None
    release_json: str | None = None
    release_from_call: str | None = None
    release_absent: str | None = None
    pause_s: float = 0.0
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        ways = [x is not None for x in (self.release_header, self.release_json, self.release_absent)]
        if sum(ways) != 1:
            raise ValueError(f"{self.name}: give exactly one of release_header, release_json and release_absent")
        if self.release_from_call is not None and self.release_json is None:
            raise ValueError(f"{self.name}: release_from_call needs release_json, the path to read there")
        if self.release_absent is not None:
            DataAbsentReason(self.release_absent)  # refuses a reason that is not a FHIR code
        if self.storage not in ("committed", "cache"):
            raise ValueError(f"{self.name}: storage must be committed or cache")
        expected = "raw/" if self.storage == "committed" else "cache/"
        if not self.stored_at.startswith(expected):
            raise ValueError(f"{self.name}: a {self.storage} snapshot is stored under {expected}")


class FetchError(RuntimeError):
    pass


def load_plan(path: Path) -> list[PlannedCall]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [PlannedCall(**item) for item in data["calls"]]


def fetch_method(on_behalf_of: str = AGENT_LUMEN) -> dict:
    return {
        "schema_version": SCHEMA_VERSION, "type": "method", "synthetic": False,
        "name": "channelscope.fetch", "version": __version__,
        "description": "One HTTP request to a public source, logged in full: the request, the times, the status, "
                       "and the SHA-256 of the bytes returned, which are kept as a raw snapshot. Redirects are not "
                       "followed.",
        "implementation": {"software": "channelscope", "version": __version__, "code_digest": code_digest()},
        "parameters": {"follow_redirects": False, "timeout_s": 120},
        "was_attributed_to": on_behalf_of,
    }


def _json_path(content: bytes, path: str, name: str) -> str:
    value: object = json.loads(content)
    for part in path.split("."):
        if isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        elif isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise FetchError(f"{name}: no {path!r} in the response that should state the release")
    if isinstance(value, (dict, list)) or value in (None, ""):
        raise FetchError(f"{name}: {path!r} does not hold a release value")
    return str(value)


def fetch(graph: Graph, calls: list[PlannedCall], http: HttpFn, *, on_behalf_of: str = AGENT_LUMEN,
          method: dict | None = None, synthetic: bool = False) -> list[Retrieval]:
    """Make each call, keep its bytes, and append its retrieval record. A call already made (a retrieval with the
    same URL and path whose snapshot is present and intact) is not made again, so a plan interrupted by a failure
    can simply be re-run."""
    method_record = graph.append(method or {**fetch_method(on_behalf_of), "synthetic": synthetic})
    done: dict[tuple[str, str], Retrieval] = {}
    for r in graph.records():
        if isinstance(r, Retrieval) and graph.path(r.stored_at).is_file() \
                and graph.file_digest(r.stored_at) == r.generated:
            done[(r.request.url, r.stored_at)] = r
    responses: dict[str, bytes] = {}
    out: list[Retrieval] = []
    for c in calls:
        previous = done.get((c.url, c.stored_at))
        if previous is not None:
            responses[c.name] = graph.path(c.stored_at).read_bytes()
            out.append(previous)
            continue
        if c.pause_s:
            time.sleep(c.pause_s)
        body = c.body.encode("utf-8") if c.body is not None else None
        res = http(c.http_method, c.url, accept=c.accept, body=body, content_type=c.content_type)
        if res.status != 200:
            raise FetchError(f"{c.name}: HTTP {res.status} for {c.http_method} {c.url} "
                             f"({res.started_at_time} to {res.ended_at_time}); nothing was recorded")
        responses[c.name] = res.content
        release, basis = None, None
        if c.release_header:
            release = res.headers.get(c.release_header.lower())
            basis = f"HTTP response header {c.release_header}"
            if not release:
                raise FetchError(f"{c.name}: the response carried no {c.release_header} header; the plan must say "
                                 f"why no release is recorded instead")
        elif c.release_json:
            source_call = c.release_from_call or c.name
            if source_call not in responses:
                raise FetchError(f"{c.name}: release_from_call {source_call!r} has not run earlier in this plan")
            release = _json_path(responses[source_call], c.release_json, c.name)
            where = "this response" if source_call == c.name else f"the response to call {source_call!r}"
            basis = f"JSON field {c.release_json} of {where}"
        body_path = None
        if body is not None:
            body_path = c.stored_at + ".request"
            graph.write_bytes(body_path, body)
        digest = graph.write_bytes(c.stored_at, res.content)
        record = {
            "schema_version": SCHEMA_VERSION, "type": "retrieval", "synthetic": synthetic,
            "source": c.source, "method": method_record.id,
            "request": {"http_method": c.http_method, "url": c.url, "accept": c.accept,
                        "body_sha256": "sha256:" + sha256_hex(body) if body is not None else None,
                        "body_path": body_path},
            "started_at_time": res.started_at_time, "ended_at_time": res.ended_at_time,
            "response": {"status": res.status, "content_type": res.headers.get("content-type"),
                         "bytes": len(res.content)},
            "source_release": release,
            "source_release_basis": basis,
            "source_release_absent": c.release_absent,
            "generated": digest, "stored_at": c.stored_at, "storage": c.storage,
            "was_associated_with": AGENT_SOFTWARE, "acted_on_behalf_of": on_behalf_of,
        }
        out.append(graph.append(record))  # type: ignore[arg-type]
    return out
