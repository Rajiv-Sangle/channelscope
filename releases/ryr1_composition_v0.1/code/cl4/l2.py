"""l2.py - L2, the structures that model a set residue: CL-2's tables read by the criteria's rule (*L2*, *Reading
CL-2's tables*, *The status of each row*), the reading's guards (check C11), and the residue types in the mmCIF files.

A chain's residues come from its segment rows only. A placed residue has a species position (status `agree`, by
`offset_s`, or `path A only`, by `offset_a`); a joined one is placed, in a segment neither identity-low nor a short
departing run (R11c), and has no exceptions row (not UNK) with `joined` false. The status function takes the chain,
the partner position p and the joins C5-S withdrew, and returns the status, the join path, the reason, the author
number shown and the rule that decided (`step2-…`, `step3-r1` … `step3-r9`).
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from common import CL2, Inputs

R11C = "short departing run, path A only (R11c): not joined"
UNK_NOTE = re.compile(r"^SIFTS gives a position for (\d+) \((?:(\d+)-(\d+)|-)\); not used$")


def gaps(cell: str) -> set[int]:
    out: set[int] = set()
    if cell in ("", "-"):
        return out
    for part in cell.split(","):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


@dataclass
class Res:
    n: int
    seg: int
    status: str
    species: int | None
    joined: bool
    kinds: list[str]  # the kinds of its exceptions rows with `joined` false, in the table's order
    r11c_only: bool


@dataclass
class Chain:
    entry: str
    chain: str
    species: str
    residues: list[Res] = field(default_factory=list)
    unk: list[dict] = field(default_factory=list)  # UNK exceptions rows: author range, n, SIFTS range or None
    neither: dict = field(default_factory=dict)  # author n -> its `path_a_partners`, as listed
    declared: dict = field(default_factory=dict)  # author n -> `declared`, for a declared difference

    def placed_at(self, p: int) -> Res | None:
        if not hasattr(self, "_placed"):
            self._placed = {}
            for r in self.residues:
                if r.species is not None:
                    self._placed.setdefault(r.species, r)
        return self._placed.get(p)

    def joined_without(self, withdrawn: frozenset) -> tuple[list[Res], list[int]]:
        """The joined residues less the withdrawn, in author order, and their species positions (cached)."""
        if not hasattr(self, "_joined"):
            self._joined = {}
        if withdrawn not in self._joined:
            js = [r for r in self.residues if r.joined and r.n not in withdrawn]
            self._joined[withdrawn] = (js, [r.species for r in js])
        return self._joined[withdrawn]

    def between(self, lo: float, hi: float) -> list[Res]:
        import bisect
        if not hasattr(self, "_authors"):
            self._authors = [r.n for r in self.residues]
        i = bisect.bisect_right(self._authors, lo) if lo != float("-inf") else 0
        j = bisect.bisect_left(self._authors, hi) if hi != float("inf") else len(self._authors)
        return self.residues[i:j]


class CL2Reading:
    """CL-2's three tables, read once (or the synthetic chains' rows, check C11-S). `segments_edit` and
    `exceptions_edit` apply a planted fault to the rows in memory (C5-N-P, C11-P)."""

    @classmethod
    def from_inputs(cls, inp: Inputs, segments_edit=None, exceptions_edit=None) -> "CL2Reading":
        _, entries = inp.table(CL2["entries"])
        _, segments = inp.table(CL2["segments"])
        _, exceptions = inp.table(CL2["exceptions"])
        segments, exceptions = [dict(r) for r in segments], [dict(r) for r in exceptions]
        if segments_edit:
            segments_edit(segments)
        if exceptions_edit:
            exceptions_edit(exceptions)
        return cls(entries, segments, exceptions)

    def __init__(self, entries: list[dict], segments: list[dict], exceptions: list[dict]):
        self.entries, self.segments, self.exceptions = entries, segments, exceptions
        self.entry_rows = {r["entry"]: r for r in self.entries if r["scope"] == "entry"}
        self.chain_rows = {(r["entry"], r["chain"]): r for r in self.entries if r["scope"] == "chain"}
        self.chains: dict[tuple[str, str], Chain] = {}
        notjoined = defaultdict(list)
        for x in self.exceptions:
            if x["kind"] != "UNK" and x["joined"] == "false":
                notjoined[(x["entry"], x["chain"], int(x["author_first"]), x["ins_code"])].append(x["kind"])
        for (e, c), row in self.chain_rows.items():
            self.chains[(e, c)] = Chain(e, c, row["species"])
        for s in self.segments:
            ch = self.chains[(s["entry"], s["chain"])]
            placed = s["status"] in ("agree", "path A only")
            off = int(s["offset_s"] if s["status"] == "agree" else s["offset_a"]) if placed else None
            g = gaps(s["unmodelled_gaps"])
            for n in range(int(s["author_first"]), int(s["author_last"]) + 1):
                if n in g:
                    continue
                kinds = notjoined.get((s["entry"], s["chain"], n, ""), [])
                joined = placed and s["identity_low"] == "false" and s["short_departing_run_path_a"] == "false" \
                    and not kinds
                r11c_only = placed and not joined and s["identity_low"] == "false" and kinds == [R11C]
                ch.residues.append(Res(n, int(s["segment"]), s["status"], n + off if placed else None, joined,
                                       kinds, r11c_only))
        for ch in self.chains.values():
            ch.residues.sort(key=lambda r: r.n)
        for x in self.exceptions:
            ch = self.chains[(x["entry"], x["chain"])]
            if x["kind"] == "UNK":
                m = UNK_NOTE.match(x["note"])
                if not m:
                    raise SystemExit(f"{x['entry']} {x['chain']}: an UNK row's note is not CL-2's form: {x['note']!r}")
                ch.unk.append({"first": int(x["author_first"]), "last": int(x["author_last"]),
                               "n": int(x["n_residues"]), "sifts_n": int(m.group(1)),
                               "sifts": (int(m.group(2)), int(m.group(3))) if m.group(2) else None})
            elif x["kind"] == "neither path":
                ch.neither[int(x["author_first"])] = x["path_a_partners"]
            elif x["kind"] == "declared difference":
                ch.declared[int(x["author_first"])] = x["declared"]

    def segment_row(self, entry: str, chain: str, seg: int) -> dict:
        return next(s for s in self.segments if s["entry"] == entry and s["chain"] == chain and int(s["segment"]) == seg)


def guards(cl2: CL2Reading) -> list[str]:
    """Check C11: the reading reproduces CL-2's own counts, and the orders it relies on hold. Returns the failures."""
    bad = []
    for s in cl2.segments:
        ch = cl2.chains[(s["entry"], s["chain"])]
        rs = [r for r in ch.residues if r.seg == int(s["segment"])]
        where = f"{s['entry']} {s['chain']} segment {s['segment']}"
        if len(rs) != int(s["n_residues"]):
            bad.append(f"{where}: {len(rs)} author numbers, n_residues {s['n_residues']}")
        if s["status"] in ("agree", "path A only") and rs and (
                rs[0].species != int(s["species_first"]) or rs[-1].species != int(s["species_last"])):
            bad.append(f"{where}: species {rs[0].species}-{rs[-1].species}, the row {s['species_first']}-"
                       f"{s['species_last']}")
        if sum(r.joined for r in rs) != int(s["joined_residues"] or 0):
            bad.append(f"{where}: {sum(r.joined for r in rs)} joined, joined_residues {s['joined_residues']}")
    for (e, c), ch in cl2.chains.items():
        joined = [r for r in ch.residues if r.joined]
        if len(joined) != int(cl2.chain_rows[(e, c)]["joined"]):
            bad.append(f"{e} {c}: {len(joined)} joined, the entries table {cl2.chain_rows[(e, c)]['joined']}")
        for r in ch.residues:
            if r.species is not None and not r.joined and not r.kinds:
                bad.append(f"{e} {c} author {r.n}: placed, not joined, and no exceptions row says why")
        placed = [r.species for r in ch.residues if r.species is not None]
        if len(placed) != len(set(placed)):
            bad.append(f"{e} {c}: a species position held twice")
        js = [r.species for r in joined]
        if js != sorted(js):
            bad.append(f"{e} {c}: joined positions out of author order")
        labels = [(int(s["author_first"]), int(s["label_first"])) for s in cl2.segments
                  if s["entry"] == e and s["chain"] == c and s["label_first"] not in ("", "-")]
        if [lab for _, lab in sorted(labels)] != sorted(lab for _, lab in labels):
            bad.append(f"{e} {c}: label order does not follow author order")
        for u in ch.unk:
            if u["sifts"] is None:
                continue
            below = [r.species for r in joined if r.n < u["first"]]
            above = [r.species for r in joined if r.n > u["last"]]
            if (below and u["sifts"][0] <= below[-1]) or (above and u["sifts"][1] >= above[0]):
                bad.append(f"{e} {c}: the UNK stretch at author {u['first']}-{u['last']} has its SIFTS range "
                           f"{u['sifts']} outside its flanks")
    return bad


