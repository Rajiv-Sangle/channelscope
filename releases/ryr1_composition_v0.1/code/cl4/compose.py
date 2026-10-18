#!/usr/bin/env python3
"""compose.py - CL-4: the composition over a residue set fixed in advance, built and checked by its criteria,
`what/context/context_channelscope_cl4_composition_criteria_v3.md` (version 3, reviewed, with the operator's answers to
Q1 to Q3 committed in 2004787: Q1 (c), the VUS-high record apart; Q2 (c), the full set with the four worked residues
in C5's sample; Q3 (c)).

For each set residue it lays out, side by side and each value traced to its record: the partners in rabbit, mouse and
pig (L1); the structures that model them, chain by chain, by L2's rule on CL-2's tables, with CL-3's classes and gate
cases; gnomAD's missense variants there (L3); ClinVar's expert-panel classification and conditions (L4). It gives no
verdict of its own and infers nothing from its counts.

Every check and planted fault of the criteria's table runs before anything is written; a planted fault counts as
caught only if its own check reports it. With --write, and only if every check that stops the build passes and every
planted fault is caught, it writes the nine tables under tables/cl4/<commit>/<scope>/, its method and run records, a
table record for each table and a check-result record for each check and planted fault, and then requires the
validator to report no finding. The code and the criteria must be committed as they are.

    uv run --project how/runtime/channelscope --with gemmi==0.7.5 python -I \
        how/runtime/channelscope/cl4/compose.py [--scope full_set|four_residues] [--write]
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))
import c5cg  # noqa: E402
import c5n  # noqa: E402
import c5s  # noqa: E402
import recount  # noqa: E402
import synthetic  # noqa: E402
from columns import KEYS, RECORD_COLUMNS, TABLES  # noqa: E402
from common import (CL2, CRITERIA, GATE_TABLE, GRAPH, MAPPING, MISSION, NUMBERING, ONE_TO_THREE, S2_TABLE, S13_TABLE,  # noqa: E402
                    SPECIES, VAULT, Inputs, Refused, git_bytes, read_tsv, sha)
from l2 import R11C, CL2Reading, guards, residue_types, status as l2_status  # noqa: E402
from layers import c2_counts, clinvar, clinvar_rows, gnomad, observed_pass, partners, set_rows  # noqa: E402
from sample import c5_sample  # noqa: E402

from channelscope.graph import Graph, normalise, tsv_bytes  # noqa: E402
from channelscope.provenance import AGENT_LUMEN, AGENT_SOFTWARE, code_digest, environment, now, software  # noqa: E402
from channelscope.validate import validate  # noqa: E402

CL2_CURATION = ("c4e8b66", "what/evidence_graph/curation/cl2_run_e888359")
EXPECT_C2 = {"read": 379, "included": 358, "residues": 299, "multi": 47, "excluded": 21, "excluded_by_rule": {1: 21},
             "vus_records": 222, "vus_residues": 200, "vus_high": ["VCV000133070.12"],
             "categories": {'molecular_consequence_list is ["splice donor variant"]': 5,
                            'molecular_consequence_list is ["synonymous variant"]': 4,
                            'molecular_consequence_list is ["intron variant"]': 3,
                            'molecular_consequence_list is ["nonsense"]': 2,
                            'molecular_consequence_list is ["inframe_deletion"]': 2,
                            'molecular_consequence_list is ["frameshift variant"]': 2,
                            'molecular_consequence_list is ["inframe_insertion"]': 1,
                            'molecular_consequence_list is ["5 prime UTR variant"]': 1,
                            "molecular_consequence_list is []": 1}}
STRUCT_ORDER = ["joined agree", "joined path A only", "withdrawn (C5-S)", "not joined", "modelled, not placed",
                "not determinable", "not modelled", "entry not analysed"]
ABSENT = {"conservation": "no source chosen",
          "emhg_list": "its terms do not clearly allow this use, and no permission was sought in the close",
          "alphamissense": "its terms do not clearly allow this use, and no permission was sought in the close",
          "des_georges_domains": "its terms do not clearly allow this use, and no permission was sought in the close"}


class Fail(Exception):
    pass


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise Fail(msg)


# --- the build -----------------------------------------------------------------------------------------------------

class World:
    """The inputs and every stage of the build. A planted fault copies a World and changes one stage's input."""

    def __init__(self, scope: str):
        self.scope = scope
        self.inp = Inputs()
        self.cv = clinvar(self.inp)
        self.residues = self.cv["set"] if scope == "full_set" else [163, 522, 614, 2060]
        self.partner_rows = partners(self.inp, self.residues)
        self.partner = {(r["human_position"], r["species"]): r for r in self.partner_rows}
        self.sample = c5_sample(self.inp, self.cv["set"], partners(self.inp, self.cv["set"]), scope)
        self.cl2 = CL2Reading.from_inputs(self.inp)
        _, self.gate_rows = self.inp.table(GATE_TABLE)
        _, self.s13_rows = self.inp.table(S13_TABLE)
        self.mapping_rows = {sp: self.inp.table(MAPPING[sp])[1] for sp in SPECIES}
        self.entry_species = {e: r["species"] for e, r in self.cl2.entry_rows.items()}
        self.mmcif = {e: self.inp.mmcif(e) for e in self.entry_species}
        self.types = {e: residue_types(text) for e, (_, text) in self.mmcif.items()}
        self.status_fn = l2_status

    def gate(self, rows=None):
        return {r["entry"]: r for r in (rows or self.gate_rows)}


