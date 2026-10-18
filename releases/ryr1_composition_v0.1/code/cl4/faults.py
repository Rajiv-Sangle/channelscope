"""faults.py - CL-4's planted faults (the criteria's table, *Checks and planted faults*), each applied in memory after
check C1's guard and run against the check it targets, which must report it; another check reporting it does not count
in its place. Each returns (caught, what happened); None for a fault not run where its row allows."""
from __future__ import annotations

import copy

import c5s
from common import CL2, NUMBERING, Inputs, Refused
from compose import (Fail, World, add_counts, assemble, check_c2, check_c3, check_c4, check_c5c, check_c5g, check_c5n,
                     check_c7, check_c8, check_c9, check_c10, check_c11, check_c11u, check_p0, need)
from l2 import CL2Reading
from layers import c2_counts, clinvar

T1, T2 = "cs:table." + "T" * 32, "cs:table." + "U" * 32


def caught(fn) -> tuple[bool, str]:
    try:
        fn()
    except (Fail, Refused) as e:
        return True, str(e)[:300]
    return False, "passed"


def flip_byte(data: bytes, at: int = 4096) -> bytes:
    return data[:at] + bytes([data[at] ^ 0x01]) + data[at + 1:]


def v3_first_rule(ch, p, withdrawn=frozenset()):
    """Version 3's first rule (cl4v3_lib.py), replaced after the re-check's finding B1': C11-U-P's substitute."""
    at = ch.placed_at(p)
    if at is not None:
        if at.joined:
            return "joined", at.status, "", at.n, "v3"
        return "not joined", "", ";".join(at.kinds), at.n, "v3"
    joined = [r for r in ch.residues if r.joined]
    below = [i for i, x in enumerate(joined) if x.species < p]
    L = joined[below[-1]] if below else None
    R = joined[below[-1] + 1] if below and below[-1] + 1 < len(joined) else (joined[0] if not below and joined else None)
    if not (L or R):
        return "not determinable", "", "no joined residue in the chain", None, "v3"
    lo, hi = (L.n if L else -10 ** 9), (R.n if R else 10 ** 9)
    M = [x for x in ch.residues if lo < x.n < hi]
    dl = L.species - L.n if L else R.species - R.n
    dr = R.species - R.n if R else dl
    cand = [x for x in M if (p - x.n) in set(range(min(dl, dr), max(dl, dr) + 1))]
    if not cand:
        return "not modelled", "", "", None, "v3"
    if L and R and dl == dr and len(cand) == 1:
        x = cand[0]
        if x.species is None:
            return "modelled, not placed", "", x.status, x.n, "v3"
        return "not determinable", "", f"CL-2 places the residue at author {x.n} at species position {x.species}", \
            x.n, "v3"
    return "not determinable", "", "the flanking joined residues' offsets differ", None, "v3"


def c5s_planted(w: World, cl2: CL2Reading, setup) -> tuple[bool, str]:
    """C5-S-P: every label of 6X32 chain B moved +1, and the join at P16960 950 tested (940 if 950 is not joined)."""
    departing, ref, cas = setup
    key = ("6X32", "B")
    p = 950 if any(r.species == 950 and r.joined for r in cl2.chains[key].residues) else 940
    pair = c5s.Pair(c5s.labelled(cl2.chains[key], cas[key], departing[key], 1), ref)
    t = c5s.test_join(pair, p)
    ok = t["verdict"] == "counts against" and t["offset"] == -1
    return ok, f"P16960 {p} in 6X32 chain B, labels moved +1: {t['verdict']}, offset {t['offset']}"


