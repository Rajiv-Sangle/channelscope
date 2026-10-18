"""synthetic.py - check C11-S's synthetic chains, committed with the build's code before the build (the criteria,
C11-S): one for each of rules 1 to 9 of L2's step 3, one for step 2's R11c, one with a withdrawn join inside M, and
one whose flank offsets fall (d(L) > d(R)). Each is a chain written as CL-2's tables would write it (segment rows,
exceptions rows and a chain row), a partner position p, the author numbers of joins C5-S withdrew, and the expected
answer: status, deciding rule, reason and the author number shown. Both the build's status function and C10's read
the rows with their own code. Data only: this module imports nothing of the build's."""
from __future__ import annotations

R11C = "short departing run, path A only (R11c): not joined"


def seg(n, status, first, last, offset=None, identity_low=False, r11c=False, gaps="-", joined=None):
    placed = status in ("agree", "path A only")
    span = [a for a in range(first, last + 1)]
    return {"segment": str(n), "status": status, "author_first": str(first), "author_last": str(last),
            "offset_s": str(offset) if status == "agree" else "", "offset_a": str(offset) if placed else "",
            "species_first": str(first + offset) if placed else "", "species_last": str(last + offset) if placed
            else "", "n_residues": str(len(span)), "unmodelled_gaps": gaps,
            "identity_low": "true" if identity_low else "false",
            "short_departing_run_path_a": "true" if r11c else "false",
            "joined_residues": str(joined if joined is not None else (len(span) if placed and not identity_low
                                                                        and not r11c else 0)),
            "label_first": str(first), "departs": "false"}


def exc(kind, first, last=None, joined="false", partners="", note="", n=None):
    last = first if last is None else last
    return {"kind": kind, "author_first": str(first), "author_last": str(last), "ins_code": "",
            "path_a_partners": partners, "joined": joined, "declared": "", "note": note,
            "n_residues": str(n if n is not None else last - first + 1)}


NOTE_NONE = "SIFTS gives a position for 0 (-); not used"

CASES = [
    {"name": "rule1", "p": 11, "withdrawn": [],
     "segments": [seg(1, "neither path", 10, 12)],
     "exceptions": [exc("neither path", 10), exc("neither path", 11), exc("neither path", 12)],
     "expect": ("not determinable", "step3-r1", "the chain has no joined residue", None)},
    {"name": "rule2", "p": 23, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "agree", 21, 40, 5)], "exceptions": [],
     "expect": ("not modelled", "step3-r2", "", None)},
    {"name": "rule3", "p": 22, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "path A only", 21, 21, 0, identity_low=True),
                  seg(3, "agree", 22, 40, 2)],
     "exceptions": [exc("identity low", 21)],
     "expect": ("not determinable", "step3-r3", "CL-2 places the residue at author 21 at species position 21", None)},
    {"name": "rule4", "p": 50, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "path A only", 21, 21, 40, identity_low=True),
                  seg(3, "agree", 100, 120, 0)],
     "exceptions": [exc("identity low", 21)],
     "expect": ("not modelled", "step3-r4", "", None)},
    {"name": "rule5", "p": 25, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "neither path", 21, 21), seg(3, "agree", 22, 40, 5)],
     "exceptions": [exc("neither path", 21, partners="22,25")],
     "expect": ("not determinable", "step3-r5", "the residue at author 21 is ambiguous on path A (partners 22 25)",
                None)},
    {"name": "rule6", "p": 22, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "UNK", 21, 23), seg(3, "agree", 24, 40, 0)],
     "exceptions": [exc("UNK", 21, 23, joined="", note=NOTE_NONE, n=3)],
     "expect": ("modelled, not placed", "step3-r6", "UNK, placed by its order between the flanks", 22)},
    {"name": "rule7", "p": 23, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "UNK", 21, 25), seg(3, "agree", 30, 40, 2)],
     "exceptions": [exc("UNK", 21, 25, joined="", note="SIFTS gives a position for 5 (21-25); not used", n=5)],
     "expect": ("modelled, not placed", "step3-r7", "UNK, author number and SIFTS agree", 23)},
    {"name": "rule8", "p": 28, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "UNK", 21, 25), seg(3, "agree", 30, 40, 2)],
     "exceptions": [exc("UNK", 21, 25, joined="", note="SIFTS gives a position for 5 (21-25); not used", n=5)],
     "expect": ("not modelled", "step3-r8", "", None)},
    {"name": "rule9", "p": 23, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "UNK", 21, 25), seg(3, "agree", 50, 60, 0)],
     "exceptions": [exc("UNK", 21, 25, joined="", note="SIFTS gives a position for 5 (31-35); not used", n=5)],
     "expect": ("not determinable", "step3-r9", "UNK, author 21-25, SIFTS 31-35", None)},
    {"name": "step2_r11c", "p": 100, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "path A only", 21, 21, 79, r11c=True), seg(3, "agree", 22, 40, 0)],
     "exceptions": [exc(R11C, 21)],
     "expect": ("not determinable", "step2-r11c", R11C, 21)},
    {"name": "withdrawn_in_m", "p": 25, "withdrawn": [21],
     "segments": [seg(1, "agree", 1, 20, 0), seg(2, "path A only", 21, 21, 0), seg(3, "agree", 30, 40, 0)],
     "exceptions": [],
     "expect": ("not determinable", "step3-r9", "withdrawn join, author 21", None)},
    {"name": "falling_offsets", "p": 27, "withdrawn": [],
     "segments": [seg(1, "agree", 1, 20, 6), seg(2, "path A only", 21, 21, 100, identity_low=True),
                  seg(3, "agree", 25, 40, 3)],
     "exceptions": [exc("identity low", 21)],
     "expect": ("not determinable", "step3-r3", "CL-2 places the residue at author 21 at species position 121",
                None)},
]


def tables(case: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """The case's rows as CL-2's three tables hold them: entry SYN, chain S, species Sus scrofa."""
    entry = "SYN_" + case["name"]
    segs = [{"entry": entry, "chain": "S", **s} for s in case["segments"]]
    excs = [{"entry": entry, "chain": "S", **x} for x in case["exceptions"]]
    joined = sum(int(s["joined_residues"]) for s in segs)
    entries = [{"entry": entry, "scope": "entry", "chain": "", "species": "Sus scrofa", "joined": ""},
               {"entry": entry, "scope": "chain", "chain": "S", "species": "Sus scrofa", "joined": str(joined)}]
    return entries, segs, excs