def struct_rows(w: World, cl2: CL2Reading, gate_rows: list[dict], withdrawn: dict, verdicts: dict, c5s_record: str,
                seg_record: str, status_fn=None) -> list[dict]:
    """L2's rows. withdrawn: (entry, chain) -> {author n: reason}; verdicts: (entry, chain, n) -> verdict."""
    status_fn = status_fn or w.status_fn
    gate = {r["entry"]: r for r in gate_rows}
    s13 = {r["entry"]: r for r in w.s13_rows}
    rows = []
    for h in w.residues:
        for (e, c) in sorted(cl2.chains):
            ch = cl2.chains[(e, c)]
            pr = w.partner.get((h, ch.species))
            if pr is None or pr["correspondence"] != "pair":
                continue
            p = pr["partner_position"]
            gone = withdrawn.get((e, c), {})
            st, path, why, n, rule = status_fn(ch, p, frozenset(gone))
            res = next((r for r in ch.residues if r.n == n), None) if n is not None else None
            if st == "withdrawn (C5-S)":
                why = gone[n]
            seg = cl2.segment_row(e, c, res.seg) if res else None
            declared = ch.declared.get(n) if st == "joined" else None
            if st == "joined" and res and res.kinds:
                raise SystemExit(f"{e} {c} author {n}: joined with an exceptions row that unjoins it")
            reads_exc = st == "not joined" or rule in ("step2-r11c", "step3-r5", "step3-r7", "step3-r9") or declared
            verdict = verdicts.get((e, c, n)) if st in ("joined", "withdrawn (C5-S)") else None
            g, s = gate[e], s13[e]
            rows.append({
                "human_position": h, "species": ch.species, "partner_numbering": NUMBERING[ch.species],
                "partner_position": p, "partner_residue": pr["partner_residue"], "entry": e, "chain": c, "status": st,
                "join_path": path or None,
                "checked_against_sifts": (seg["checked_against_sifts"] == "true") if path else None,
                "not_joined_reason": why or None, "author_number": n,
                "structure_residue": w.types[e].get((c, n, "")) if n is not None else None,
                "differs_from_reference": (declared is not None) if st == "joined" else None,
                "declaration": declared, "cl2_segment": res.seg if res else None,
                "gate_case": g["gate_case"], "gate_case_reason": g["gate_case_reason"] or None,
                "state_class_a": s["class_a"], "state_class_b": s["class_b_fixed"],
                "state_class_minus_0_5": s["class_at_minus_0_5"], "state_class_plus_0_5": s["class_at_plus_0_5"],
                "gate_radius_a": s["radius_a"], "deposited_words": s["deposited_words"],
                "deposited_implies": s["deposited_implies"], "local_model_quality": "not assessed",
                "c5s_verdict": verdict,
                "c5s_check_result": (seg_record if why == "withdrawn with its segment (C5-S's segment rule)"
                                     else c5s_record) if verdict or st == "withdrawn (C5-S)" else None,
                "structure_record": w.mmcif[e][0],
                "numbering_tables": ";".join([CL2["entries"], CL2["segments"]] + ([CL2["exceptions"]] if reads_exc
                                                                                  else [])),
                "state_table": S13_TABLE, "gate_case_table": GATE_TABLE, "mapping_table": MAPPING[ch.species]})
            if n is not None and rows[-1]["structure_residue"] is None:
                raise SystemExit(f"{e} {c} author {n}: no atom record holds the residue")
    return rows


def entry_status(rows: list[dict]) -> dict:
    first = {}
    for r in rows:
        lab = f"joined {r['join_path']}" if r["status"] == "joined" else r["status"]
        k = (r["human_position"], r["entry"])
        first[k] = min(first.get(k, lab), lab, key=STRUCT_ORDER.index)
    return first


def measures(w: World) -> list[str]:
    return ["A"] + (["B"] if any(r["class_a"] != r["class_b_fixed"] for r in w.s13_rows) else [])


def counts(w: World, rows: list[dict], gate_rows: list[dict], structures_table: str) -> list[dict]:
    first = entry_status(rows)
    gate = {r["entry"]: r["gate_case"] for r in gate_rows}
    out = []
    for h in w.residues:
        for sp in SPECIES:
            ents = sorted(e for e, s in w.entry_species.items() if s == sp)
            for m in measures(w):
                cls = {r["entry"]: r["class_a" if m == "A" else "class_b_fixed"] for r in w.s13_rows}
                c = Counter()
                for e in ents:
                    lab = first.get((h, e), "entry not analysed")
                    if lab.startswith("joined "):
                        if gate[e] in ("c", "d"):
                            c["entries_joined_gate_case_c_or_d"] += 1
                        elif cls[e] == "indeterminate":
                            c["entries_joined_indeterminate"] += 1
                        else:
                            c[f"entries_joined_{cls[e]}_{'agree' if lab == 'joined agree' else 'path_a_only'}"] += 1
                    else:
                        c["entries_" + {"withdrawn (C5-S)": "withdrawn_c5s", "not joined": "not_joined",
                                        "modelled, not placed": "modelled_not_placed",
                                        "not determinable": "not_determinable", "not modelled": "not_modelled",
                                        "entry not analysed": "not_analysed"}[lab]] += 1
                row = {"human_position": h, "species": sp, "class_measure": m, "entries": len(ents)}
                for name, *_ in TABLES["cl4_structure_counts"][4:-1]:
                    row[name] = c.get(name, 0)
                row["structures_table"] = structures_table
                out.append(row)
    return out


def vus_counts(w: World, clin: list[dict], rows: list[dict], gate_rows: list[dict], clinvar_table: str,
               structures_table: str) -> list[dict]:
    gate = {r["entry"]: r["gate_case"] for r in gate_rows}
    joins = defaultdict(list)
    for r in rows:
        if r["status"] == "joined":
            joins[r["human_position"]].append(r)
    out = []
    for subset in ("VUS", "VUS-high (apart)"):
        hs = [r["human_position"] for r in clin if r["subset"] == subset]
        for unit in ("records", "residues"):
            items = hs if unit == "records" else sorted(set(hs))
            for scope in ("agree", "agree or path A only"):
                for sp in SPECIES + ["any"]:
                    for m in measures(w):
                        cls = {r["entry"]: r["class_a" if m == "A" else "class_b_fixed"] for r in w.s13_rows}
                        t = Counter()
                        for h in items:
                            js = [r["entry"] for r in joins.get(h, []) if (scope != "agree" or r["join_path"] == "agree")
                                  and (sp == "any" or r["species"] == sp)]
                            ok = [e for e in js if gate[e] in ("a", "b")]
                            cl = any(cls[e] == "closed" for e in ok)
                            op = any(cls[e] == "open" for e in ok)
                            t["n_total"] += 1
                            t["n_closed"] += cl
                            t["n_open"] += op
                            t["n_both"] += cl and op
                            t["n_joined_other_only"] += bool(js) and not cl and not op
                            t["n_not_joined"] += not js
                        out.append({"subset": subset, "unit": unit, "join_scope": scope, "species": sp,
                                    "class_measure": m, **{k: t.get(k, 0) for k in
                                                           ("n_total", "n_closed", "n_open", "n_both",
                                                            "n_joined_other_only", "n_not_joined")},
                                    "clinvar_table": clinvar_table, "structures_table": structures_table})
    return out


