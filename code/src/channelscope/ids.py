"""Identifiers in the evidence graph: content digests, canonical JSON, and the grammar of every identifier.

ADR-001 §3. External identifiers are used wherever they exist (HGNC, UniProtKB, Ensembl, RefSeq, NCBI Taxonomy).
Our own records take a content digest: `sha512t24u` over RFC 8785 canonical JSON, the convention GA4GH VRS uses for
its computed identifiers and refget for sequences. Both were checked against their specifications on 2026-09-29:
- VRS, "Computed Identifiers": digest serialisation is RFC 8785 after filtering out fields with null values;
  `sha512t24u` is SHA-512 truncated to 24 bytes, base64url-encoded;
- refget, "Sequences": the sequence digest is `SQ.` + `sha512t24u` of the sequence, uppercased; its worked example
  is ACGT -> SQ.aKF498dAxcJAqme6QYQ7EZ07-fiw8Kw2 (pinned in tests/test_ids.py).

This module is pure: no network, no filesystem.
"""

from __future__ import annotations

import base64
import hashlib
import re
from typing import Any

import rfc8785

# --- digests ----------------------------------------------------------------------------------------------------


def sha512t24u(blob: bytes) -> str:
    """SHA-512 truncated to its first 24 bytes, base64url-encoded without padding (32 characters)."""
    return base64.urlsafe_b64encode(hashlib.sha512(blob).digest()[:24]).decode("ascii")


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def md5_hex(blob: bytes) -> str:
    return hashlib.md5(blob).hexdigest()


_SEQUENCE_LETTERS = re.compile(r"^[A-Za-z]+$")


def refget_digest(sequence: str) -> str:
    """The refget (ga4gh) sequence digest: `SQ.` + sha512t24u of the uppercased sequence.

    refget strips non-letter symbols before digesting. Here any such symbol is refused instead: a sequence that
    reaches this function with a newline, a gap or a stop symbol in it has been parsed wrongly, and stripping would
    hide that.
    """
    if not _SEQUENCE_LETTERS.match(sequence):
        raise ValueError("a sequence to digest must be letters only; refusing rather than stripping")
    return "SQ." + sha512t24u(sequence.upper().encode("ascii"))


def sequence_md5(sequence: str) -> str:
    """MD5 of the uppercased sequence, as refget and RefSeq give it (M01's A1 was designed against this value)."""
    if not _SEQUENCE_LETTERS.match(sequence):
        raise ValueError("a sequence to digest must be letters only")
    return md5_hex(sequence.upper().encode("ascii"))


# --- canonical JSON and record identifiers ---------------------------------------------------------------------


