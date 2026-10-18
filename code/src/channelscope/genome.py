"""From GRCh38 to protein, for one transcript: the per-base codon map, HGVS c. positions, and translation. Pure.

The strand is read from the annotation and passed in; nothing here assumes the plus strand (M01's G3), and a minus-
strand gene is exercised by the tests. A genome position is accepted only with its assembly, and only GRCh38 (G5).

HGVS c. numbering, as hgvs-nomenclature.org states it (checked 2026-09-29): c.1 is the A of the start codon; c.-N
counts upstream of it and c.*N downstream of the stop codon; there is no c.0. An intron's 5' half is numbered from
the upstream exon's last base with `+`, its 3' half from the downstream exon's first base with `-`, and the central
base of an intron with an odd number of bases takes the upstream `+`.
"""

from __future__ import annotations

from dataclasses import dataclass

_BASES = "TCAG"
# NCBI translation table 1 (the standard code), in its own TCAG order; pinned by tests and, live, against NCBI.
TABLE_1 = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
STANDARD_CODE = {a + b + c: TABLE_1[16 * i + 4 * j + k]
                 for i, a in enumerate(_BASES) for j, b in enumerate(_BASES) for k, c in enumerate(_BASES)}
_COMPLEMENT = str.maketrans("ACGT", "TGCA")


class AssemblyRefused(ValueError):
    """A genome position without its assembly, or on an assembly other than GRCh38."""


def translate(cds: str) -> str:
    if len(cds) % 3:
        raise ValueError(f"a coding sequence of {len(cds)} bases is not a whole number of codons")
    try:
        return "".join(STANDARD_CODE[cds[i:i + 3]] for i in range(0, len(cds), 3))
    except KeyError as e:
        raise ValueError(f"codon {e.args[0]!r} is not four-letter DNA; refusing to guess its amino acid") from None


def reverse_complement(seq: str) -> str:
    if set(seq) - set("ACGT"):
        raise ValueError("only ACGT can be complemented here")
    return seq.translate(_COMPLEMENT)[::-1]


@dataclass(frozen=True)
class Exon:
    number: int
    start: int  # GRCh38, 1-based, inclusive; start <= end whatever the strand
    end: int


@dataclass(frozen=True)
class TranscriptModel:
    """One annotation's exon model. `cds_start` and `cds_end` are the lowest and highest genome coordinates of the
    coding sequence, stop codon included, whatever the strand."""

    accession: str
    strand: str
    exons: tuple[Exon, ...]  # in transcript order: exon 1 first
    cds_start: int
    cds_end: int

    def __post_init__(self) -> None:
        if self.strand not in ("+", "-"):
            raise ValueError(f"strand {self.strand!r}: read it from the annotation as + or -, never assume it")
        if [e.number for e in self.exons] != list(range(1, len(self.exons) + 1)):
            raise ValueError("exons must be numbered 1..n in transcript order")
        for a, b in zip(self.exons, self.exons[1:]):
            ok = a.end < b.start if self.strand == "+" else b.end < a.start
            if not ok:
                raise ValueError(f"exons {a.number} and {b.number} overlap or are out of transcript order")
        if any(e.start > e.end for e in self.exons) or self.cds_start > self.cds_end:
            raise ValueError("a start after its end")


@dataclass(frozen=True)
class GenomeWindow:
    """A stretch of one GRCh38 chromosome sequence, plus strand."""

    sequence_accession: str
    start: int  # the 1-based coordinate of seq[0]
    seq: str

    def base(self, pos: int) -> str:
        if not self.start <= pos < self.start + len(self.seq):
            raise ValueError(f"{pos} is outside the fetched window {self.start}-{self.start + len(self.seq) - 1}")
        return self.seq[pos - self.start]


@dataclass(frozen=True)
class MapRow:
    genome_position: int
    exon_number: int
    transcript_position: int
    c_hgvs: str
    c_position: int | None
    region: str  # 5utr, cds or 3utr
    codon_number: int | None
    codon_position: int | None
    residue_number: int | None
    genome_base: str
    transcript_base: str
    codon: str | None
    amino_acid: str | None
    split_codon: bool | None
    data_absent_reason: str | None


def _walk(model: TranscriptModel) -> list[tuple[int, int]]:
    """(genome position, exon number) for every exonic base, in transcript order."""
    out = []
    for e in model.exons:
        rng = range(e.start, e.end + 1) if model.strand == "+" else range(e.end, e.start - 1, -1)
        out.extend((p, e.number) for p in rng)
    return out