# --- C5-S ----------------------------------------------------------------------------------------------------------

def c5s_setup(w: World, cl2: CL2Reading):
    departing = defaultdict(set)
    for s in cl2.segments:
        if s["departs"] == "true":
            departing[(s["entry"], s["chain"])].add(int(s["segment"]))
    ref_e, ref_c = c5s.REFERENCE
    ref = c5s.labelled(cl2.chains[(ref_e, ref_c)], c5s.ca_atoms(w.mmcif[ref_e][1], ref_c), set())
    cas = {}
    for e in c5s.WOLL:
        for (ee, c) in cl2.chains:
            if ee == e:
                cas[(e, c)] = c5s.ca_atoms(w.mmcif[e][1], c)
    return departing, ref, cas


def c5s_tests(w: World, cl2: CL2Reading, rows: list[dict], setup, shift: dict | None = None,
              only: tuple | None = None) -> list[dict]:
    departing, ref, cas = setup
    pairs = {}
    tests = []
    for r in rows:
        if r["status"] != "joined" or r["join_path"] != "path A only" or r["human_position"] not in w.sample["all"]:
            continue
        if only and (r["entry"], r["chain"], r["partner_position"]) != only:
            continue
        key = (r["entry"], r["chain"])
        if r["entry"] not in c5s.WOLL:
            raise SystemExit(f"{key}: a join on path A alone outside the six Woll et al. entries")
        if key not in pairs:
            labels = c5s.labelled(cl2.chains[key], cas[key], departing[key], (shift or {}).get(key, 0))
            pairs[key] = c5s.Pair(labels, ref)
        t = c5s.test_join(pairs[key], r["partner_position"])
        tests.append({"entry": r["entry"], "chain": r["chain"], "author_number": r["author_number"],
                      "partner_position": r["partner_position"], "human_position": r["human_position"],
                      "segment": r["cl2_segment"], **t})
    return tests


def withdrawals(cl2: CL2Reading, tests: list[dict]) -> tuple[dict, list]:
    out = defaultdict(dict)
    for t in tests:
        if t["verdict"] == "counts against":
            out[(t["entry"], t["chain"])][t["author_number"]] = "coordinates disagree with 9PWO (C5-S)"
    segs = c5s.segment_rule(tests)
    for e, c, sg in segs:
        for r in cl2.chains[(e, c)].residues:
            if r.seg == sg and r.joined:
                out[(e, c)].setdefault(r.n, "withdrawn with its segment (C5-S's segment rule)")
    return out, segs


# --- the checks ----------------------------------------------------------------------------------------------------

def check_p0(w: World, segments_copy: bytes | None = None) -> dict:
    obs = {}
    _, s2 = w.inp.table(S2_TABLE)
    cols = list(s2[0].keys())
    need(len(s2) == 7963 and len(cols) == 37 and len({r["variant_id"] for r in s2}) == 7963,
         f"S2's table: {len(s2)} rows, {len(cols)} columns")
    keys = {"entries": ["entry", "scope", "entity", "chain"], "segments": ["entry", "chain", "segment"],
            "exceptions": ["entry", "chain", "kind", "author_first"]}
    for name, tid in CL2.items():
        t = w.inp.tables[tid]
        copy_bytes = segments_copy if (name == "segments" and segments_copy is not None) else w.inp.data[tid]
        cur = git_bytes("show", f"{CL2_CURATION[0]}:{CL2_CURATION[1]}/cl2_numbering_{name}.tsv").decode("utf-8")
        body = [ln for ln in cur.split("\n") if ln and not ln.startswith("#")]
        mine = [ln for ln in copy_bytes.decode("utf-8").split("\n") if ln]
        diff = [i for i, (a, b) in enumerate(zip(body, mine)) if a != b]
        need(len(body) == len(mine) and not diff, f"CL-2's {name} copy differs from its curation file at "
                                                  f"{CL2_CURATION[0]}: row {diff[:1]}, {len(body)} against {len(mine)}")
        _, rows = read_tsv(copy_bytes)
        k = [tuple(r[c] for c in keys[name]) for r in rows]
        need(len(set(k)) == len(k), f"CL-2's {name}: its key is not distinct")
        if name == "exceptions":
            need(all(r["author_first"] for r in rows), "an exceptions row with an empty author_first")
        obs[name] = {"record": tid, "rows": len(rows)}
        heads = [ln for ln in cur.split("\n") if ln.startswith("#")]
        need("# Run: complete" in heads and "# Outcomes: usable" in heads, f"CL-2's {name}: the run is not usable")
        faults = [h for h in heads if re.match(r"^# K\S*-P \[", h)]
        need(faults and all(" caught" in h and "NOT CAUGHT" not in h for h in faults),
             f"CL-2's {name}: a planted fault not caught")
        need(any(h.startswith("# K9 [labelled] pass") for h in heads), f"CL-2's {name}: K9 does not pass")
    need(all(r["k9_sum_holds"] == "true" for r in w.cl2.entries if r["scope"] == "chain")
         and len([r for r in w.cl2.entries if r["scope"] == "chain"]) == 104, "k9_sum_holds is not true in 104 chains")
    for tid in (S2_TABLE, S13_TABLE, GATE_TABLE):
        t = w.inp.tables[tid]
        runs = {r["id"] for r in __import__("common").records("run")}
        need(t["provenance"]["was_generated_by"] in runs, f"{t['name']}: its run record is missing")
    need(len(w.gate_rows) == 26 and all(r["gate_case"] in "abcd" and len(r["gate_case"]) == 1 for r in w.gate_rows)
         and all(r["gate_case_reason"] for r in w.gate_rows if r["gate_case"] in "cd"), "CL-3's gate cases")
    found = list(validate(Graph(GRAPH)))
    need(not found, f"the validator reports {len(found)}: {[str(f) for f in found[:2]]}")
    obs.update({"s2": {"record": S2_TABLE, "rows": 7963, "columns": 37}, "s13": S13_TABLE, "gate": GATE_TABLE,
                "validator_findings": 0, "p0_4": "the recording tool reviewed by a fresh critic and its findings "
                                                 "applied (commit ef73c06), as the vault's record states"})
    return obs


