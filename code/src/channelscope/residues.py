"""Residue positions across a protein's isoforms: refused unless translated explicitly (M01's A2). Pure.

One residue number means different residues on different isoforms: P21817-2 lacks 3481-3485 and P21817-3 lacks
3865-3869, so every position after a deletion is offset. A position on an isoform is therefore refused unless the
caller asks for an explicit translation, which is made from the two sequences themselves and says what it did.
"""

from __future__ import annotations

from dataclasses import dataclass


class IsoformRefused(ValueError):
    """A position on a non-canonical isoform, given where a canonical position is needed."""


@dataclass(frozen=True)
class Deletion:
    start: int  # first canonical residue missing from the isoform
    end: int    # last one


def deletion_between(canonical: str, isoform: str) -> Deletion:
    """The one contiguous stretch of `canonical` that `isoform` lacks, found from the sequences alone."""
    k = len(canonical) - len(isoform)
    if k <= 0:
        raise ValueError("the isoform is not shorter than the canonical sequence")
    prefix = 0
    while prefix < len(isoform) and canonical[prefix] == isoform[prefix]:
        prefix += 1
    if canonical[prefix + k:] != isoform[prefix:]:
        raise ValueError("the isoform differs by more than one deletion; no single translation exists")
    # Report the leftmost placement, the convention UniProt's VSP features follow for a deletion in a repeat.
    return Deletion(prefix + 1, prefix + k)


def to_canonical(isoform_numbering: str, canonical_numbering: str, position: int, canonical: str, isoform: str,
                 *, explicit: bool = False) -> tuple[str, int, str]:
    """(canonical numbering, canonical position, how it was translated). Refuses unless `explicit`."""
    if isoform_numbering == canonical_numbering:
        return canonical_numbering, position, "same numbering"
    if not explicit:
        raise IsoformRefused(f"{isoform_numbering}:{position} is not a position on {canonical_numbering}; ask for an "
                             f"explicit translation")
    d = deletion_between(canonical, isoform)
    if position < d.start:
        return canonical_numbering, position, f"before the deletion {d.start}-{d.end}: unchanged"
    shift = d.end - d.start + 1
    return canonical_numbering, position + shift, f"after the deletion {d.start}-{d.end}: +{shift}"
