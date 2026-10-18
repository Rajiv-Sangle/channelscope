"""The network layer. This is the only module that talks to the network (the archive's pure-core rule); everything
else receives what it returns. Redirects are not followed: a moved resource is a changed plan, and following it
silently would record one URL and read another."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from . import __version__
from .provenance import now

USER_AGENT = f"channelscope/{__version__} (evidence-graph fetch)"


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: dict[str, str]  # names lower-cased
    content: bytes
    started_at_time: str
    ended_at_time: str


def http(method: str, url: str, *, accept: str | None = None, body: bytes | None = None,
         content_type: str | None = None, timeout: float = 120.0,
         transport: httpx.BaseTransport | None = None) -> HttpResult:
    """One request. `transport` exists for tests, which substitute a stand-in for the network."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    if content_type:
        headers["Content-Type"] = content_type
    started = now()
    with httpx.Client(timeout=timeout, follow_redirects=False, transport=transport) as client:
        resp = client.request(method, url, headers=headers, content=body)
        content = resp.content
    ended = now()
    return HttpResult(resp.status_code, {k.lower(): v for k, v in resp.headers.items()}, content, started, ended)