def check_c2(cv: dict) -> dict:
    got = c2_counts(cv)
    for k, v in EXPECT_C2.items():
        need(got[k] == v, f"C2: {k} is {got[k]}, the criteria's {v}")
    return got


def check_c3(cv: dict) -> dict:
    """Rule 3, applied: every included record's Xaa is P21817-1's residue there."""
    bad = [r["accession_version"] for r in cv["excluded"] if r["rule"] == 3]
    need(not bad, f"C3: excluded by rule 3: {bad}")
    return {"excluded_by_rule_3": 0}


def check_c4(tables: dict, pending: dict, graph_ids: dict) -> dict:
    bad = []
    for name, rows in tables.items():
        for rc, (kind, several, backs) in RECORD_COLUMNS[name].items():
            for i, r in enumerate(rows):
                cell = r.get(rc)
                if not cell:
                    if any(r.get(b) not in (None, "") for b in backs) and rc not in ("a6_record", "c5s_check_result"):
                        bad.append(f"{name} row {i}: {rc} empty")
                    if rc == "a6_record" and r.get("a6_entries"):
                        bad.append(f"{name} row {i}: a6_record empty")
                    if rc == "c5s_check_result" and r.get("c5s_verdict"):
                        bad.append(f"{name} row {i}: c5s_check_result empty")
                    continue
                for v in cell.split(";") if several else [cell]:
                    if not v.startswith(f"cs:{kind}.") or (v not in graph_ids.get(kind, set())
                                                            and v not in pending.get(kind, set())):
                        bad.append(f"{name} row {i}: {rc} {v} names no {kind} record")
    need(not bad, f"C4: {len(bad)}: {bad[:3]}")
    return {"record_cells_checked": sum(len(rows) * len(RECORD_COLUMNS[n]) for n, rows in tables.items())}


def check_c7(w: World, rows: list[dict]) -> dict:
    bad = []
    for r in rows:
        if r["status"] != "joined":
            continue
        want = ONE_TO_THREE[r["partner_residue"]]
        if r["structure_residue"] != want and not (r["differs_from_reference"] and r["declaration"]):
            bad.append(f"human {r['human_position']} {r['entry']} {r['chain']} author {r['author_number']}: "
                       f"{r['structure_residue']}, the partner {want}")
    need(not bad, f"C7: {len(bad)}: {bad[:3]}")
    return {"joined_rows": sum(r["status"] == "joined" for r in rows)}


def report_c7r(w: World, rows: list[dict]) -> dict:
    blind = {(p["human_position"], p["species"]): (p["c7_blind_plus1"], p["c7_blind_minus1"]) for p in w.partner_rows}
    out = Counter()
    for r in rows:
        if r["status"] == "joined":
            b = blind[(r["human_position"], r["species"])]
            if b[0]:
                out[f"{r['species']}: +1"] += 1
            if b[1]:
                out[f"{r['species']}: -1"] += 1
    return {"joined_rows_blind": dict(out),
            "residues_blind_plus1": sorted({p["human_position"] for p in w.partner_rows if p["c7_blind_plus1"]}),
            "residues_blind_minus1": sorted({p["human_position"] for p in w.partner_rows if p["c7_blind_minus1"]})}


def check_c8(w: World, rows: list[dict]) -> dict:
    bad = [r for r in rows if r["status"] == "joined" and w.entry_species[r["entry"]] != r["species"]]
    need(not bad, f"C8: {len(bad)} cross-species joins: {[(r['human_position'], r['entry']) for r in bad[:3]]}")
    return {"joined_rows": sum(r["status"] == "joined" for r in rows)}


def check_c9(w: World, gn: list[dict]) -> dict:
    _, s2 = w.inp.table(S2_TABLE)
    by = {r["variant_id"]: r for r in s2}
    bad = []
    for r in gn:
        s = by[r["variant_id"]]
        for t in ("exome", "genome"):
            if r[f"{t}_present"] != (s[f"{t}_ac"] != ""):
                bad.append(f"{r['variant_id']} {t}_present")
            for k in ("ac", "an"):
                if (str(r[f"{t}_{k}"]) if r[f"{t}_{k}"] is not None else "") != s[f"{t}_{k}"]:
                    bad.append(f"{r['variant_id']} {t}_{k}")
            if (r[f"{t}_filters"] or "") != s[f"{t}_filters"]:
                bad.append(f"{r['variant_id']} {t}_filters")
        if (r["flags"] or "") != s["flags"]:
            bad.append(f"{r['variant_id']} flags")
        if r["observed_pass"] != observed_pass(r) or str(r["observed_pass"]).lower() != s["observed_pass"]:
            bad.append(f"{r['variant_id']} observed_pass")
    want = {v for v, s in by.items() if int(s["residue"]) in set(w.residues)}
    need({r["variant_id"] for r in gn} == want, "C9: the rows at the set are not S2's")
    filt = {v for v in want if by[v]["exome_filters"] or by[v]["genome_filters"]}
    need(filt == {r["variant_id"] for r in gn if r["exome_filters"] or r["genome_filters"]}, "C9: filtered rows")
    need(not bad, f"C9: {len(bad)}: {bad[:3]}")
    return {"rows": len(gn), "rows_with_a_filter": len(filt)}


