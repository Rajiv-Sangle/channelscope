"""Global pairwise alignment, two ways, for M01's residue mapping (objective 4). Pure: no network, no files.

Method A is Biopython's `PairwiseAligner`. Method B is parasail's `nw_trace`, a separately written C library, not a
wrapper around A (M01's check A3). Both score with BLOSUM62 and affine gaps, and score end gaps as internal ones: a
gap of length L scores `open + (L - 1) * extend`, the convention both libraries were measured to share on
2026-10-03. parasail scores in integers, so method B uses BLOSUM62 doubled, with the gap scores doubled too. That is
the same scoring scaled by two: it leaves every optimal alignment unchanged and doubles the score.

Paths use the alignment record's run-length alphabet (models.Alignment): `M` pairs a subject residue with an object
residue, `I` is a subject residue against a gap, `D` an object residue against a gap.

An optimal global alignment is often not unique. Method A enumerates every alignment of optimal score and keeps:
- the count;
- the positions whose partner differs between them, which the mapping flags *ambiguous* (A3);
- one representative, the 3'-most, by the same convention as HGVS's 3' rule. Its first gap column is as late as any
  optimal alignment's, then its second, and so on.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mapping import columns_from_path

STANDARD = "ARNDCQEGHILKMFPSTWYV"


@dataclass(frozen=True)
class Scoring:
    matrix: str = "BLOSUM62"
    open_gap_score: float = -10.0  # the score of a gap's first position
    extend_gap_score: float = -0.5  # the score of each further position
    end_gaps: str = "as internal gaps"

    def parameters(self) -> dict:
        return {"mode": "global", "substitution_matrix": self.matrix, "open_gap_score": self.open_gap_score,
                "extend_gap_score": self.extend_gap_score, "end_gaps": self.end_gaps}


def run_length(ops: list[tuple[int, str]]) -> str:
    merged: list[list] = []
    for n, op in ops:
        if n <= 0:
            continue
        if merged and merged[-1][1] == op:
            merged[-1][0] += n
        else:
            merged.append([n, op])
    return "".join(f"{n}{op}" for n, op in merged)


def path_from_coordinates(coordinates) -> str:
    """A Biopython alignment's `coordinates` (row 0 the subject, row 1 the object) as a run-length path."""
    ops = []
    for k in range(coordinates.shape[1] - 1):
        ds = int(coordinates[0, k + 1] - coordinates[0, k])
        do = int(coordinates[1, k + 1] - coordinates[1, k])
        if ds and do:
            if ds != do:
                raise ValueError("an aligned block of unequal lengths")
            ops.append((ds, "M"))
        elif ds:
            ops.append((ds, "I"))
        elif do:
            ops.append((do, "D"))
    return run_length(ops)


def path_from_cigar(cigar: str) -> str:
    """A parasail CIGAR string (`=` and `X` pairs, `I` a query residue against a gap, `D` a reference residue against
    a gap) as a run-length path, with the query as the subject."""
    ops, n = [], ""
    for ch in cigar:
        if ch.isdigit():
            n += ch
            continue
        if ch in "=XM":
            ops.append((int(n), "M"))
        elif ch in "ID":
            ops.append((int(n), ch))
        else:
            raise ValueError(f"unexpected CIGAR operation {ch!r}")
        n = ""
    if n:
        raise ValueError("a CIGAR string ending in a count")
    return run_length(ops)


def gap_columns(path: str) -> tuple[int, ...]:
    return tuple(c.column for c in columns_from_path(path) if c.subject_position is None or c.object_position is None)


def three_prime(paths: list[str]) -> str:
    """The 3'-most of several alignments: the latest first gap column, then the latest second, and so on."""
    return max(paths, key=gap_columns)


def partners(path: str) -> tuple[dict[int, int | None], dict[int, int | None]]:
    """Each subject position's object partner, and each object position's subject partner (None for a gap)."""
    subj, obj = {}, {}
    for c in columns_from_path(path):
        if c.subject_position is not None:
            subj[c.subject_position] = c.object_position
        if c.object_position is not None:
            obj[c.object_position] = c.subject_position
    return subj, obj


def counts(subject: str, obj: str, path: str) -> dict[str, int]:
    cols = columns_from_path(path)
    pairs = [c for c in cols if c.subject_position and c.object_position]
    return {"n_columns": len(cols), "n_pairs": len(pairs),
            "n_identical": sum(subject[c.subject_position - 1] == obj[c.object_position - 1] for c in pairs),
            "n_subject_only": sum(1 for c in cols if c.object_position is None),
            "n_object_only": sum(1 for c in cols if c.subject_position is None)}


