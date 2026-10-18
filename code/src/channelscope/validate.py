"""Validate the evidence graph: every line, every reference, every file (M01's check A8 runs this).

Each rule has a code, and each code has a test that injects a fault it must catch (tests/test_validate.py).
The validator reads files but never writes, and never calls the network.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass

from pydantic import ValidationError

from . import models as m
from .graph import RECORD_ADAPTER, Graph, canonical_line, normalise
from .ids import record_id, reference_kind, refget_digest, sequence_md5, sha256_hex

RULES: dict[str, str] = {
    "V01": "each line parses as JSON and validates against its type's model",
    "V02": "each line is in canonical form: RFC 8785, defaults filled in, null fields dropped",
    "V03": "each record's id is the digest of its own content",
    "V04": "no two lines carry the same id",
    "V05": "each record sits in the file for its type",
    "V06": "at most one current record per entity identifier (a later one must name what it revises)",
    "V07": "every reference resolves, to a record of the right type (a revision, to one of its own type)",
    "V08": "every stored raw snapshot matches its retrieval's digest and size",
    "V09": "every table matches its record: checksum, size, header, row count, cell types, required cells, key",
    "V10": "every numbering's sequence agrees with its length, its digests and its identifier",
    "V11": "every residue's identifier and amino acid agree with its numbering",
    "V12": "every exon's coding arithmetic holds, and a transcript's exons add up to it",
    "V13": "every alignment's counts and identity follow from its path and its numberings",
    "V14": "a record that uses or refers to a synthetic record is synthetic too",
    "V15": "every retrieval states its source release or why it has none, and its times are in order",
    "V16": "every search result's count matches its hits",
    "V17": "every gene locus is well formed, and its identifier matches its fields",
}

ENTITY_TYPES = ("source", "gene", "gene_locus", "transcript", "exon", "protein", "numbering", "residue")
ACTIVITY_TYPES = ("retrieval", "run")


@dataclass(frozen=True)
class Finding:
    rule: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.rule} {self.where}: {self.message}"


@dataclass(frozen=True)
class Located:
    record: m.Record
    where: str


def _references(r: m.Record) -> Iterator[tuple[str, str, tuple[str, ...] | None]]:
    """(field, value, allowed target types or None for any) for every reference a record makes."""
    prov = getattr(r, "provenance", None)
    if prov is not None:
        yield "provenance.was_generated_by", prov.was_generated_by, ACTIVITY_TYPES
        yield "provenance.method", prov.method, ("method",)
        for u in prov.used:
            yield "provenance.used", u, None
        if prov.primary_knowledge_source:
            yield "provenance.primary_knowledge_source", prov.primary_knowledge_source, ("source",)
        if prov.was_revision_of:
            yield "provenance.was_revision_of", prov.was_revision_of, (r.type,)
    single = {
        "retrieval": [("source", ("source",)), ("method", ("method",))],
        "run": [("method", ("method",))],
        "gene_locus": [("gene", ("gene",))],
        "transcript": [("gene", ("gene",)), ("annotation", ("source",)), ("mane_counterpart", ("transcript",))],
        "exon": [("transcript", ("transcript",)), ("residue_numbering", ("numbering",))],
        "protein": [("gene", ("gene",)), ("canonical_numbering", ("numbering",))],
        "numbering": [("protein", ("protein",))],
        "residue": [("numbering", ("numbering",))],
        "alignment": [("subject", ("numbering",)), ("object", ("numbering",))],
        "residue_mapping": [("subject", ("numbering",)), ("object", ("numbering",)), ("table", ("table",))],
        "search_result": [("source", ("source",)), ("retrieval", ("retrieval",))],
    }
    for field, allowed in single.get(r.type, []):
        value = getattr(r, field)
        if value is not None:
            yield field, value, allowed
    multi = {
        "protein": [("isoform_numberings", ("numbering",))],
        "residue_mapping": [("alignments", ("alignment",))],
        "release": [("has_part", None)],
        "table": [("about", None)],
    }
    for field, allowed in multi.get(r.type, []):
        for value in getattr(r, field):
            yield field, value, allowed


def validate(graph: Graph) -> list[Finding]:
    findings: list[Finding] = []

    def add(rule: str, where: str, message: str) -> None:
        findings.append(Finding(rule, where, message))

    located: list[Located] = []
    seen_ids: dict[str, str] = {}

    # --- line by line: V01-V05 ---------------------------------------------------------------------------------
    for line in graph.lines():
        where = f"{graph.relative(line.path)}:{line.number}"
        try:
            data = json.loads(line.raw)
        except json.JSONDecodeError as e:
            add("V01", where, f"not JSON: {e}")
            continue
        try:
            rec = RECORD_ADAPTER.validate_json(line.raw)
        except ValidationError as e:
            first = e.errors()[0]
            add("V01", where, f"invalid: {'.'.join(str(p) for p in first['loc'])}: {first['msg']}")
            continue
        # The stored id is kept as it is, so a bad id is reported once, as V03, not also as a form problem here.
        if canonical_line({**normalise(data), "id": data.get("id")}) != line.raw:
            add("V02", where, "not in canonical form (key order, spacing, a missing default, a written-out null, "
                              "or no final newline); records are written only through the tool")
        expected = record_id({k: v for k, v in data.items() if k != "id"})
        if rec.id != expected:
            add("V03", where, f"id {rec.id} does not match its content ({expected}); was it edited in place?")
        if rec.id in seen_ids:
            add("V04", where, f"id {rec.id} already appears at {seen_ids[rec.id]}")
        else:
            seen_ids[rec.id] = where
        if line.path.name != f"{rec.type}.jsonl":
            add("V05", where, f"a {rec.type} record in {line.path.name}")
        located.append(Located(rec, where))

    by_id: dict[str, Located] = {}
    for loc in located:
        by_id.setdefault(loc.record.id, loc)
    by_identifier: dict[tuple[str, str], list[Located]] = defaultdict(list)
    for loc in located:
        ident = getattr(loc.record, "identifier", None)
        if ident is not None:
            by_identifier[(loc.record.type, ident)].append(loc)
    identifier_index: dict[str, Located] = {}
    for (_t, ident), locs in by_identifier.items():
        identifier_index.setdefault(ident, locs[-1])
    raw_digests: dict[str, str] = {}
    for loc in located:
        r = loc.record
        if isinstance(r, m.Retrieval):
            raw_digests[r.generated] = loc.record.id
        elif isinstance(r, m.Run):
            for f in r.used_files:
                raw_digests.setdefault(f.sha256, loc.record.id)

    # --- V06: one current record per identifier ------------------------------------------------------------------
    revised = {loc.record.provenance.was_revision_of for loc in located
               if getattr(loc.record, "provenance", None) is not None and loc.record.provenance.was_revision_of}
    for (rtype, ident), locs in by_identifier.items():
        current = [loc for loc in locs if loc.record.id not in revised]
        if len(current) > 1:
            add("V06", current[-1].where, f"{len(current)} current {rtype} records for {ident}; a later one must "
                                          f"name the one it revises (was_revision_of)")

    # --- V07 and V14: references, and synthetic propagation ------------------------------------------------------
    def resolve(value: str) -> tuple[str | None, Located | None]:
        """(kind, target) — target is None for a raw digest that resolves, or when nothing resolves."""
        kind = reference_kind(value)
        if kind == "record_id":
            return kind, by_id.get(value)
        if kind == "raw_digest":
            return kind, None
        if kind is not None:
            return kind, identifier_index.get(value)
        return None, None

    for loc in located:
        r = loc.record
        for field, value, allowed in _references(r):
            kind, target = resolve(value)
            if kind is None:
                add("V07", loc.where, f"{field}: {value!r} is not a reference of any known form")
                continue
            if kind == "raw_digest":
                if value not in raw_digests:
                    add("V07", loc.where, f"{field}: {value} is not generated by any retrieval or read by any run")
                continue
            if target is None:
                add("V07", loc.where, f"{field}: {value} does not resolve")
                continue
            if allowed is not None and target.record.type not in allowed:
                add("V07", loc.where, f"{field}: {value} is a {target.record.type}, expected {'/'.join(allowed)}")
                continue
            if target.record.synthetic and not r.synthetic:
                add("V14", loc.where, f"{field}: uses synthetic {target.record.type} {value} but is not synthetic")

    # --- per-type content rules -------------------------------------------------------------------------------
    numberings = {loc.record.identifier: loc.record for loc in located if isinstance(loc.record, m.Numbering)}
    exons_by_transcript: dict[str, list[m.Exon]] = defaultdict(list)

    for loc in located:
        r, where = loc.record, loc.where
        if isinstance(r, m.Retrieval):
            _check_retrieval(graph, r, where, add)
        elif isinstance(r, m.Table):
            _check_table(graph, r, where, add)
        elif isinstance(r, m.Numbering):
            _check_numbering(r, where, add)
        elif isinstance(r, m.Residue):
            expected_ident = f"residue:{r.numbering.removeprefix('numbering:')}:{r.position}"
            if r.identifier != expected_ident:
                add("V11", where, f"identifier {r.identifier} does not match numbering and position")
            n = numberings.get(r.numbering)
            if n is not None:
                if r.position > n.length:
                    add("V11", where, f"position {r.position} beyond the numbering's length {n.length}")
                elif n.sequence[r.position - 1] != r.amino_acid:
                    add("V11", where, f"amino acid {r.amino_acid} but the numbering has "
                                      f"{n.sequence[r.position - 1]} at {r.position}")
        elif isinstance(r, m.Exon):
            _check_exon(r, where, add)
            exons_by_transcript[r.transcript].append(r)
        elif isinstance(r, m.Alignment):
            _check_alignment(r, where, add, numberings)
        elif isinstance(r, m.SearchResult):
            if r.n_hits != len(r.hits):
                add("V16", where, f"n_hits is {r.n_hits} but {len(r.hits)} hits are listed")
        elif isinstance(r, m.GeneLocus):
            if r.start > r.end:
                add("V17", where, f"start {r.start} after end {r.end}")
            expected_ident = f"locus:GRCh38:{r.sequence_accession}:{r.start}-{r.end}:{r.strand}"
            if r.identifier != expected_ident:
                add("V17", where, f"identifier {r.identifier} does not match its fields ({expected_ident})")

    for loc in located:  # V10, across records: a UniProt numbering names its isoform exactly when the entry has some
        p = loc.record
        if not isinstance(p, m.Protein):
            continue
        has_isoforms = bool(p.isoform_numberings)
        for num in [p.canonical_numbering, *p.isoform_numberings]:
            key = num.removeprefix("numbering:")
            if key.startswith(("NP_", "XP_")):
                continue
            qualified = "-" in key.split(".sv")[0]
            if has_isoforms and not qualified:
                add("V10", loc.where, f"{p.identifier} defines isoforms, so {num} must name its isoform")
            elif not has_isoforms and qualified:
                add("V10", loc.where, f"{p.identifier} defines no isoforms, so {num} must not name one")

    transcripts = {loc.record.identifier: loc for loc in located if isinstance(loc.record, m.Transcript)}
    for ident, exons in exons_by_transcript.items():
        t = transcripts.get(ident)
        if t is None:
            continue  # V07 has reported it
        tr: m.Transcript = t.record  # type: ignore[assignment]
        numbers = sorted(e.exon_number for e in exons)
        if numbers != list(range(1, tr.exon_count + 1)):
            add("V12", t.where, f"exon_count {tr.exon_count}, but exons numbered {numbers[:3]}...{numbers[-3:]} "
                                f"({len(numbers)} records)")
        total = sum(e.coding_length_nt for e in exons)
        if total != tr.cds_length_nt:
            add("V12", t.where, f"cds_length_nt {tr.cds_length_nt}, but its exons code {total} bases")
        coding = sorted((e for e in exons if e.c_start is not None), key=lambda e: e.exon_number)
        for a, b in zip(coding, coding[1:]):
            if b.c_start != a.c_end + 1:  # type: ignore[operator]
                add("V12", t.where, f"exon {a.exon_number} ends at c.{a.c_end} but exon {b.exon_number} "
                                    f"starts at c.{b.c_start}")
    return findings


def _check_retrieval(graph: Graph, r: m.Retrieval, where: str, add) -> None:
    if (r.source_release is None) == (r.source_release_absent is None):
        add("V15", where, "exactly one of source_release and source_release_absent must be given")
    if r.source_release is not None and not r.source_release_basis:
        add("V15", where, "source_release given without source_release_basis")
    if r.ended_at_time < r.started_at_time:
        add("V15", where, "ended before it started")
    prefix = "raw/" if r.storage == "committed" else "cache/"
    if not r.stored_at.startswith(prefix):
        add("V08", where, f"storage {r.storage} but stored_at {r.stored_at} is not under {prefix}")
        return
    try:
        p = graph.path(r.stored_at)
    except ValueError as e:
        add("V08", where, str(e))
        return
    if not p.is_file():
        if r.storage == "committed":
            add("V08", where, f"committed snapshot {r.stored_at} is missing")
        return  # a cache entry may be absent: its retrieval is the fetch pointer
    data = p.read_bytes()
    if "sha256:" + sha256_hex(data) != r.generated:
        add("V08", where, f"{r.stored_at} does not match the digest its retrieval recorded")
    if len(data) != r.response.bytes:
        add("V08", where, f"{r.stored_at} is {len(data)} bytes; its retrieval recorded {r.response.bytes}")


_INT = re.compile(r"^-?[0-9]+$")


def _check_table(graph: Graph, t: m.Table, where: str, add) -> None:
    try:
        p = graph.path(t.path)
    except ValueError as e:
        add("V09", where, str(e))
        return
    if not p.is_file():
        add("V09", where, f"{t.path} is missing")
        return
    data = p.read_bytes()
    if "sha256:" + sha256_hex(data) != t.sha256:
        add("V09", where, f"{t.path} does not match its recorded sha256")
    if len(data) != t.bytes:
        add("V09", where, f"{t.path} is {len(data)} bytes; its record says {t.bytes}")
    if b"\r" in data:
        add("V09", where, f"{t.path} contains carriage returns; tables are LF-only")
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines:
        add("V09", where, f"{t.path} has no header")
        return
    header = lines[0].split("\t")
    names = [c.name for c in t.columns]
    if header != names:
        add("V09", where, f"header {header} does not match the recorded columns {names}")
        return
    rows = [ln.split("\t") for ln in lines[1:]]
    if len(rows) != t.row_count:
        add("V09", where, f"{len(rows)} rows; its record says {t.row_count}")
    for key in t.primary_key:
        if key not in names:
            add("V09", where, f"primary key column {key} is not a column")
            return
    key_idx = [names.index(k) for k in t.primary_key]
    keys: set[tuple[str, ...]] = set()
    reported = 0
    for i, row in enumerate(rows, start=2):
        if reported >= 20:
            add("V09", where, "more problems not listed")
            break
        if len(row) != len(names):
            add("V09", where, f"line {i}: {len(row)} cells for {len(names)} columns")
            reported += 1
            continue
        k = tuple(row[j] for j in key_idx)
        if k in keys:
            add("V09", where, f"line {i}: duplicate key {k}")
            reported += 1
        keys.add(k)
        for col, cell in zip(t.columns, row):
            if cell == "":
                if col.required:
                    add("V09", where, f"line {i}: required column {col.name} is empty")
                    reported += 1
                continue
            ok = True
            if col.datatype == "integer":
                ok = bool(_INT.match(cell))
            elif col.datatype == "number":
                try:
                    ok = math.isfinite(float(cell))
                except ValueError:
                    ok = False
            elif col.datatype == "boolean":
                ok = cell in ("true", "false")
            if not ok:
                add("V09", where, f"line {i}: {col.name} = {cell!r} is not a {col.datatype}")
                reported += 1


def _check_numbering(n: m.Numbering, where: str, add) -> None:
    if len(n.sequence) != n.length:
        add("V10", where, f"length {n.length} but the sequence has {len(n.sequence)} residues")
    if refget_digest(n.sequence) != n.sequence_digest:
        add("V10", where, "sequence_digest does not match the sequence")
    if sequence_md5(n.sequence) != n.md5:
        add("V10", where, "md5 does not match the sequence")
    if n.accession.startswith(("NP_", "XP_")):
        expected = f"numbering:{n.accession}"
        if not n.accession.endswith(f".{n.sequence_version}"):
            add("V10", where, f"RefSeq accession {n.accession} does not carry sequence_version {n.sequence_version}")
    else:
        expected = f"numbering:{n.accession}.sv{n.sequence_version}"
    if n.identifier != expected:
        add("V10", where, f"identifier {n.identifier} does not match accession and version ({expected})")


def _check_exon(e: m.Exon, where: str, add) -> None:
    if e.genome_start > e.genome_end:
        add("V12", where, "genome_start after genome_end")
    acc = e.transcript.split(":", 1)[1]
    if e.identifier != f"exon:{acc}:{e.exon_number}":
        add("V12", where, f"identifier {e.identifier} does not match transcript and exon number")
    coding_fields = (e.coding_genome_start, e.coding_genome_end, e.c_start, e.c_end, e.first_residue,
                     e.last_residue, e.start_phase, e.end_phase, e.splits_codon_at_end)
    if e.coding_length_nt == 0:
        if any(v is not None for v in coding_fields):
            add("V12", where, "an untranslated exon carries coding values")
        if e.data_absent_reason is None:
            add("V12", where, "an untranslated exon must say why its coding values are absent")
        return
    if any(v is None for v in coding_fields) or e.residue_numbering is None:
        add("V12", where, "a coding exon must carry every coding field and its residue numbering")
        return
    assert e.c_start is not None and e.c_end is not None
    if e.c_end - e.c_start + 1 != e.coding_length_nt:
        add("V12", where, f"c.{e.c_start}..c.{e.c_end} is not {e.coding_length_nt} bases")
    if e.coding_genome_end - e.coding_genome_start + 1 != e.coding_length_nt:  # type: ignore[operator]
        add("V12", where, "the coding genome span is not coding_length_nt bases")
    if not (e.genome_start <= e.coding_genome_start <= e.coding_genome_end <= e.genome_end):  # type: ignore[operator]
        add("V12", where, "the coding span is not inside the exon")
    if e.start_phase != (e.c_start - 1) % 3:
        add("V12", where, f"start_phase {e.start_phase}, but (c_start - 1) mod 3 = {(e.c_start - 1) % 3}")
    if e.end_phase != e.c_end % 3:
        add("V12", where, f"end_phase {e.end_phase}, but c_end mod 3 = {e.c_end % 3}")
    if e.splits_codon_at_end != (e.c_end % 3 != 0):
        add("V12", where, "splits_codon_at_end disagrees with end_phase")
    if e.first_residue != (e.c_start + 2) // 3:
        add("V12", where, f"first_residue {e.first_residue}, but c.{e.c_start} is in codon {(e.c_start + 2) // 3}")
    if e.last_residue > (e.c_end + 2) // 3:  # type: ignore[operator]
        add("V12", where, f"last_residue {e.last_residue} is past c.{e.c_end}'s codon {(e.c_end + 2) // 3}")
    if e.data_absent_reason is not None:
        add("V12", where, "a coding exon carries a data_absent_reason")


_PATH = re.compile(r"([1-9][0-9]*)([MID])")


def _check_alignment(a: m.Alignment, where: str, add, numberings: dict[str, m.Numbering]) -> None:
    ops = [(int(n), op) for n, op in _PATH.findall(a.path)]
    cols = sum(n for n, _ in ops)
    pairs = sum(n for n, op in ops if op == "M")
    s_only = sum(n for n, op in ops if op == "I")
    o_only = sum(n for n, op in ops if op == "D")
    for name, got, want in (("n_columns", a.n_columns, cols), ("n_pairs", a.n_pairs, pairs),
                            ("n_subject_only", a.n_subject_only, s_only), ("n_object_only", a.n_object_only, o_only)):
        if got != want:
            add("V13", where, f"{name} is {got}, but the path gives {want}")
    if a.n_pairs and not math.isclose(a.identity, a.n_identical / a.n_pairs, rel_tol=0, abs_tol=1e-9):
        add("V13", where, f"identity {a.identity} is not n_identical / n_pairs = {a.n_identical / a.n_pairs}")
    s, o = numberings.get(a.subject), numberings.get(a.object)
    if s is None or o is None:
        return  # V07 reports the missing numbering
    if s.sequence_digest != a.subject_sequence_digest or o.sequence_digest != a.object_sequence_digest:
        add("V13", where, "a sequence digest does not match its numbering")
    if pairs + s_only != s.length or pairs + o_only != o.length:
        add("V13", where, f"the path covers {pairs + s_only} subject and {pairs + o_only} object residues; "
                          f"the numberings have {s.length} and {o.length}")
        return
    identical, i, j = 0, 0, 0
    for n, op in ops:
        for _ in range(n):
            if op == "M":
                identical += s.sequence[i] == o.sequence[j]
                i, j = i + 1, j + 1
            elif op == "I":
                i += 1
            else:
                j += 1
    if identical != a.n_identical:
        add("V13", where, f"n_identical is {a.n_identical}, but the sequences give {identical} along the path")