def _c_label(i: int, i0: int, i1: int) -> tuple[str, int | None, str]:
    if i < i0:
        return f"c.-{i0 - i}", None, "5utr"
    if i <= i1:
        return f"c.{i - i0 + 1}", i - i0 + 1, "cds"
    return f"c.*{i - i1}", None, "3utr"


def codon_map(model: TranscriptModel, window: GenomeWindow) -> list[MapRow]:
    """One row per exonic base of the transcript, in transcript order."""
    walk = _walk(model)
    index = {g: i for i, (g, _) in enumerate(walk)}
    first = model.cds_start if model.strand == "+" else model.cds_end  # the A of the start codon
    last = model.cds_end if model.strand == "+" else model.cds_start   # the last base of the stop codon
    if first not in index or last not in index:
        raise ValueError("the coding sequence's ends do not lie in the transcript's exons")
    i0, i1 = index[first], index[last]
    tx = []
    for g, _ in walk:
        b = window.base(g)
        tx.append(b if model.strand == "+" else reverse_complement(b))
    cds_len = i1 - i0 + 1
    if cds_len % 3:
        raise ValueError(f"the coding sequence is {cds_len} bases, not a whole number of codons")
    n_codons = cds_len // 3
    codon_exons: dict[int, set[int]] = {}
    for i in range(i0, i1 + 1):
        codon_exons.setdefault((i - i0) // 3 + 1, set()).add(walk[i][1])
    rows = []
    for i, (g, exon) in enumerate(walk):
        label, c_pos, region = _c_label(i, i0, i1)
        codon_number = codon_position = residue = codon = aa = split = reason = None
        if c_pos is not None:
            codon_number, codon_position = (c_pos - 1) // 3 + 1, (c_pos - 1) % 3 + 1
            start = i0 + (codon_number - 1) * 3
            codon = "".join(tx[start:start + 3])
            aa = STANDARD_CODE.get(codon)
            split = len(codon_exons[codon_number]) > 1
            residue = codon_number if codon_number < n_codons else None
        if residue is None:
            reason = "not-applicable"  # untranslated base, or the stop codon: no residue by definition
        rows.append(MapRow(g, exon, i + 1, label, c_pos, region, codon_number, codon_position, residue,
                           window.base(g), tx[i], codon, aa, split, reason))
    return rows


def coding_sequence(rows: list[MapRow]) -> str:
    return "".join(r.transcript_base for r in rows if r.region == "cds")


def split_codons_in_map(rows: list[MapRow]) -> int:
    return len({r.codon_number for r in rows if r.split_codon})


def split_codons_from_exon_model(model: TranscriptModel) -> int:
    """Codons split by an intron, counted from exon and CDS coordinates alone, with no per-base walk: every coding
    exon boundary that falls inside a codon splits one (G3's independent recount)."""
    lengths = [max(0, min(e.end, model.cds_end) - max(e.start, model.cds_start) + 1) for e in model.exons]
    coding = [n for n in lengths if n > 0]
    count, total = 0, 0
    for n in coding[:-1]:
        total += n
        count += total % 3 != 0
    return count


def locate(model: TranscriptModel, rows: list[MapRow], position: int, assembly: str | None) -> dict:
    """Where a GRCh38 position falls on the transcript. Refuses a position without its assembly, or on another
    assembly (G5). An intronic or untranslated position has no residue, and says why."""
    if assembly != "GRCh38":
        raise AssemblyRefused(f"position {position} given on {assembly!r}; only GRCh38 positions are accepted, "
                              f"each with its assembly named")
    by_genome = {r.genome_position: r for r in rows}
    if position in by_genome:
        r = by_genome[position]
        return {"where": "exon", "exon_number": r.exon_number, "c_hgvs": r.c_hgvs, "c_position": r.c_position,
                "residue_number": r.residue_number, "data_absent_reason": r.data_absent_reason, "row": r}
    downstream = (lambda a, b: a < b) if model.strand == "+" else (lambda a, b: a > b)
    for a, b in zip(model.exons, model.exons[1:]):
        a_last = a.end if model.strand == "+" else a.start
        b_first = b.start if model.strand == "+" else b.end
        if downstream(a_last, position) and downstream(position, b_first):
            up, down = abs(position - a_last), abs(b_first - position)
            label = (f"{by_genome[a_last].c_hgvs}+{up}" if up <= down else f"{by_genome[b_first].c_hgvs}-{down}")
            return {"where": "intron", "intron_number": a.number, "c_hgvs": label, "c_position": None,
                    "residue_number": None, "data_absent_reason": "not-applicable"}
    return {"where": "outside the transcript", "c_hgvs": None, "c_position": None, "residue_number": None,
            "data_absent_reason": "not-applicable"}
