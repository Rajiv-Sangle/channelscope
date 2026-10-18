"""rebuild_revision.py - rebuild a measured coordinate file from the PDB's later revision of it and a patch.

The PDB released revision 1.1 of 9ZO8 and 9ZOE on 14 October 2026. Both were measured at revision 1.0, which the PDB no
longer serves (this project's decision of 15 October 2026, its option (e)). A patch, made by
make_revision_patch.py, holds the lines of 1.0 that 1.1 replaced and the places of those it added, the measured file's
gzip header, and the SHA-256 of the two texts. rebuild() unzips the file the PDB serves, checks its text against the
patch, applies the patch, checks the text again, and compresses it with zlib at level 9 behind the stored header.

It returns bytes, never a verdict: the caller's guard checks them against the measured file's retrieval record, as it
checks any coordinate file, and reads the SHA-256 it expects from that record only. Compression depends on the deflate
library of the Python that runs it: the patches were made with zlib 1.3.2 (Windows); zlib 1.3.2 (Windows) and 1.3
(Linux) gave the measured bytes in the runs the states release logs, and 1.3.2 (Linux) in a separate test whose log it
does not carry, while zlib-ng (as in CPython 3.14's Windows builds) gives others, which the guard then refuses. why_refused() names zlib-ng when this Python's zlib is zlib-ng, and
otherwise says that the patch or the record may be wrong. The interpreter's pin does not fix the zlib a Python links.
"""
from __future__ import annotations

import gzip
import hashlib
import struct
import zlib

LEVEL, WBITS, MEMLEVEL = 9, -15, 8  # raw deflate, 32 KB window, as the PDB's files were compressed


class NotRebuilt(Exception):
    pass


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def library() -> str:
    """The deflate library of this Python, as it reports itself."""
    ng = getattr(zlib, "ZLIBNG_VERSION", None)
    return f"zlib {zlib.ZLIB_RUNTIME_VERSION}" + (f", which is zlib-ng {ng}" if ng else "")


def is_zlib_ng() -> bool:
    return hasattr(zlib, "ZLIBNG_VERSION") or "zlib-ng" in zlib.ZLIB_RUNTIME_VERSION


def apply(text: bytes, patch: dict) -> bytes:
    """The text of the revision measured, from the text served and the patch, each checked by its SHA-256."""
    if sha256(text) != patch["from"]["text_sha256"]:
        raise NotRebuilt(f"the file served is not the text of revision {patch['from']['revision']} the patch was made "
                         f"from: its SHA-256 is {sha256(text)}")
    lines, out, pos = text.decode("utf-8").split("\n"), [], 0
    for h in patch["hunks"]:
        if h["at"] < pos or h["remove"] < 0 or h["at"] + h["remove"] > len(lines):
            raise NotRebuilt(f"the patch's hunk at line {h['at']} does not fit the text")
        out += lines[pos:h["at"]] + h["insert"]
        pos = h["at"] + h["remove"]
    out += lines[pos:]
    rebuilt = "\n".join(out).encode("utf-8")
    if sha256(rebuilt) != patch["to"]["text_sha256"]:
        raise NotRebuilt(f"the patch did not give the text of revision {patch['to']['revision']}")
    return rebuilt


def compress(text: bytes, header: bytes) -> bytes:
    c = zlib.compressobj(LEVEL, zlib.DEFLATED, WBITS, MEMLEVEL, zlib.Z_DEFAULT_STRATEGY)
    return header + c.compress(text) + c.flush() + struct.pack("<II", zlib.crc32(text), len(text) & 0xFFFFFFFF)


def rebuild(served: bytes, patch: dict) -> bytes:
    """The measured file's bytes, rebuilt from the gzip file the PDB serves now; NotRebuilt if the file served or the
    patch does not fit (a malformed patch is refused by name, never passed on as an error)."""
    try:
        text = gzip.decompress(served)
    except (OSError, EOFError, zlib.error) as e:
        raise NotRebuilt(f"the file served is not a gzip file: {e}") from None
    try:
        header = bytes.fromhex(patch["gzip_header_hex"])
        if len(header) < 10 or header[:3] != b"\x1f\x8b\x08":
            raise NotRebuilt("the patch's gzip header is not a gzip header")
        return compress(apply(text, patch), header)
    except (KeyError, TypeError, ValueError, AttributeError, UnicodeDecodeError) as e:
        raise NotRebuilt(f"the patch is not in the form this module reads: {type(e).__name__}: {e}") from None


def why_refused(patch: dict) -> str:
    """For a caller whose guard refused a rebuilt file: what the rebuild did, and what may be wrong. zlib-ng is named
    only when this Python's zlib is zlib-ng; otherwise the patch's header or target, or the record, may be wrong."""
    done = (f"rebuilt from revision {patch['from']['revision']}, its text has the SHA-256 the patch gives for revision "
            f"{patch['to']['revision']}, but compressed by this Python's {library()} it is not the measured file")
    if is_zlib_ng():
        return (f"{done}: the measured bytes need zlib's output at level {LEVEL}, and zlib-ng compresses otherwise; "
                "run it with a Python whose zlib is zlib itself (CPython 3.12, as the repository pins it)")
    return (f"{done}; this zlib is not one known to compress otherwise, so the patch's gzip header or its target, or "
            "the retrieval record, may be wrong")
