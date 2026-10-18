"""Residue mappings from recorded alignments: the per-column table that CQ-02 reads. Pure: no network, no files.

One row per alignment column. A residue in an insertion or deletion maps to no residue, never to a neighbour
(M01's A4). Local identity travels with its denominator, the number of pairs in the window (ADR-001 §6, rule 2).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Column

PATH_OP = re.compile(r"([1-9][0-9]*)([MID])")

MAPPING_COLUMNS: list[Column] = [
    Column(name="column", datatype="integer", required=True, description="The alignment column, 1-based."),
    Column(name="subject_position", datatype="integer", required=False,
           description="The subject residue in this column; empty where the subject has a gap."),
    Column(name="subject_residue", datatype="string", required=False,
           description="The subject's amino acid in this column."),
    Column(name="object_position", datatype="integer", required=False,
           description="The object residue in this column; empty where the object has a gap."),
    Column(name="object_residue", datatype="string", required=False,
           description="The object's amino acid in this column."),
    Column(name="correspondence", datatype="string", required=True,
           description="`pair` where both residues are present; `no-correspondence` where one side is a gap."),
    Column(name="indel", datatype="string", required=True,
           description="`none`; `subject-only` (a subject residue against a gap, an insertion in the subject); "
                       "or `object-only`."),
    Column(name="distance_to_indel", datatype="integer", required=False,
           description="Columns to the nearest indel column (0 inside one); empty if the alignment has none."),
    Column(name="ambiguous", datatype="boolean", required=True,
           description="True where alignments of equal score, or the two methods, place this column differently."),
    Column(name="local_identity", datatype="number", required=False,
           description="Identical pairs / pairs, over the columns within the window; empty if the window holds no "
                       "pair."),
    Column(name="local_pairs", datatype="integer", required=True,
           description="The number of pairs in the window: local_identity's denominator."),
    Column(name="reliability", datatype="string", required=True,
           description="`standard`, or `lowered` for the reasons given."),
    Column(name="reliability_reasons", datatype="string", required=False,
           description="Semicolon-separated reason codes for a lowered reliability."),
]
MAPPING_HEADER = [c.name for c in MAPPING_COLUMNS]


@dataclass(frozen=True)
class AlignedColumn:
    column: int
    subject_position: int | None
    object_position: int | None


def columns_from_path(path: str) -> list[AlignedColumn]:
    out, i, j, col = [], 0, 0, 0
    for n, op in PATH_OP.findall(path):
        for _ in range(int(n)):
            col += 1
            if op == "M":
                i, j = i + 1, j + 1
                out.append(AlignedColumn(col, i, j))
            elif op == "I":
                i += 1
                out.append(AlignedColumn(col, i, None))
            else:
                j += 1
                out.append(AlignedColumn(col, None, j))
    return out


def path_from_columns(columns: list[AlignedColumn]) -> str:
    ops: list[list] = []
    for c in columns:
        op = "M" if c.subject_position and c.object_position else ("I" if c.subject_position else "D")
        if ops and ops[-1][1] == op:
            ops[-1][0] += 1
        else:
            ops.append([1, op])
    return "".join(f"{n}{op}" for n, op in ops)


def mapping_rows(subject: str, obj: str, path: str, window: int, ambiguous_columns: frozenset[int] = frozenset(),
                 lowered: dict[int, list[str]] | None = None) -> list[list]:
    """Rows of the mapping table, in MAPPING_HEADER order.

    `lowered` maps a column to reason codes that lower its reliability (feature-based rules, applied by the
    caller); `near-indel` (within `window` columns of an indel) and `ambiguous` are added here."""
    cols = columns_from_path(path)
    if sum(1 for c in cols if c.subject_position) != len(subject) or \
            sum(1 for c in cols if c.object_position) != len(obj):
        raise ValueError("the path does not cover both sequences exactly")
    indel_cols = [c.column for c in cols if c.subject_position is None or c.object_position is None]
    is_pair = [c.subject_position is not None and c.object_position is not None for c in cols]
    same = [p and subject[c.subject_position - 1] == obj[c.object_position - 1] for p, c in zip(is_pair, cols)]
    rows = []
    for k, c in enumerate(cols):
        lo, hi = max(0, k - window), min(len(cols), k + window + 1)
        pairs = sum(is_pair[lo:hi])
        ident = sum(same[lo:hi]) / pairs if pairs else None
        dist = min((abs(c.column - x) for x in indel_cols), default=None)
        reasons = list((lowered or {}).get(c.column, []))
        if dist is not None and dist <= window:
            reasons.append("near-indel")
        if c.column in ambiguous_columns:
            reasons.append("ambiguous")
        reasons = sorted(set(reasons))
        pair = is_pair[k]
        rows.append([
            c.column,
            c.subject_position, subject[c.subject_position - 1] if c.subject_position else None,
            c.object_position, obj[c.object_position - 1] if c.object_position else None,
            "pair" if pair else "no-correspondence",
            "none" if pair else ("subject-only" if c.subject_position else "object-only"),
            dist,
            c.column in ambiguous_columns,
            round(ident, 6) if ident is not None else None,
            pairs,
            "lowered" if reasons else "standard",
            ";".join(reasons) if reasons else None,
        ])
    return rows
