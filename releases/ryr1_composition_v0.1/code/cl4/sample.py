"""sample.py - C5's sample, as the criteria fix it (*C5: the re-derivation, in detail*, *The sample*): the set residues
whose pig partner lies in CL-2's one departure; 30 others drawn by `random.Random(20261011).sample(others, 30)` from
the other set residues in ascending order; and the four worked residues (Q2, answered (c)). Each list is compared with
the one the criteria print, so a different reading stops the build."""
from __future__ import annotations

import random

from common import CL2, Inputs

PRINTED_NINE = [2764, 2776, 2787, 2840, 2843, 2867, 2880, 2885, 2910]
PRINTED_THIRTY = [33, 64, 71, 156, 177, 178, 248, 1075, 1342, 1583, 2130, 2224, 2321, 2346, 2363, 2435, 2458, 3118,
                  3217, 3218, 3253, 3290, 3402, 3985, 4283, 4638, 4664, 4725, 4733, 4856]
FOUR = [163, 522, 614, 2060]


def departure(inp: Inputs) -> tuple[int, int]:
    """The species range of CL-2's departing segments, which must be one range (P16960 2737-2940)."""
    _, segs = inp.table(CL2["segments"])
    ranges = {(int(s["species_first"]), int(s["species_last"])) for s in segs if s["departs"] == "true"}
    if len(ranges) != 1:
        raise SystemExit(f"CL-2's departing segments span {sorted(ranges)}, not one range")
    return ranges.pop()


def c5_sample(inp: Inputs, residues: list[int], partner_rows: list[dict], scope: str = "full_set") -> dict:
    lo, hi = departure(inp)
    pig = {r["human_position"]: r["partner_position"] for r in partner_rows if r["species"] == "Sus scrofa"}
    nine = sorted(h for h in residues if pig.get(h) is not None and lo <= pig[h] <= hi)
    others = sorted(h for h in residues if h not in nine)
    thirty = sorted(random.Random(20261011).sample(others, 30))
    if nine != PRINTED_NINE or thirty != PRINTED_THIRTY:
        raise SystemExit(f"C5's sample differs from the criteria's: nine {nine}, thirty {thirty}")
    if any(h not in residues for h in FOUR) or set(FOUR) & (set(nine) | set(thirty)):
        raise SystemExit("the four worked residues are not set residues apart from the nine and the thirty")
    if scope == "four_residues":
        return {"nine": [], "thirty": [], "four": FOUR, "all": FOUR, "departure": (lo, hi)}
    return {"nine": nine, "thirty": thirty, "four": FOUR, "all": sorted(nine + thirty + FOUR), "departure": (lo, hi)}