def run_faults(w: World, b: dict, res: dict) -> dict:
    out = {}

    def p0p():
        data = w.inp.data[CL2["segments"]]
        lines = data.decode("utf-8").split("\n")
        cells = lines[1].split("\t")
        cells[7] = str(int(cells[7]) + 1)  # one cell of one data row: the first segment's author_first
        lines[1] = "\t".join(cells)
        changed = "\n".join(lines).encode("utf-8")
        assert changed != data, "P0-P changed nothing"
        check_p0(w, changed)
    out["P0-P"] = caught(p0p)

    def c1p():
        Inputs(corrupt={"cache/rcsb/2026-10-06/9PWO.cif.gz": flip_byte}).mmcif("9PWO")
    out["C1-P"] = caught(c1p)

    def c2p():
        def edit(summ):
            summ["12964"]["molecular_consequence_list"] = ["nonsense"]
        cv = clinvar(w.inp, edit)
        got = c2_counts(cv)
        if (got["included"], got["excluded"]) != (357, 22):
            return  # not the report the criteria require, so not caught
        check_c2(cv)
    out["C2-P"] = caught(c2p)

    def c3p():
        def edit(summ):
            before = summ["12964"]["title"]
            summ["12964"]["title"] = before.replace("p.Arg614Cys", "p.Gly614Cys")
            assert summ["12964"]["title"] != before, "C3-P changed nothing"
        check_c3(clinvar(w.inp, edit))
    out["C3-P"] = caught(c3p)

    def c4p(part):
        def go():
            t = copy.deepcopy(res["tables"])
            if part == 1:
                row = next(r for r in t["cl4_clinvar"] if r["human_position"] == 163)
                row["clinvar_retrieval"] = "cs:retrieval." + "A" * 32
            else:
                row = dict(next(r for r in t["cl4_gnomad"] if r["human_position"] == 163))
                row["gnomad_table"] = None
                t["cl4_gnomad"].append(row)
            check_c4(t, res["pending"], res["graph_ids"])
        return go
    i, ii = caught(c4p(1)), caught(c4p(2))
    out["C4-P"] = (i[0] and ii[0], f"(i) {i[1][:140]} | (ii) {ii[1][:140]}")

    same = [x for x in res["c5c"]["compared"] if x["outcome"] == "same version: equal"]
    if same:
        uid = min(x["uid"] for x in same)

        def c5cp():
            clin = copy.deepcopy(b["clinvar"])
            next(r for r in clin if r["uid"] == uid)["description"] += "x"
            check_c5c(w, clin, b["conditions"])
        out["C5-C-P"] = caught(c5cp)
    else:
        out["C5-C-P"] = (None, "not run: no sampled record came back at the same version")

    present = sorted((r for r in b["gnomad"] if r["human_position"] in w.sample["all"] and r["exome_present"]),
                     key=lambda r: r["variant_id"])
    if present:
        vid = present[0]["variant_id"]

        def c5gp():
            gn = copy.deepcopy(b["gnomad"])
            next(r for r in gn if r["variant_id"] == vid)["exome_ac"] += 1
            check_c5g(w, gn)
        out["C5-G-P"] = caught(c5gp)
    else:
        out["C5-G-P"] = (None, "not run: no sampled variant has exome data")

    out["C5-S-P"] = res["c5s_p"]

    def c5swp():
        key = ("6X32", "B")
        seg = next(r.seg for r in b["cl2"].chains[key].residues if r.species == 950)
        tests = copy.deepcopy(b["tests"])
        hit = [t for t in tests if (t["entry"], t["chain"], t["segment"]) == (*key, seg)]
        for t in hit:
            t["verdict"], t["offset"] = "counts against", -1
        b3 = assemble(w, tests=tests)
        add_counts(w, b3, T1, T2)
        rows = [r for r in b3["structures"] if (r["entry"], r["chain"], r["cl2_segment"]) == (*key, seg)
                and r["join_path"]]
        need(len(hit) >= 2, f"segment {seg} holds {len(hit)} sampled joins, fewer than the segment rule needs")
        need(rows and all(r["status"] == "withdrawn (C5-S)" for r in rows),
             f"{sum(r['status'] != 'withdrawn (C5-S)' for r in rows)} rows of segment {seg} stay joined")
        need(b3["counts"] != b["counts"], "the counts did not move")
        check_c10(w, b3, tests=tests)
        return f"{len(hit)} sampled joins of segment {seg} given counts against: all {len(rows)} joined rows of the " \
               f"segment withdrawn, the counts moved, C10's recount equal"
    try:
        out["C5-S-W-P"] = (True, c5swp())
    except Fail as e:
        out["C5-S-W-P"] = (False, str(e)[:300])

    def c5np():
        rows0 = [r for r in b["structures"] if r["status"] == "joined" and r["join_path"] == "agree"
                 and r["human_position"] in w.sample["all"]]
        first = min(rows0, key=lambda r: (r["entry"], r["chain"], r["human_position"]))
        segs = [dict(s) for s in b["cl2"].segments]
        n = 0
        for s in segs:
            if (s["entry"], s["chain"], int(s["segment"])) == (first["entry"], first["chain"], first["cl2_segment"]):
                for k in ("offset_s", "offset_a", "species_first", "species_last"):
                    s[k] = str(int(s[k]) + 1)
                n += 1
        assert n == 1, "C5-N-P changed no segment"
        b3 = assemble(w, cl2=CL2Reading(b["cl2"].entries, segs, b["cl2"].exceptions), tests=b["tests"])
        check_c5n(w, b3["structures"])
    out["C5-N-P"] = caught(c5np)

    hits = []
    for e, c in (("7M6A", "A"), ("9NMO", "A"), ("9PWO", "A")):
        def c6p(e=e, c=c):
            rows = copy.deepcopy(b["structures"])
            r = next(x for x in rows if (x["human_position"], x["entry"], x["chain"]) == (163, e, c))
            nxt = b["cl2"].chains[(e, c)].placed_at(r["partner_position"] + 1)
            r["author_number"], r["structure_residue"] = nxt.n, w.types[e][(c, nxt.n, "")]
            assert r["structure_residue"] == "VAL", "C6-P's planted residue is not the valine the criteria name"
            check_c7(w, rows)
        hits.append(caught(c6p))
    out["C6-P"] = (all(h[0] for h in hits), " | ".join(h[1][:110] for h in hits))

    def c8p():
        rows = copy.deepcopy(b["structures"])
        r = dict(next(x for x in rows if (x["human_position"], x["entry"], x["chain"]) == (163, "7M6A", "A")))
        pig = w.partner[(163, "Sus scrofa")]
        r.update(species="Sus scrofa", partner_numbering=NUMBERING["Sus scrofa"],
                 partner_position=pig["partner_position"], partner_residue=pig["partner_residue"], status="joined")
        rows.append(r)
        check_c8(w, rows)
    out["C8-P"] = caught(c8p)

    def c9p():
        gn = copy.deepcopy(b["gnomad"])
        if w.scope == "full_set":
            r = next(x for x in gn if x["variant_id"] == "19-38440803-G-T")
            assert r["exome_filters"] == "AC0", "C9-P's row is not S2's AC0"
            r["exome_filters"] = None
        else:
            r = next(x for x in gn if x["variant_id"] == "19-38457545-C-T")
            r["exome_filters"] = "AC0"
        check_c9(w, gn)
    out["C9-P"] = caught(c9p)

    def c10p(part):
        def go():
            b3 = dict(b)
            if part == 1:
                b3["vus"] = copy.deepcopy(b["vus"])
                b3["vus"][0]["n_total"] += 1
            else:
                b3["structures"] = copy.deepcopy(b["structures"])
                r = next(x for x in b3["structures"]
                         if (x["human_position"], x["entry"], x["chain"]) == (614, "6X34", "B"))
                assert r["status"] == "not joined", "C10-P's row is not the not-joined row the criteria name"
                r.update(status="joined", join_path="path A only", not_joined_reason=None)
                add_counts(w, b3, T1, T2)
            check_c10(w, b3)
        return go
    i, ii = caught(c10p(1)), caught(c10p(2))
    out["C10-P"] = (i[0] and ii[0], f"(i) {i[1][:140]} | (ii) {ii[1][:140]}")

    def c10gp():
        gate = [dict(r) for r in w.gate_rows]
        g = next(r for r in gate if r["entry"] == "7M6L")
        g["gate_case"], g["gate_case_reason"] = "c", "planted fault C10-G-P"
        b3 = assemble(w, gate_rows=gate, tests=b["tests"])
        add_counts(w, b3, T1, T2)
        joined = {r["human_position"] for r in b3["structures"] if r["entry"] == "7M6L" and r["status"] == "joined"}
        old = {(r["human_position"], r["species"]): r for r in b["counts"]}
        moved = joined and all(
            r["entries_joined_gate_case_c_or_d"] == old[(r["human_position"], r["species"])][
                "entries_joined_gate_case_c_or_d"] + 1
            and r["entries_joined_open_agree"] == old[(r["human_position"], r["species"])]["entries_joined_open_agree"] - 1
            for r in b3["counts"] if r["species"] == "Oryctolagus cuniculus" and r["human_position"] in joined)
        need(bool(moved), "7M6L did not leave the open column for case c or d at every residue it joins")
        try:
            check_c10(w, b3, gate_rows=gate)
        except Fail as e:
            need("7M6L" in str(e), f"C10 failed, but not on 7M6L's mark: {str(e)[:150]}")
            return f"7M6L moved at {len(joined)} residues; C10: {str(e)[:150]}"
        raise Fail("C10 did not report 7M6L's mark")
    try:
        out["C10-G-P"] = (True, c10gp())
    except Fail as e:
        out["C10-G-P"] = (False, str(e)[:300])

    def c10wp():
        tests = copy.deepcopy(b["tests"])
        hit = [t for t in tests if t["entry"] == "6X33" and t["human_position"] == 614]
        need(len(hit) == 4, f"6X33 has {len(hit)} sampled joins at 614, not four")
        for t in hit:
            t["verdict"], t["offset"] = "counts against", -1
        b3 = assemble(w, tests=tests)
        add_counts(w, b3, T1, T2)
        row = next(r for r in b3["counts"] if (r["human_position"], r["species"]) == (614, "Sus scrofa"))
        old = next(r for r in b["counts"] if (r["human_position"], r["species"]) == (614, "Sus scrofa"))
        need(row["entries_withdrawn_c5s"] == old["entries_withdrawn_c5s"] + 1, "6X33 did not move to withdrawn")
        check_c10(w, b3, tests=tests)
        return "6X33 moved to entries_withdrawn_c5s at 614, and C10's recount equals the build's"
    try:
        out["C10-W-P"] = (True, c10wp())
    except Fail as e:
        out["C10-W-P"] = (False, str(e)[:300])

    out["C11-U-P"] = caught(lambda: check_c11u(b["cl2"], v3_first_rule))

    def c11p():
        exc = [dict(x) for x in b["cl2"].exceptions]
        x = next(x for x in exc if (x["entry"], x["chain"], x["author_first"], x["kind"]) ==
                 ("6X34", "B", "615", "undeclared difference"))
        x["joined"] = "true"
        check_c11(CL2Reading(b["cl2"].entries, [dict(s) for s in b["cl2"].segments], exc))
    out["C11-P"] = caught(c11p)
    return out