def check_c10(w: World, b: dict, gate_rows=None, tests=None) -> dict:
    cl2 = b["cl2"]
    res = recount.run({"cl4_structures": [strs(r) for r in b["structures"]],
                       "cl4_structure_counts": [strs(r) for r in b["counts"]],
                       "cl4_vus_counts": [strs(r) for r in b["vus"]]},
                      (cl2.entries, cl2.segments, cl2.exceptions), gate_rows or b["gate_rows"], w.s13_rows,
                      w.mapping_rows, [strs(r) for r in b["clinvar"]], w.residues, tests if tests is not None
                      else b["tests"], True)
    need(not res["differences"], f"C10: {len(res['differences'])}: {res['differences'][:3]}")
    return {"rows_recounted": res["rows"], "withdrawn_segments": [list(x) for x in res["withdrawn_segments"]]}


def check_c11(cl2: CL2Reading) -> dict:
    bad = guards(cl2)
    need(not bad, f"C11: {len(bad)}: {bad[:3]}")
    return {"segments": len(cl2.segments), "chains": len(cl2.chains)}


C11U = [(("5TB0", "B"), 4260, "step3-r9"), (("6X35", "B"), 237, "step3-r5")]


def check_c11u(cl2: CL2Reading, status_fn) -> dict:
    out = []
    for key, p, rule in C11U:
        a = status_fn(cl2.chains[key], p, frozenset())
        r = recount.derive(recount.Chains(cl2.entries, cl2.segments, cl2.exceptions), key, p, set())
        out.append({"chain": list(key), "p": p, "build": [a[0], a[2], a[4]], "c10": list(r)})
        need(a[0] == "not determinable" and a[4] == rule and (a[0], a[2]) == r,
             f"C11-U at {key} {p}: build {a[0]!r} {a[4]} {a[2]!r}; C10 {r}")
    return {"positions": out}


def check_c11s(status_fn) -> dict:
    out = []
    for case in synthetic.CASES:
        t = synthetic.tables(case)
        ch = next(iter(CL2Reading(*t).chains.values()))
        a = status_fn(ch, case["p"], frozenset(case["withdrawn"]))
        r = recount.synthetic(t, case["p"], case["withdrawn"])
        exp = case["expect"]
        ok = (a[0], a[4], a[2], a[3]) == exp and r == (exp[0], exp[2])
        out.append({"case": case["name"], "expected": list(exp), "build": [a[0], a[4], a[2], a[3]], "c10": list(r),
                    "ok": ok})
        need(ok, f"C11-S {case['name']}: build {a}, C10 {r}, expected {exp}")
    return {"cases": out}


def check_c5n(w: World, rows: list[dict]) -> dict:
    agree = [{"entry": r["entry"], "chain": r["chain"], "species": r["species"], "author_number": r["author_number"],
              "partner_position": r["partner_position"]}
             for r in rows if r["status"] == "joined" and r["join_path"] == "agree"
             and r["human_position"] in w.sample["all"]]
    entries = sorted({x["entry"] for x in agree})
    res = c5n.rederive(agree, {e: w.inp.sifts(e)[1] for e in entries}, {e: w.mmcif[e][1] for e in entries})
    bad = [x for x in res if not x["equal"]]
    need(not bad, f"C5-N: {len(bad)} of {len(res)} differ: {bad[:2]}")
    return {"compared": len(res), "entries": entries, "sifts_records": [w.inp.sifts(e)[0] for e in entries]}


def fetched(w: World, prefix: str, names: list[str]) -> tuple[dict, list[str]]:
    out, rids = {}, []
    for name in names:
        rid, data = w.inp.raw_at(f"{prefix}{name}")
        out[name] = data
        rids.append(rid)
    return out, rids


def check_c5c(w: World, clin: list[dict], conds: list[dict]) -> dict:
    rows = [r for r in clin if r["human_position"] in w.sample["all"]]
    files, rids = fetched(w, "raw/clinvar/2026-10-12/c5_vcv_", [f"{r['uid']}.xml" for r in rows])
    res = c5cg.c5c(rows, [c for c in conds if c["human_position"] in w.sample["all"]],
                   {k.split(".")[0]: v for k, v in files.items()})
    need(not res["failures"], f"C5-C: {len(res['failures'])}: {res['failures'][:2]}")
    return {**res, "retrievals": rids}


def check_c5g(w: World, gn: list[dict]) -> dict:
    rows = [r for r in gn if r["human_position"] in w.sample["all"]]
    files, rids = fetched(w, "raw/gnomad/2026-10-12/c5_variant_", [f"{r['variant_id']}.json" for r in rows])
    _, meta = w.inp.raw_at("raw/gnomad/2026-10-12/c5_browser_dataset_metadata_main.ts")
    _, news = w.inp.raw_at("raw/gnomad/2026-10-12/c5_news.html")
    rel = c5cg.release_check(meta, news)
    res = c5cg.c5g(rows, {k[:-5]: v for k, v in files.items()}, rel)
    need(not res["failures"], f"C5-G: {len(res['failures'])}: {res['failures'][:2]}")
    return {**res, "retrievals": rids}


def strs(r: dict) -> dict:
    """A row as its TSV cells read back: the second script sees what the table holds."""
    return {k: ("" if v is None else ("true" if v is True else "false" if v is False else str(v))) for k, v in r.items()}


# --- assembling a build --------------------------------------------------------------------------------------------

def assemble(w: World, cl2=None, gate_rows=None, tests=None, status_fn=None, setup=None, c5s_record="cs:check_result."
             + "C" * 32, seg_record="cs:check_result." + "S" * 32) -> dict:
    """The rows of every table (record ids of this run's own records are filled in later)."""
    cl2 = cl2 or w.cl2
    gate_rows = gate_rows or w.gate_rows
    base = struct_rows(w, cl2, gate_rows, {}, {}, c5s_record, seg_record, status_fn)
    if tests is None:
        tests = c5s_tests(w, cl2, base, setup or c5s_setup(w, cl2))
    gone, segs = withdrawals(cl2, tests)
    verdicts = {(t["entry"], t["chain"], t["author_number"]): t["verdict"] for t in tests}
    rows = struct_rows(w, cl2, gate_rows, gone, verdicts, c5s_record, seg_record, status_fn)
    clin, conds, excl = clinvar_rows(w.cv) if w.scope == "full_set" else _clin_four(w)
    return {"cl2": cl2, "gate_rows": gate_rows, "tests": tests, "segments_withdrawn": segs, "structures": rows,
            "clinvar": clin, "conditions": conds, "exclusions": excl, "gnomad": gnomad(w.inp, w.residues),
            "set": set_rows(w.inp, w.cv, set(w.sample["all"])) if w.scope == "full_set" else
            [r for r in set_rows(w.inp, w.cv, set(w.sample["all"])) if r["human_position"] in w.residues],
            "partners": w.partner_rows}


