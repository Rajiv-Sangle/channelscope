"""recount.py - check C10's second script (the criteria, C10). It does not import the build's code: the build hands it,
in memory, the inputs it used (any planted change included) and its rows, and this module derives every structure
row's status and reason by its own reading of CL-2's tables, applies C5-S's segment rule itself from the verdicts,
derives each entry's gate case from CL-2's entries and segments tables by CL-2's rule (criteria 2.2, "The gate residue,
and what CL-3 does with it", as CL-3's gate-case script states how each condition is read), and recounts both count
tables and their sums. It returns every difference it finds; none means the check passes."""
from __future__ import annotations

import bisect
import re
from collections import defaultdict

R11C = "short departing run, path A only (R11c): not joined"
ORDER = ["joined agree", "joined path A only", "withdrawn (C5-S)", "not joined", "modelled, not placed",
         "not determinable", "not modelled", "entry not analysed"]


def _ranges(cell):
    s = set()
    for part in ([] if cell in ("", "-") else cell.split(",")):
        lo, _, hi = part.partition("-")
        s |= set(range(int(lo), int(hi or lo) + 1))
    return s


class Chains:
    """CL-2's tables, read again: per chain, parallel lists in author order."""

    def __init__(self, entries, segments, exceptions):
        self.rows = {(r["entry"], r["chain"]): r for r in entries if r["scope"] == "chain"}
        self.entry_species = {r["entry"]: r["species"] for r in entries if r["scope"] == "entry"}
        bad = defaultdict(list)
        self.unk, self.partners = defaultdict(list), {}
        for x in exceptions:
            k = (x["entry"], x["chain"])
            if x["kind"] == "UNK":
                m = re.fullmatch(r"SIFTS gives a position for (\d+) \((\d+)-(\d+)\); not used", x["note"])
                self.unk[k].append((int(x["author_first"]), int(x["author_last"]), int(x["n_residues"]),
                                    (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None))
            else:
                if x["joined"] == "false":
                    bad[(k, int(x["author_first"]), x["ins_code"])].append(x["kind"])
                if x["kind"] == "neither path":
                    self.partners[(k, int(x["author_first"]))] = x["path_a_partners"]
        self.res = defaultdict(list)  # (n, segment status, species or None, joined, kinds, r11c only, segment)
        for s in segments:
            k = (s["entry"], s["chain"])
            st = s["status"]
            off = int(s["offset_s"]) if st == "agree" else int(s["offset_a"]) if st == "path A only" else None
            holes = _ranges(s["unmodelled_gaps"])
            for n in range(int(s["author_first"]), int(s["author_last"]) + 1):
                if n in holes:
                    continue
                kinds = bad.get((k, n, ""), [])
                ok = off is not None and s["identity_low"] != "true" and s["short_departing_run_path_a"] != "true"
                j = ok and not kinds
                self.res[k].append((n, st, None if off is None else n + off, j, kinds,
                                    off is not None and not j and s["identity_low"] != "true" and kinds == [R11C],
                                    int(s["segment"])))
        self.at, self.authors, self._js = {}, {}, {}
        for k in self.res:
            self.res[k].sort()
            self.at[k] = {r[2]: r for r in reversed(self.res[k]) if r[2] is not None}
            self.authors[k] = [r[0] for r in self.res[k]]

    def joined(self, key, gone):
        g = (key, frozenset(gone))
        if g not in self._js:
            js = [(r[0], r[2]) for r in self.res[key] if r[3] and r[0] not in gone]
            self._js[g] = (js, [x[1] for x in js])
        return self._js[g]


def derive(ch: Chains, key, p: int, gone: set[int]):
    """(status, reason) by L2's rule, read independently."""
    rs = ch.res[key]
    hit = ch.at[key].get(p)
    if hit is not None:
        n, st, sp, j, kinds, r11, _ = hit
        if j and n in gone:
            return "withdrawn (C5-S)", ""
        if j:
            return "joined", ""
        if r11:
            return "not determinable", R11C
        return "not joined", ";".join(kinds)
    js, pos = ch.joined(key, gone)
    if not js:
        return "not determinable", "the chain has no joined residue"
    i = bisect.bisect_left(pos, p) - 1  # the joined residues' positions rise with their authors
    left = js[i] if i >= 0 else None
    right = js[i + 1] if i + 1 < len(js) else None
    a = left[0] if left else -10 ** 9
    b = right[0] if right else 10 ** 9
    lo = bisect.bisect_right(ch.authors[key], a)
    mid = rs[lo:bisect.bisect_left(ch.authors[key], b)]
    offs = [x[1] - x[0] for x in (left, right) if x]
    allowed = range(min(offs), max(offs) + 1)
    if not mid:
        return "not modelled", ""
    loose = [r for r in mid if r[2] is None or r[0] in gone or r[5]]
    placed = [r for r in mid if r not in loose]
    for r in placed:
        if (p - r[0]) in allowed:
            return "not determinable", f"CL-2 places the residue at author {r[0]} at species position {r[2]}"
    if not loose:
        return "not modelled", ""
    for r in loose:
        lst = ch.partners.get((key, r[0]), "")
        if lst and p in [int(v) for v in lst.split(",")]:
            return "not determinable", f"the residue at author {r[0]} is ambiguous on path A (partners {' '.join(lst.split(','))})"
    if left and right and not placed and len(mid) == right[1] - left[1] - 1:
        return "modelled, not placed", f"{mid[p - left[1] - 1][1]}, placed by its order between the flanks"
    good = [u for u in ch.unk[key] if u[3] and u[1] - u[0] + 1 == u[2] == u[3][0] and (u[3][1], u[3][2]) == (u[0], u[1])
            and any(r[0] == u[0] for r in mid)]
    for u in good:
        if u[0] <= p <= u[1]:
            st = next(r[1] for r in mid if r[0] == p)
            return "modelled, not placed", f"{st}, author number and SIFTS agree"
    if all(any(u[0] <= r[0] <= u[1] for u in good) for r in loose):
        return "not modelled", ""
    parts, done = [], set()
    for r in loose:
        if r[0] in gone:
            parts.append(f"withdrawn join, author {r[0]}")
        elif r[5]:
            parts.append(f"R11c, author {r[0]}")
        elif r[1] == "UNK":
            u = next(u for u in ch.unk[key] if u[0] <= r[0] <= u[1])
            if u in done:
                continue
            done.add(u)
            parts.append(f"UNK, author {u[0]}-{u[1]}, " + (f"SIFTS {u[3][1]}-{u[3][2]}" if u[3] else "SIFTS none"))
        else:
            lst = ch.partners.get((key, r[0]), "")
            parts.append(f"{r[1]}, author {r[0]}, " + (f"partners {' '.join(lst.split(','))}" if lst
                                                       else "partners not listed"))
    return "not determinable", " | ".join(parts)


def withdrawn_by_verdicts(tests: list[dict]) -> dict:
    """Each tested join that counts against, and every join of a segment the segment rule withdraws."""
    gone = defaultdict(set)
    by_seg = defaultdict(list)
    for t in tests:
        by_seg[(t["entry"], t["chain"], t["segment"])].append(t)
        if t["verdict"] == "counts against":
            gone[(t["entry"], t["chain"])].add(t["author_number"])
    return gone, [k for k, v in by_seg.items()
                  if sum(t["verdict"] == "counts against" for t in v) >= 2
                  and 2 * sum(t["verdict"] == "counts against" for t in v) >= len(v)]


def gate_case(ch: Chains, segments, entry, gate_n: int, usable: bool) -> str:
    keys = [k for k in ch.rows if k[0] == entry]
    if not usable or not keys:
        return "d"
    worst = "a"
    for k in keys:
        row = ch.rows[k]
        run = [s for s in segments if (s["entry"], s["chain"]) == k
               and int(s["author_first"]) <= gate_n <= int(s["author_last"]) and gate_n not in _ranges(s["unmodelled_gaps"])]
        case = "c"
        if len(run) == 1 and row["gate_residue"].endswith(str(gate_n)):
            s = run[0]
            outcome = row["gate_outcome"]
            off = int(s["offset_s"] or 0) if s["status"] == "agree" else int(s["offset_a"] or 0)
            joined = (s["status"] == outcome and s["identity_low"] == "false"
                      and s["short_departing_run_path_a"] == "false" and row["gate_note"] == "-")
            at0 = row["gate_species_position"] == str(gate_n) and off == 0
            holes = _ranges(s["unmodelled_gaps"])
            span = int(s["author_last"]) - int(s["author_first"]) + 1 - len(holes)
            left = len([n for n in range(int(s["author_first"]), gate_n) if n not in holes])
            right = len([n for n in range(gate_n + 1, int(s["author_last"]) + 1) if n not in holes])
            nosifts = row["path_s"].startswith(("none", "another accession"))
            if outcome == "agree" and joined and at0 and row["gate_structure_residue"] == "ILE":
                case = "a"
            elif (nosifts and outcome == "path A only" and joined and at0 and span == int(s["n_residues"])
                  and left >= 10 and right >= 10):
                case = "b"
        worst = max(worst, case)
    return worst


def run(build_rows: dict, cl2: tuple, gate_rows, s13_rows, mapping_rows: dict, clinvar_rows, residues: list[int],
        tests: list[dict], usable: bool) -> dict:
    """build_rows: the build's cl4_structures, cl4_structure_counts and cl4_vus_counts rows. Returns the differences."""
    entries, segments, exceptions = cl2
    ch = Chains(entries, segments, exceptions)
    gone, segs_out = withdrawn_by_verdicts(tests)
    against = {k: set(v) for k, v in gone.items()}
    for e, c, sg in segs_out:
        gone[(e, c)] |= {r[0] for r in ch.res[(e, c)] if r[6] == sg and r[3]}
    partner = {}
    for sp, rows in mapping_rows.items():
        for r in rows:
            if r["subject_position"] and r["correspondence"] == "pair":
                partner[(int(r["subject_position"]), sp)] = int(r["object_position"])
    diffs = []
    status = {}
    built = {(int(r["human_position"]), r["entry"], r["chain"]): r for r in build_rows["cl4_structures"]}
    for h in residues:
        for key in sorted(ch.rows):
            sp = ch.entry_species[key[0]]
            if (h, sp) not in partner:
                continue
            st, why = derive(ch, key, partner[(h, sp)], gone.get(key, set()))
            path = ""
            if st in ("joined", "withdrawn (C5-S)"):
                hit = next(r for r in ch.res[key] if r[2] == partner[(h, sp)])
                path = hit[1]
                if st == "withdrawn (C5-S)":
                    why = ("coordinates disagree with 9PWO (C5-S)" if hit[0] in against.get(key, set())
                           else "withdrawn with its segment (C5-S's segment rule)")
            status[(h, key)] = (st, path)
            b = built.get((h, key[0], key[1]))
            if b is None:
                diffs.append(f"no build row for human {h} {key}")
            elif (b["status"], b["not_joined_reason"] or "", b["join_path"] or "") != (st, why, path):
                diffs.append(f"human {h} {key}: build {b['status']!r} {b['not_joined_reason']!r} "
                             f"{b['join_path']!r}, recount {st!r} {why!r} {path!r}")
    if len(built) != len(status):
        diffs.append(f"{len(built)} build rows, {len(status)} recounted")
    gate = {r["entry"]: r["gate_case"] for r in gate_rows}
    s13 = {r["entry"]: r for r in s13_rows}
    for e in sorted(ch.entry_species):
        d = gate_case(ch, segments, e, int(re.sub(r"\D", "", s13[e]["gate_residue"])), usable)
        if d != gate.get(e):
            diffs.append(f"{e}: CL-3's mark {gate.get(e)!r}, CL-2's rule {d!r}")
    measures = ["A"] + (["B"] if any(r["class_a"] != r["class_b_fixed"] for r in s13_rows) else [])
    cls = {m: {r["entry"]: r["class_a" if m == "A" else "class_b_fixed"] for r in s13_rows} for m in measures}
    # the counts
    first = {}
    for (h, key), (st, path) in status.items():
        label = f"joined {path}" if st == "joined" else st
        k = (h, key[0])
        first[k] = min(first.get(k, label), label, key=ORDER.index)
    counts = {}
    for h in residues:
        for sp in ["Oryctolagus cuniculus", "Mus musculus", "Sus scrofa"]:
            ents = [e for e in ch.entry_species if ch.entry_species[e] == sp]
            for m in measures:
                n = defaultdict(int)
                for e in ents:
                    lab = first.get((h, e), "entry not analysed")
                    if lab.startswith("joined"):
                        if gate[e] in ("c", "d"):
                            n["entries_joined_gate_case_c_or_d"] += 1
                        elif cls[m][e] == "indeterminate":
                            n["entries_joined_indeterminate"] += 1
                        else:
                            way = "agree" if lab == "joined agree" else "path_a_only"
                            n[f"entries_joined_{cls[m][e]}_{way}"] += 1
                    else:
                        n[{"withdrawn (C5-S)": "entries_withdrawn_c5s", "not joined": "entries_not_joined",
                           "modelled, not placed": "entries_modelled_not_placed",
                           "not determinable": "entries_not_determinable", "not modelled": "entries_not_modelled",
                           "entry not analysed": "entries_not_analysed"}[lab]] += 1
                counts[(h, sp, m)] = (len(ents), dict(n))
    got = {(int(r["human_position"]), r["species"], r["class_measure"]): r for r in build_rows["cl4_structure_counts"]}
    if set(got) != set(counts):
        diffs.append("the count table's keys differ")
    for k, (total, n) in counts.items():
        r = got.get(k)
        if r is None:
            continue
        cols = [c for c in r if c.startswith("entries_")]
        if int(r["entries"]) != total or sum(int(r[c]) for c in cols) != int(r["entries"]):
            diffs.append(f"{k}: entries {r['entries']}, recount {total}; the twelve columns sum to "
                         f"{sum(int(r[c]) for c in cols)}")
        for c in cols:
            if int(r[c]) != n.get(c, 0):
                diffs.append(f"{k} {c}: build {r[c]}, recount {n.get(c, 0)}")
    # the VUS counts
    vus = defaultdict(list)
    for r in clinvar_rows:
        if r["subset"] != "not VUS":
            vus[r["subset"]].append(int(r["human_position"]))
    at_residue = defaultdict(list)
    for (hh, key), (st, path) in status.items():
        at_residue[hh].append((key, st, path))
    want = {}
    for subset, hs in vus.items():
        for unit in ("records", "residues"):
            items = hs if unit == "records" else sorted(set(hs))
            for scope in ("agree", "agree or path A only"):
                for sp in ["Oryctolagus cuniculus", "Mus musculus", "Sus scrofa", "any"]:
                    for m in measures:
                        tally = defaultdict(int)
                        for h in items:
                            joined = [key[0] for key, st, path in at_residue[h] if st == "joined"
                                      and (scope != "agree" or path == "agree")
                                      and (sp == "any" or ch.entry_species[key[0]] == sp)]
                            good = [e for e in joined if gate[e] in ("a", "b")]
                            closed = any(cls[m][e] == "closed" for e in good)
                            opened = any(cls[m][e] == "open" for e in good)
                            tally["n_total"] += 1
                            tally["n_closed"] += closed
                            tally["n_open"] += opened
                            tally["n_both"] += closed and opened
                            tally["n_joined_other_only"] += bool(joined) and not closed and not opened
                            tally["n_not_joined"] += not joined
                        want[(subset, unit, scope, sp, m)] = dict(tally)
    got = {(r["subset"], r["unit"], r["join_scope"], r["species"], r["class_measure"]): r
           for r in build_rows["cl4_vus_counts"]}
    if set(got) != set(want):
        diffs.append(f"the VUS count table's keys differ: {sorted(set(got) ^ set(want))[:3]}")
    for k, t in want.items():
        r = got.get(k)
        if r is None:
            continue
        for c, v in t.items():
            if int(r[c]) != v:
                diffs.append(f"VUS {k} {c}: build {r[c]}, recount {v}")
        if int(r["n_total"]) != int(r["n_closed"]) + int(r["n_open"]) - int(r["n_both"]) + \
                int(r["n_joined_other_only"]) + int(r["n_not_joined"]):
            diffs.append(f"VUS {k}: the sum does not hold")
    return {"differences": diffs, "rows": len(status), "withdrawn_segments": segs_out}


def synthetic(case_tables, p: int, withdrawn: list[int]):
    entries, segments, exceptions = case_tables
    ch = Chains(entries, segments, exceptions)
    key = next(iter(ch.rows))
    return derive(ch, key, p, set(withdrawn))