@dataclass(frozen=True)
class OptimalSet:
    """Every alignment of optimal score, as method A finds them."""

    score: float
    count: int
    paths: tuple[str, ...]  # distinct paths, sorted
    representative: str
    ambiguous_subject: frozenset[int]
    ambiguous_object: frozenset[int]

    def ambiguous_columns(self, path: str) -> frozenset[int]:
        """The columns of `path` whose subject or object residue has more than one partner across the set."""
        return frozenset(c.column for c in columns_from_path(path)
                         if (c.subject_position in self.ambiguous_subject)
                         or (c.object_position in self.ambiguous_object))


def biopython_aligner(scoring: Scoring):
    from Bio.Align import PairwiseAligner, substitution_matrices

    return PairwiseAligner(mode="global", substitution_matrix=substitution_matrices.load(scoring.matrix),
                           open_gap_score=scoring.open_gap_score, extend_gap_score=scoring.extend_gap_score)


def method_a(subject: str, obj: str, scoring: Scoring, limit: int = 100_000) -> OptimalSet:
    """Biopython: the optimal score, and every alignment that reaches it (refused above `limit`)."""
    aligner = biopython_aligner(scoring)
    for name in ("open_left_insertion_score", "open_right_insertion_score", "open_left_deletion_score",
                 "open_right_deletion_score"):
        if getattr(aligner, name) != scoring.open_gap_score:
            raise ValueError(f"{name} is {getattr(aligner, name)}: end gaps are not scored as internal ones")
    for name in ("extend_left_insertion_score", "extend_right_insertion_score", "extend_left_deletion_score",
                 "extend_right_deletion_score"):
        if getattr(aligner, name) != scoring.extend_gap_score:
            raise ValueError(f"{name} is {getattr(aligner, name)}: end gaps are not scored as internal ones")
    alignments = aligner.align(subject, obj)
    n = len(alignments)
    if n > limit:
        raise ValueError(f"{n} optimal alignments; enumerating more than {limit} is refused")
    paths = sorted({path_from_coordinates(a.coordinates) for a in alignments})
    seen_s: dict[int, set] = {}
    seen_o: dict[int, set] = {}
    for p in paths:
        s_map, o_map = partners(p)
        for k, v in s_map.items():
            seen_s.setdefault(k, set()).add(v)
        for k, v in o_map.items():
            seen_o.setdefault(k, set()).add(v)
    return OptimalSet(score=float(alignments.score), count=n, paths=tuple(paths), representative=three_prime(paths),
                      ambiguous_subject=frozenset(k for k, v in seen_s.items() if len(v) > 1),
                      ambiguous_object=frozenset(k for k, v in seen_o.items() if len(v) > 1))


def parasail_matrix(scale: int):
    """parasail's BLOSUM62, every entry multiplied by `scale`. Refused unless parasail's own BLOSUM62 equals
    Biopython's on all 400 pairs of the standard amino acids."""
    import parasail
    from Bio.Align import substitution_matrices

    base, bio = parasail.blosum62, substitution_matrices.load("BLOSUM62")
    index = {x: int(base.mapper[ord(x)]) for x in STANDARD}  # parasail's own map from a letter to its row
    for x in STANDARD:
        for y in STANDARD:
            if int(base.matrix[index[x], index[y]]) != int(bio[x][y]):
                raise ValueError(f"parasail's BLOSUM62 gives {x}{y} a different score from Biopython's")
    m = base.copy()
    for i in range(base.size):
        for j in range(base.size):
            m.set_value(i, j, scale * int(base.matrix[i, j]))
    return m


def method_b(subject: str, obj: str, scoring: Scoring, scale: int = 2) -> tuple[str, int]:
    """parasail's `nw_trace`: one optimal path, and its score in method B's units (the scale times method A's)."""
    import parasail

    open_, extend = -scoring.open_gap_score * scale, -scoring.extend_gap_score * scale
    if open_ != int(open_) or extend != int(extend):
        raise ValueError("the scaled gap scores are not integers")
    result = parasail.nw_trace(subject, obj, int(open_), int(extend), parasail_matrix(scale))
    if result.cigar.beg_query != 0 or result.cigar.beg_ref != 0:
        raise ValueError("parasail's global alignment does not begin at both sequences' first residues")
    return path_from_cigar(result.cigar.decode), int(result.score)


def library_versions() -> dict[str, str]:
    import Bio
    import parasail

    return {"biopython": Bio.__version__, "parasail_python": parasail.__version__,
            "parasail_c": ".".join(str(x) for x in parasail.version())}