def _clin_four(w: World):
    clin, conds, excl = clinvar_rows(w.cv)
    keep = set(w.residues)
    return [r for r in clin if r["human_position"] in keep], [c for c in conds if c["human_position"] in keep], excl


def add_counts(w: World, b: dict, structures_table: str, clinvar_table: str) -> None:
    b["counts"] = counts(w, b["structures"], b["gate_rows"], structures_table)
    b["vus"] = vus_counts(w, b["clinvar"], b["structures"], b["gate_rows"], clinvar_table, structures_table)


# --- the records ---------------------------------------------------------------------------------------------------

def criteria_table() -> dict[str, list[str]]:
    """The criteria's check table as committed: label -> [label, what, kind, passes when, fails when]."""
    text = (VAULT / CRITERIA).read_text(encoding="utf-8")
    sect = text.split("## Checks and planted faults, each with what fails it", 1)[1]
    sect = sect.split("**If a planted fault is missed,**", 1)[0]
    out = {}
    for ln in sect.splitlines():
        if ln.startswith("| ") and not ln.startswith(("| # ", "|---")):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            if len(cells) != 5:
                raise SystemExit(f"the criteria's check table: a row with {len(cells)} cells: {ln[:60]}")
            out[cells[0]] = cells
    return out


def first_commit_with(fragment: str, cache: dict) -> str:
    if not cache:
        for c in git_bytes("log", "--format=%h", "--reverse", "--", CRITERIA).decode().split():
            cache[c] = git_bytes("show", f"{c}:{CRITERIA}").decode("utf-8")
    for c, text in cache.items():
        if fragment in " ".join(text.split()):
            return c
    raise SystemExit(f"not in any committed version of the criteria: {fragment[:60]}")


# check label -> (its planted faults, the first its control; the rest records of their own)
GROUPS = [("P0", ["P0-P"]), ("C1", ["C1-P"]), ("C2", ["C2-P"]), ("C3", ["C3-P"]), ("C4", ["C4-P"]),
          ("C5-C", ["C5-C-P"]), ("C5-G", ["C5-G-P"]), ("C5-S", ["C5-S-P", "C5-S-W-P"]), ("C5-N", ["C5-N-P"]),
          ("C7", ["C6-P"]), ("C7-R", []), ("C8", ["C8-P"]), ("C9", ["C9-P"]), ("C10", ["C10-P", "C10-G-P", "C10-W-P"]),
          ("C11-U", ["C11-U-P"]), ("C11-S", []), ("C11", ["C11-P"])]
STOPS = {"P0", "C1", "C2", "C4", "C5-C", "C5-G", "C5-N", "C7", "C8", "C9", "C10", "C11-U", "C11-S", "C11"}


def table_record(name: str, rows: list[dict], scope: str, commit: str, run_id: str, method_id: str,
                 used: list[str]) -> tuple[str, bytes, dict]:
    cols = TABLES[name]
    data = tsv_bytes([c[0] for c in cols], [[r.get(c[0]) for c in cols] for r in rows])
    path = f"tables/cl4/{commit}/{scope}/{name}.tsv"
    rec = normalise({"schema_version": "0.2.0", "type": "table", "synthetic": False, "name": name, "path": path,
                     "media_type": "text/tab-separated-values", "sha256": sha(data), "bytes": len(data),
                     "row_count": len(rows),
                     "columns": [{k: v for k, v in (("name", c[0]), ("datatype", c[1]), ("required", c[2]),
                                                    ("description", c[3]), ("unit", c[4]), ("numbering", c[5]))
                                  if v is not None} for c in cols],
                     "primary_key": KEYS[name],
                     "provenance": {"was_generated_by": run_id, "method": method_id, "used": sorted(set(used)),
                                    "was_attributed_to": AGENT_LUMEN}})
    return path, data, rec


def check_record(label: str, outcome: str, control: dict, observed: dict, run_id: str, method_id: str,
                 used: list[str], crit: dict, cache: dict, note: str | None = None) -> dict:
    fails = crit[label][4]
    body = {"schema_version": "0.2.0", "type": "check_result", "synthetic": False, "check": f"CL4.{label}",
            "mission": MISSION, "criterion": {"document": CRITERIA, "pre_registered_in": first_commit_with(fails, cache),
                                             "fails_if": fails},
            "outcome": outcome, "control": control, "observed": json.loads(json.dumps(observed, default=str)),
            "provenance": {"was_generated_by": run_id, "method": method_id, "used": sorted(set(used)),
                           "was_attributed_to": AGENT_LUMEN}}
    if note:
        body["note"] = note
    return normalise(body)