def unk_of(ch: Chain, n: int) -> dict | None:
    hit = [u for u in ch.unk if u["first"] <= n <= u["last"]]
    return hit[0] if hit else None


def status(ch: Chain, p: int, withdrawn: frozenset = frozenset()) -> tuple[str, str, str, int | None, str]:
    """L2's rule for chain `ch` at species position p. `withdrawn` holds the author numbers of this chain's joins that
    C5-S withdrew. Returns (status, join_path, not_joined_reason, author_number, rule)."""
    at = ch.placed_at(p)
    if at is not None:
        if at.joined and at.n in withdrawn:
            return "withdrawn (C5-S)", at.status, "", at.n, "step4-withdrawn"
        if at.joined:
            return "joined", at.status, "", at.n, "step2-joined"
        if at.r11c_only:
            return "not determinable", "", R11C, at.n, "step2-r11c"
        return "not joined", "", ";".join(at.kinds), at.n, "step2-not-joined"
    import bisect
    joined, positions = ch.joined_without(frozenset(withdrawn))
    if not joined:
        return "not determinable", "", "the chain has no joined residue", None, "step3-r1"
    k = bisect.bisect_left(positions, p)  # joined positions rise with author numbers (guard C11)
    L = joined[k - 1] if k > 0 else None
    R = joined[k] if k < len(joined) else None
    lo, hi = (L.n if L else float("-inf")), (R.n if R else float("inf"))
    M = ch.between(lo, hi)
    if L and R:
        dl, dr = L.species - L.n, R.species - R.n
        allowed = set(range(min(dl, dr), max(dl, dr) + 1))
    else:
        f = L or R
        allowed = {f.species - f.n}

    def unplaced(r: Res) -> bool:
        return r.species is None or r.n in withdrawn or r.r11c_only

    if not M:
        return "not modelled", "", "", None, "step3-r2"
    elsewhere = [r for r in M if not unplaced(r)]
    hit = [r for r in elsewhere if p - r.n in allowed]
    if hit:
        r = hit[0]
        return "not determinable", "", f"CL-2 places the residue at author {r.n} at species position {r.species}", \
            None, "step3-r3"
    loose = [r for r in M if unplaced(r)]
    if not loose:
        return "not modelled", "", "", None, "step3-r4"
    for r in loose:
        partners = ch.neither.get(r.n, "")
        if partners and str(p) in partners.split(","):
            return "not determinable", "", (f"the residue at author {r.n} is ambiguous on path A (partners "
                                             f"{partners.replace(',', ' ')})"), None, "step3-r5"
    if L and R and not elsewhere and len(M) == R.species - L.species - 1:
        r = M[p - L.species - 1]
        return "modelled, not placed", "", f"{r.status}, placed by its order between the flanks", r.n, "step3-r6"
    agreeing = []
    for u in ch.unk:
        contiguous = u["last"] - u["first"] + 1 == u["n"] == u["sifts_n"]
        if contiguous and u["sifts"] == (u["first"], u["last"]) and any(r.n == u["first"] for r in M):
            agreeing.append(u)
    for u in agreeing:
        if u["first"] <= p <= u["last"]:
            r = next(x for x in M if x.n == p)
            return "modelled, not placed", "", f"{r.status}, author number and SIFTS agree", r.n, "step3-r7"
    in_agreeing = {r.n for u in agreeing for r in M if u["first"] <= r.n <= u["last"]}
    if all(r.n in in_agreeing for r in loose):
        return "not modelled", "", "", None, "step3-r8"
    readings, seen = [], set()
    for r in loose:
        if r.n in withdrawn:
            readings.append(f"withdrawn join, author {r.n}")
        elif r.r11c_only:
            readings.append(f"R11c, author {r.n}")
        elif r.status == "UNK" or unk_of(ch, r.n):
            u = unk_of(ch, r.n)
            if u is None:
                raise SystemExit(f"{ch.entry} {ch.chain} author {r.n}: an UNK residue with no UNK row")
            if id(u) in seen:
                continue
            seen.add(id(u))
            sifts = f"SIFTS {u['sifts'][0]}-{u['sifts'][1]}" if u["sifts"] else "SIFTS none"
            readings.append(f"UNK, author {u['first']}-{u['last']}, {sifts}")
        else:
            partners = ch.neither.get(r.n, "")
            listed = f"partners {partners.replace(',', ' ')}" if partners else "partners not listed"
            readings.append(f"{r.status}, author {r.n}, {listed}")
    return "not determinable", "", " | ".join(readings), None, "step3-r9"


def residue_types(text: str) -> dict[tuple[str, int, str], str]:
    """(auth_asym_id, auth_seq_id, insertion code) -> label_comp_id, from the first model's atom records."""
    import gemmi
    block = gemmi.cif.read_string(text).sole_block()
    t = block.find("_atom_site.", ["auth_asym_id", "auth_seq_id", "pdbx_PDB_ins_code", "label_comp_id",
                                   "pdbx_PDB_model_num"])
    out: dict = {}
    first_model = None
    for row in t:
        model = row[4]
        first_model = first_model or model
        if model != first_model:
            continue
        ins = row[2] if row[2] not in ("?", ".") else ""
        out.setdefault((row[0], int(row[1]), ins), row[3])
    return out
