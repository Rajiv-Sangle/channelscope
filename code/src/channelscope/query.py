"""Queries over the evidence graph, with DuckDB reading the JSONL records and TSV tables where they lie (ADR-001 §8).

`connect` exposes one view per record type, named after it, for ad hoc SQL. Competency questions are functions
with a fixed answer shape; CQ-02 is the first (M01's contract).
"""

from __future__ import annotations

from typing import Any

import duckdb

from . import models as m
from .graph import Graph
from .ids import parse_residue_identifier, residue_identifier


def _sql_path(graph: Graph, relative: str) -> str:
    return graph.path(relative).as_posix().replace("'", "''")


def connect(graph: Graph) -> duckdb.DuckDBPyConnection:
    """One view per record type, named after it. View names are quoted, since `table` is an SQL keyword: write
    `FROM "table"` for that one."""
    con = duckdb.connect()
    if graph.records_dir.is_dir():
        for f in sorted(graph.records_dir.glob("*.jsonl")):
            if f.stat().st_size == 0:
                continue
            p = f.as_posix().replace("'", "''")
            con.execute(f"CREATE VIEW \"{f.stem}\" AS SELECT * FROM read_json('{p}', format='newline_delimited', "
                        f"sample_size=-1, union_by_name=true)")
    return con


def current(records: list[m.Record]) -> list[m.Record]:
    """Records not revised by another record."""
    revised = {r.provenance.was_revision_of for r in records
               if getattr(r, "provenance", None) is not None and r.provenance.was_revision_of}
    return [r for r in records if r.id not in revised]


CQ02_FIELDS = ("residue", "other_numbering", "other_residue", "correspondence", "indel", "distance_to_indel",
               "ambiguous", "local_identity", "local_pairs", "local_identity_window", "reliability",
               "reliability_reasons", "mapping", "alignments", "methods")


def cq02(graph: Graph, residue: str) -> list[dict[str, Any]]:
    """CQ-02: for a residue, the corresponding residue in every other numbering the graph maps it to.

    One row per residue mapping that has the residue's numbering on either side: the other residue, or `None` with
    correspondence `no-correspondence`; the alignments and their methods with versions; local identity with its
    window and denominator; whether the position sits in an indel; and its reliability."""
    numbering, position = parse_residue_identifier(residue)
    records = current(graph.records())
    by_id = {r.id: r for r in records}
    mappings = [r for r in records if isinstance(r, m.ResidueMapping) and numbering in (r.subject, r.object)]
    con = duckdb.connect()
    answers = []
    for mp in sorted(mappings, key=lambda r: (r.object if r.subject == numbering else r.subject, r.id)):
        side, other_side, other = (("subject", "object", mp.object) if mp.subject == numbering
                                   else ("object", "subject", mp.subject))
        table = by_id[mp.table]
        assert isinstance(table, m.Table)
        rel = con.execute(
            f"SELECT * FROM read_csv('{_sql_path(graph, table.path)}', delim='\t', header=true, all_varchar=true, "
            f"quote='', escape='') WHERE {side}_position = ?", [str(position)])
        names = [d[0] for d in rel.description]
        hits = [dict(zip(names, row)) for row in rel.fetchall()]
        if len(hits) != 1:
            raise LookupError(f"{residue}: {len(hits)} rows in {table.path}; a position appears exactly once")
        h = hits[0]
        other_position = h[f"{other_side}_position"]
        methods = []
        for a in mp.alignments:
            aln = by_id[a]
            meth = by_id[aln.provenance.method]  # type: ignore[union-attr]
            methods.append(f"{meth.name} {meth.version}")  # type: ignore[union-attr]
        answers.append({
            "residue": residue,
            "other_numbering": other,
            "other_residue": residue_identifier(other, int(other_position)) if other_position else None,
            "correspondence": h["correspondence"],
            "indel": h["indel"],
            "distance_to_indel": int(h["distance_to_indel"]) if h["distance_to_indel"] else None,
            "ambiguous": h["ambiguous"] == "true",
            "local_identity": float(h["local_identity"]) if h["local_identity"] else None,
            "local_pairs": int(h["local_pairs"]),
            "local_identity_window": mp.local_identity_window,
            "reliability": h["reliability"],
            "reliability_reasons": h["reliability_reasons"].split(";") if h["reliability_reasons"] else [],
            "mapping": mp.id,
            "alignments": list(mp.alignments),
            "methods": methods,
        })
    return answers


def cq02_for_mapping(graph: Graph, mapping_id: str):
    """CQ-02, answered for one residue mapping only. CQ-02 answers once per mapping that holds the residue's
    numbering, so a check of one mapping reads that mapping's answer: once O4's mouse and pig mappings sit beside
    M01's rabbit one, a human residue has three answers (added 2026-10-06)."""
    def answer(residue: str) -> list[dict[str, Any]]:
        return [a for a in cq02(graph, residue) if a["mapping"] == mapping_id]
    return answer