def main(argv: list[str] | None = None) -> int:
    import faults
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scope", choices=("full_set", "four_residues"), default="full_set")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    started, t0 = now(), time.time()
    commit = git_bytes("rev-parse", "--short=7", "HEAD").decode().strip()
    dirty = git_bytes("status", "--porcelain", "--", "how/runtime/channelscope/cl4", CRITERIA).decode().strip()
    if args.write and dirty:
        print(f"NOT WRITTEN: the code or the criteria are not committed as they are:\n{dirty}")
        return 1
    log = []

    def step(msg):
        log.append(f"{time.time() - t0:7.1f}s {msg}")
        print(log[-1], flush=True)

    w = World(args.scope)
    step(f"inputs read through C1's guard: {len(w.inp.data)}")
    outcome, observed = {}, {}

    def run(label, fn):
        try:
            observed[label] = fn()
            outcome[label] = "pass"
        except Fail as e:
            observed[label] = {"failure": str(e)}
            outcome[label] = "fail"
        step(f"{label}: {outcome[label]}{'' if outcome[label] == 'pass' else ': ' + observed[label]['failure'][:200]}")

    observed["C1"] = {"inputs": len(w.inp.data), "refused": 0}
    outcome["C1"] = "pass"
    run("P0", lambda: check_p0(w))
    run("C2", lambda: check_c2(w.cv))
    run("C3", lambda: check_c3(w.cv))
    run("C11", lambda: check_c11(w.cl2))
    run("C11-U", lambda: check_c11u(w.cl2, l2_status))
    run("C11-S", lambda: check_c11s(l2_status))
    setup = c5s_setup(w, w.cl2)
    b = assemble(w, setup=setup)
    step(f"assembled: {len(b['structures'])} structure rows; C5-S tested {len(b['tests'])} joins")
    c5s_p = faults.c5s_planted(w, w.cl2, setup)
    against = [t for t in b["tests"] if t["verdict"] == "counts against"]
    observed["C5-S"] = {"tested": len(b["tests"]), "verdicts": dict(Counter(t["verdict"] for t in b["tests"])),
                        "counts_against": [{k: t[k] for k in ("entry", "chain", "author_number", "partner_position",
                                                              "offset", "fits")} for t in against],
                        "segments_withdrawn": [list(s) for s in b["segments_withdrawn"]],
                        "joins": [[t["entry"], t["chain"], t["author_number"], t["partner_position"], t["verdict"],
                                   t["offset"]] for t in b["tests"]],
                        "thresholds": "window p-15 to p+15, nearest 9PWO CA under 2.0 A, at least 10 offsets; "
                                      "consistent at 75% offset 0; three fits r = 40, 60, 80; rule B"}
    outcome["C5-S"] = "pass" if not against else "fail"
    step(f"C5-S: {observed['C5-S']['verdicts']}; C5-S-P {c5s_p}")
    run("C7", lambda: check_c7(w, b["structures"]))
    observed["C7-R"], outcome["C7-R"] = report_c7r(w, b["structures"]), "not-run"
    run("C8", lambda: check_c8(w, b["structures"]))
    run("C9", lambda: check_c9(w, b["gnomad"]))
    run("C5-N", lambda: check_c5n(w, b["structures"]))
    run("C5-C", lambda: check_c5c(w, b["clinvar"], b["conditions"]))
    run("C5-G", lambda: check_c5g(w, b["gnomad"]))
    add_counts(w, b, "cs:table." + "T" * 32, "cs:table." + "U" * 32)
    run("C10", lambda: check_c10(w, b))
    res = {"c5c": observed["C5-C"] if outcome["C5-C"] == "pass" else {"compared": []}, "c5s_p": c5s_p}

    # this run's own records
    ended = now()
    digest = code_digest(HERE)
    scripts = {f"script_{p.name}": sha(p.read_bytes()) for p in sorted(HERE.glob("*.py"))}
    method = normalise({
        "schema_version": "0.2.0", "type": "method", "synthetic": False, "name": "channelscope.cl4.compose",
        "version": "0.1.0", "was_attributed_to": AGENT_LUMEN,
        "description": "CL-4: the composition over a residue set fixed in advance, by the criteria "
                       f"{CRITERIA} (version 3, with Q1 to Q3 answered (c), (c), (c)): L1 partners, L2 structures by "
                       "L2's rule on CL-2's tables with CL-3's classes and gate cases, L3 gnomAD, L4 ClinVar; checks "
                       "and planted faults as the criteria's table fixes them. The run's end is taken before its "
                       "records are assembled; C4 and C4-P then run on the assembled records.",
        "implementation": {"software": "channelscope cl4 (how/runtime/channelscope/cl4)", "version": "0.1.0",
                           "code_digest": digest},
        "parameters": {"scope": args.scope, "c5_sample": ",".join(map(str, w.sample["all"])),
                       "c5s_thresholds": observed["C5-S"]["thresholds"],
                       "q1": "(c): VUS-high reported apart as 'VUS-high (apart)', never added to the VUS",
                       "q2": "(c): the full set, the four worked residues added to C5's sample",
                       "q3": "(c): L3 in the same run, since S2's records exist (P0.1)",
                       **{f"absent_{k}": v for k, v in ABSENT.items()},
                       "input_tables": ";".join([*MAPPING.values(), *CL2.values(), S13_TABLE, GATE_TABLE, S2_TABLE]),
                       "a6_file": "what/references/a6_stated_correspondences.tsv",
                       "a6_sha256": sha(w.inp.data["a6"]), "criteria_commit": "2004787", "build_commit": commit,
                       **scripts}})
    used_files = []
    for key, data in w.inp.data.items():
        if key == "a6":
            continue
        rec = w.inp.retrievals.get(key) or w.inp.tables.get(key)
        path = rec.get("stored_at") or rec.get("path")
        used_files.append({"path": path, "sha256": sha(data), "bytes": len(data)})
    run_rec = normalise({"schema_version": "0.2.0", "type": "run", "synthetic": False, "method": method["id"],
                         "command": ["python", "how/runtime/channelscope/cl4/compose.py", *sys.argv[1:]],
                         "started_at_time": started, "ended_at_time": ended,
                         "used_files": sorted(used_files, key=lambda f: f["path"]), "software": software(),
                         "environment": environment(), "was_associated_with": AGENT_SOFTWARE,
                         "acted_on_behalf_of": AGENT_LUMEN})
    crit, cache = criteria_table(), {}
    rid, mid = run_rec["id"], method["id"]
    structures_inputs = [*MAPPING.values(), *CL2.values(), S13_TABLE, GATE_TABLE, *[w.mmcif[e][0] for e in w.mmcif]]
    c5s_rec = check_record("C5-S", outcome["C5-S"], {"fault": crit["C5-S-P"][1], "outcome": "detected" if c5s_p[0]
                                                      else "missed"}, {**observed["C5-S"], "control": c5s_p[1]},
                           rid, mid, structures_inputs, crit, cache)
    seg_rec = None
    if b["segments_withdrawn"]:
        seg_rec = normalise({"schema_version": "0.2.0", "type": "check_result", "synthetic": False,
                             "check": "CL4.C5-S-segment", "mission": MISSION,
                             "criterion": {"document": CRITERIA, "pre_registered_in": first_commit_with(
                                 "every join of that segment in that chain is withdrawn the same way", cache),
                                           "fails_if": "every join of that segment in that chain is withdrawn the same way"},
                             "outcome": "fail", "control": {"fault": "none: the segment rule's record",
                                                            "outcome": "not-run"},
                             "observed": {"segments": [list(s) for s in b["segments_withdrawn"]]},
                             "provenance": {"was_generated_by": rid, "method": mid, "used": [c5s_rec["id"]],
                                            "was_attributed_to": AGENT_LUMEN}})
    for r in b["structures"]:
        if r["c5s_check_result"] == "cs:check_result." + "C" * 32:
            r["c5s_check_result"] = c5s_rec["id"]
        elif r["c5s_check_result"] == "cs:check_result." + "S" * 32:
            r["c5s_check_result"] = seg_rec["id"]
    out_tables, records = {}, []
    used = {"cl4_set": [*__import__("common").CLINVAR_BATCHES, __import__("common").CLINVAR_SEARCH,
                        __import__("common").UNIPROT["human"]],
            "cl4_partners": [*MAPPING.values(), *(w.inp.numbering_record(sp) for sp in SPECIES),
                             __import__("common").A6_RECORD],
            "cl4_structures": structures_inputs + [c5s_rec["id"]] + ([seg_rec["id"]] if seg_rec else []),
            "cl4_gnomad": [S2_TABLE, __import__("common").GNOMAD_LABEL, __import__("common").GNOMAD_TERMS],
            "cl4_clinvar": [*__import__("common").CLINVAR_BATCHES, __import__("common").CLINVAR_USE_PAGE],
            "cl4_clinvar_conditions": [*__import__("common").CLINVAR_BATCHES],
            "cl4_exclusions": [*__import__("common").CLINVAR_BATCHES]}
    rows_of = {"cl4_set": b["set"], "cl4_partners": b["partners"], "cl4_structures": b["structures"],
               "cl4_gnomad": b["gnomad"], "cl4_clinvar": b["clinvar"], "cl4_clinvar_conditions": b["conditions"],
               "cl4_exclusions": b["exclusions"]}
    files = {}
    for name, rows in rows_of.items():
        path, data, rec = table_record(name, rows, args.scope, commit, rid, mid, used[name])
        files[path], out_tables[name] = data, rows
        records.append(rec)
    tid = {r["name"]: r["id"] for r in records}
    add_counts(w, b, tid["cl4_structures"], tid["cl4_clinvar"])
    for name, rows, u in (("cl4_structure_counts", b["counts"], [tid["cl4_structures"]]),
                          ("cl4_vus_counts", b["vus"], [tid["cl4_structures"], tid["cl4_clinvar"]])):
        path, data, rec = table_record(name, rows, args.scope, commit, rid, mid, u)
        files[path], out_tables[name] = data, rows
        records.append(rec)
    pending = defaultdict(set)
    for r in [method, run_rec, c5s_rec, *([seg_rec] if seg_rec else []), *records]:
        pending[r["type"]].add(r["id"])
    graph_ids = defaultdict(set)
    for kind in ("retrieval", "table", "numbering", "check_result", "run", "method"):
        graph_ids[kind] = {r["id"] for r in __import__("common").records(kind)}
    res.update(tables=out_tables, pending=pending, graph_ids=graph_ids)
    run("C4", lambda: check_c4(out_tables, pending, graph_ids))
    step("planted faults")
    fo = faults.run_faults(w, b, res)
    for k, (ok, how) in fo.items():
        step(f"  fault {k}: {'caught' if ok else 'not run' if ok is None else 'NOT CAUGHT'}: {how[:200]}")

    # the check records
    checks = []
    for label, fl in GROUPS:
        if label == "C5-S":
            checks.append(c5s_rec)
        else:
            if fl:
                ok, how = fo[fl[0]]
                control = {"fault": crit[fl[0]][1], "outcome": "not-run" if ok is None else "detected" if ok
                           else "missed"}
            else:
                control = {"fault": "none: a report" if label == "C7-R" else "none: no planted fault is listed for "
                           "it in the criteria", "outcome": "not-run"}
            obs = dict(observed.get(label, {}))
            if fl:
                obs["control"] = fo[fl[0]][1]
            note = "a report: it has no pass or fail; observed holds what it reports" if label == "C7-R" else None
            checks.append(check_record(label, outcome[label], control, obs, rid, mid, used.get("cl4_structures")
                                       if label in ("C7", "C7-R", "C8", "C10", "C11", "C11-U", "C11-S", "C5-N")
                                       else [*CL2.values()] if label == "P0" else [S2_TABLE] if label in ("C9", "C5-G")
                                       else [*__import__("common").CLINVAR_BATCHES], crit, cache, note))
        parent = checks[-1]["id"]
        for extra in fl[1:]:
            ok, how = fo[extra]
            checks.append(check_record(extra, "not-run" if ok is None else "pass" if ok else "fail",
                                       {"fault": "none: this record reports a planted fault itself",
                                        "outcome": "not-run"}, {"what_happened": how}, rid, mid, [parent], crit,
                                       cache))
    if seg_rec:
        checks.append(seg_rec)
    failed = [k for k in STOPS if outcome.get(k) != "pass"]
    missed = [k for k, (ok, _) in fo.items() if ok is False]
    step(f"checks that stop the build and failed: {failed}; planted faults missed: {missed}")
    print(json.dumps({"rows": {k: len(v) for k, v in out_tables.items()}, "c5s": observed["C5-S"]["verdicts"],
                      "records": len(checks) + len(records) + 2}, indent=1))
    if failed or missed:
        print("NOT WRITTEN")
        return 1
    if not args.write:
        print("checked; nothing written (no --write)")
        return 0
    g = Graph(GRAPH)
    for path, data in files.items():
        g.write_bytes(path, data)
    for r in [method, run_rec, *checks, *records]:
        g.append(r)
    found = list(validate(g))
    step(f"written: {len(files)} tables, {len(checks) + len(records) + 2} records; validator findings: {len(found)}")
    for f in found[:5]:
        print("  ", f)
    return 0 if not found else 1


if __name__ == "__main__":
    raise SystemExit(main())