def drop_nulls(value: Any) -> Any:
    """Remove object fields whose value is null, recursively (VRS digest serialisation, step 1)."""
    if isinstance(value, dict):
        return {k: drop_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [drop_nulls(v) for v in value]
    return value


def canonical_json(value: Any) -> bytes:
    """RFC 8785 (JSON Canonicalization Scheme) serialisation of `value`, with null fields dropped first."""
    return rfc8785.dumps(drop_nulls(value))


# Fields left out of a record's content digest. The generating activity and the agent are left out so that the same
# method on the same inputs gives the same identifier whenever it runs (ADR-001 §3); the method itself stays in, so
# a new method version gives a new identifier (SO-DOMAIN-01).
DIGEST_EXCLUDED_PROVENANCE = ("was_generated_by", "was_attributed_to")


def content_digest(record: dict[str, Any]) -> str:
    """sha512t24u over the canonical JSON of a record, without its `id` and without the excluded provenance fields."""
    body = {k: v for k, v in record.items() if k != "id"}
    prov = body.get("provenance")
    if isinstance(prov, dict):
        body["provenance"] = {k: v for k, v in prov.items() if k not in DIGEST_EXCLUDED_PROVENANCE}
    return sha512t24u(canonical_json(body))


def record_id(record: dict[str, Any]) -> str:
    """`cs:<type>.<digest>`: the identifier a record must carry, computed from its own content."""
    return f"cs:{record['type']}.{content_digest(record)}"


# --- identifier grammar -----------------------------------------------------------------------------------------
# Patterns are written for the Rust regex engine pydantic uses (no look-around). Each is anchored where used.

UNIPROT_ACCESSION = r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"
"""UniProt's own accession format (uniprot.org/help/accession_numbers)."""

NUMBERING_KEY = (rf"(?:{UNIPROT_ACCESSION}-[1-9][0-9]*\.sv[1-9][0-9]*|{UNIPROT_ACCESSION}\.sv[1-9][0-9]*"
                 rf"|[NX]P_[0-9]+\.[1-9][0-9]*)")
"""A numbering names one exact sequence: a UniProtKB isoform with its sequence version (`P21817-1.sv3`); the sole
sequence of a UniProtKB entry that defines no isoforms (`P11716.sv1`, schema 0.2.0); or a versioned RefSeq protein
(`NP_000531.2`). An unversioned accession is not a numbering. Whether a UniProt accession needs its isoform is
checked against the protein record (validation rule V10), since the grammar alone cannot know."""

TRANSCRIPT_ACCESSION = r"(?:ENS[A-Z]*T[0-9]{11}\.[1-9][0-9]*|[NX][MR]_[0-9]+\.[1-9][0-9]*)"

PATTERNS: dict[str, str] = {
    "record_id": r"cs:[a-z_]+\.[A-Za-z0-9_-]{32}",
    "raw_digest": r"sha256:[0-9a-f]{64}",
    "sequence_digest": r"SQ\.[A-Za-z0-9_-]{32}",
    "source": r"source:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    "infores": r"infores:[a-z0-9][a-z0-9._-]*",
    "agent": r"agent:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    "gene": r"HGNC:[1-9][0-9]*",
    "taxon": r"NCBITaxon:[1-9][0-9]*",
    "protein": rf"UniProtKB:{UNIPROT_ACCESSION}",
    "numbering": rf"numbering:{NUMBERING_KEY}",
    "residue": rf"residue:{NUMBERING_KEY}:[1-9][0-9]*",
    "transcript": rf"(?:ENSEMBL:ENS[A-Z]*T[0-9]{{11}}\.[1-9][0-9]*|refseq:[NX][MR]_[0-9]+\.[1-9][0-9]*)",
    "exon": rf"exon:{TRANSCRIPT_ACCESSION}:[1-9][0-9]*",
    "gene_locus": r"locus:GRCh38:NC_[0-9]{6}\.[1-9][0-9]*:[1-9][0-9]*-[1-9][0-9]*:[+-]",
    "eco": r"ECO:[0-9]{7}",
    "timestamp": r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z",
}

# A provenance reference (`used`) may name a record, a raw snapshot by its digest, or an entity by its identifier.
REFERENCE_KINDS = ("record_id", "raw_digest", "source", "gene", "protein", "numbering", "residue", "transcript",
                   "exon", "gene_locus")
REFERENCE_PATTERN = "^(?:" + "|".join(PATTERNS[k] for k in REFERENCE_KINDS) + ")$"


def anchored(kind: str) -> str:
    return "^" + PATTERNS[kind] + "$"


_COMPILED = {k: re.compile(anchored(k)) for k in PATTERNS}


def matches(kind: str, value: str) -> bool:
    return bool(_COMPILED[kind].match(value))


def reference_kind(value: str) -> str | None:
    """Which kind of reference `value` is, or None if it is none of them."""
    for kind in REFERENCE_KINDS:
        if _COMPILED[kind].match(value):
            return kind
    return None


# --- residues and numberings --------------------------------------------------------------------------------------


def numbering_key(numbering_identifier: str) -> str:
    if not matches("numbering", numbering_identifier):
        raise ValueError(f"not a numbering identifier: {numbering_identifier!r}")
    return numbering_identifier.removeprefix("numbering:")


def residue_identifier(numbering_identifier: str, position: int) -> str:
    """`residue:<numbering key>:<position>`. A residue number never travels without its numbering."""
    if position < 1:
        raise ValueError(f"residue positions are 1-based; got {position}")
    return f"residue:{numbering_key(numbering_identifier)}:{position}"


def parse_residue_identifier(value: str) -> tuple[str, int]:
    if not matches("residue", value):
        raise ValueError(f"not a residue identifier: {value!r}")
    key, position = value.removeprefix("residue:").rsplit(":", 1)
    return f"numbering:{key}", int(position)
