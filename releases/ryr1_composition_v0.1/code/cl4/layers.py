"""layers.py - CL-4's layers L1 (partners), L3 (gnomAD) and L4 (ClinVar), and the residue set, by the criteria's
rules (*The residue set, fixed now*; *The VUS subset*; *The layers, and the rule for each*). No value is changed: every
cell is its source's, verbatim, or a stated derivation of it."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from common import (A6_RECORD, CLINVAR_BATCHES, CLINVAR_SEARCH, MAPPING, NUMBERING, S2_TABLE, SPECIES, THREE, UNIPROT,
                    Inputs)

TITLE = re.compile(r"^(NM_\d+\.\d+)\(RYR1\):c\.[^ ]+ \(p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\)$")
VUS_PREFIX = "Uncertain significance"
VUS_HIGH = "VUS-high"  # Q1, answered (c) at 23:28:41 IST on 2026-10-11: reported apart, never added to the VUS


def subset_of(description: str) -> str:
    if description.startswith(VUS_PREFIX):
        return "VUS"
    if description == VUS_HIGH:
        return "VUS-high (apart)"
    return "not VUS"


def clinvar(inp: Inputs, edit=None) -> dict:
    """Every record the held search returned, in its order, each with the first rule it fails or none. `edit`, a
    planted fault's change, is applied to the summaries in memory after the guard (C2-P, C3-P)."""
    ids = inp.json(CLINVAR_SEARCH)["esearchresult"]["idlist"]
    summ, batch_of = {}, {}
    for rid in CLINVAR_BATCHES:
        res = inp.json(rid)["result"]
        for uid in res["uids"]:
            summ[uid] = json.loads(json.dumps(res[uid]))
            batch_of[uid] = rid
    if edit:
        edit(summ)
    seq = inp.sequence("human")
    out = []
    for uid in ids:
        s = summ[uid]
        gc = s.get("germline_classification") or {}
        title, mcl = s.get("title", ""), s.get("molecular_consequence_list")
        rule, reason, n, xaa, yaa = None, "", None, None, None
        m = TITLE.match(title)
        if mcl != ["missense variant"]:
            rule, reason = 1, f"molecular_consequence_list is {json.dumps(mcl)}"
        elif not m:
            rule, reason = 2, f"the title does not name one substitution in the form NM_000540.3(RYR1):c.… (p.XaaNYaa)"
        elif m.group(1) != "NM_000540.3":
            rule, reason = 2, f"the title names {m.group(1)}, not NM_000540.3"
        elif m.group(2) not in THREE or m.group(4) not in THREE:
            rule, reason = 2, "the title names an amino acid that is not one of the twenty"
        else:
            n, xaa, yaa = int(m.group(3)), THREE[m.group(2)], THREE[m.group(4)]
            if n > len(seq) or seq[n - 1] != xaa:
                rule, reason = 3, (f"P21817-1 has {seq[n - 1] if n <= len(seq) else 'no residue'} at {n}; the title "
                                   f"names {m.group(2)}")
        conds = []
        for t in gc.get("trait_set") or []:
            mondo = [x["db_id"] for x in (t.get("trait_xrefs") or []) if x.get("db_source") == "MONDO"]
            if len(mondo) > 1:
                raise SystemExit(f"{s.get('accession_version')}: a condition with {len(mondo)} Mondo identifiers")
            conds.append({"name": t.get("trait_name", ""), "mondo": mondo[0] if mondo else ""})
        out.append({"uid": uid, "accession_version": s.get("accession_version"), "title": title, "rule": rule,
                    "reason": reason, "n": n if rule is None else None, "xaa": xaa, "yaa": yaa,
                    "protein_change": f"p.{m.group(2)}{m.group(3)}{m.group(4)}" if rule is None else "",
                    "description": gc.get("description", ""), "review_status": gc.get("review_status", ""),
                    "last_evaluated": gc.get("last_evaluated", ""), "conditions": conds, "batch": batch_of[uid]})
    included = [r for r in out if r["rule"] is None]
    return {"read": out, "included": included, "excluded": [r for r in out if r["rule"] is not None],
            "set": sorted({r["n"] for r in included}), "search": CLINVAR_SEARCH}


def set_rows(inp: Inputs, cv: dict, sample: set[int]) -> list[dict]:
    seq = inp.sequence("human")
    by_n = defaultdict(list)
    for r in cv["included"]:
        by_n[r["n"]].append(r)
    rows = []
    for n in cv["set"]:
        batches = sorted({r["batch"] for r in by_n[n]})
        rows.append({"human_position": n, "human_residue": seq[n - 1], "n_records": len(by_n[n]),
                     "in_c5_sample": n in sample, "clinvar_records": ";".join([cv["search"], *batches]),
                     "uniprot_record": UNIPROT["human"]})
    return rows


def a6_entries(inp: Inputs) -> list[tuple[str, set[int], set[int]]]:
    def positions(cell: str) -> set[int]:
        a, _, b = cell.partition("-")
        return set(range(int(a), int(b or a) + 1))

    _, rows = inp.a6()
    return [(r["id"], positions(r["human"]), positions(r["rabbit"])) for r in rows]


def partners(inp: Inputs, residues: list[int]) -> list[dict]:
    a6 = a6_entries(inp)
    rows = []
    for sp in SPECIES:
        _, mrows = inp.table(MAPPING[sp])
        by_subject = {int(r["subject_position"]): r for r in mrows if r["subject_position"]}
        seq = inp.sequence(sp)
        for h in residues:
            m = by_subject.get(h)
            if m is None:
                raise SystemExit(f"human {h}: no row in the {sp} mapping")
            pair = m["correspondence"] == "pair"
            p = int(m["object_position"]) if pair else None
            row = {"human_position": h, "species": sp, "partner_numbering": NUMBERING[sp],
                   "correspondence": m["correspondence"], "partner_position": p,
                   "partner_residue": m["object_residue"] if pair else None, "reliability": m["reliability"],
                   "reliability_reasons": m["reliability_reasons"] or None, "ambiguous": m["ambiguous"] == "true",
                   "mapping_column": int(m["column"]), "mapping_table": MAPPING[sp],
                   "c7_blind_plus1": (p < len(seq) and seq[p] == seq[p - 1]) if pair else None,
                   "c7_blind_minus1": (p > 1 and seq[p - 2] == seq[p - 1]) if pair else None,
                   "partner_numbering_record": inp.numbering_record(sp), "a6_entries": None, "a6_record": None}
            if pair and seq[p - 1] != m["object_residue"]:
                raise SystemExit(f"human {h}: the {sp} mapping's residue is not the sequence's")
            if sp == "Oryctolagus cuniculus":
                hit = [e for e, hs, rs in a6 if h in hs or (pair and p in rs)]
                if hit:
                    row["a6_entries"], row["a6_record"] = ";".join(hit), A6_RECORD
            rows.append(row)
    return rows


GNOMAD_COLS = ["exome_ac", "exome_an", "exome_filters", "genome_ac", "genome_an", "genome_filters", "joint_ac",
               "joint_an"]


def gnomad(inp: Inputs, residues: list[int]) -> list[dict]:
    from common import GNOMAD_LABEL, GNOMAD_TERMS
    _, rows = inp.table(S2_TABLE)
    want = set(residues)
    out = []
    for r in rows:
        if int(r["residue"]) not in want:
            continue
        if (r["exome_ac"] == "") != (r["exome_an"] == "") or (r["genome_ac"] == "") != (r["genome_an"] == ""):
            raise SystemExit(f"{r['variant_id']}: an allele count without its number, or the reverse")
        out.append({"human_position": int(r["residue"]), "variant_id": r["variant_id"], "hgvsc": r["hgvsc"],
                    "hgvsp": r["hgvsp"], "ref_aa": r["ref_aa"], "alt_aa": r["alt_aa"],
                    "exome_present": r["exome_ac"] != "",
                    **{c: (int(r[c]) if r[c] != "" else None) if c.endswith(("_ac", "_an")) else (r[c] or None)
                       for c in GNOMAD_COLS},
                    "genome_present": r["genome_ac"] != "", "observed_pass": r["observed_pass"] == "true",
                    "flags": r["flags"] or None, "gnomad_dataset": "gnomad_r4", "gnomad_label": "gnomAD v4.1.2",
                    "gnomad_label_record": GNOMAD_LABEL, "gnomad_table": S2_TABLE,
                    "attribution": "gnomAD (Genome Aggregation Database), dataset gnomad_r4, retrieved 2026-10-06",
                    "attribution_record": GNOMAD_TERMS})
    return sorted(out, key=lambda r: r["variant_id"])


def observed_pass(r: dict) -> bool:
    """S2's rule (gnomad_ryr1_missense.py, line 177): an allele count above 0 with no filter, in the exomes or the
    genomes."""
    return any((r[f"{t}_ac"] or 0) > 0 and not r[f"{t}_filters"] for t in ("exome", "genome"))


def clinvar_rows(cv: dict) -> tuple[list[dict], list[dict], list[dict]]:
    from common import CLINVAR_USE_PAGE
    recs, conds, excl = [], [], []
    for r in cv["included"]:
        recs.append({"human_position": r["n"], "uid": int(r["uid"]), "accession_version": r["accession_version"],
                     "title": r["title"], "protein_change": r["protein_change"], "ref_residue": r["xaa"],
                     "alt_residue": r["yaa"], "description": r["description"], "review_status": r["review_status"],
                     "last_evaluated": r["last_evaluated"], "subset": subset_of(r["description"]),
                     "n_conditions": len(r["conditions"]),
                     "n_conditions_with_mondo": sum(1 for c in r["conditions"] if c["mondo"]),
                     "clinvar_retrieval": r["batch"], "attribution": "ClinVar (NCBI), retrieved 2026-09-29",
                     "attribution_record": CLINVAR_USE_PAGE})
        for i, c in enumerate(r["conditions"], 1):
            conds.append({"human_position": r["n"], "accession_version": r["accession_version"], "condition_index": i,
                          "condition_name": c["name"], "mondo_id": c["mondo"] or None, "mondo_given": bool(c["mondo"]),
                          "clinvar_retrieval": r["batch"]})
    for r in cv["excluded"]:
        excl.append({"uid": int(r["uid"]), "accession_version": r["accession_version"], "title": r["title"],
                     "rule": r["rule"], "reason": r["reason"], "clinvar_retrieval": r["batch"]})
    return recs, conds, excl


def c2_counts(cv: dict) -> dict:
    """What check C2 compares: the set's counts on the whole held input."""
    inc, exc = cv["included"], cv["excluded"]
    per = Counter(r["n"] for r in inc)
    vus = [r for r in inc if subset_of(r["description"]) == "VUS"]
    high = [r for r in inc if subset_of(r["description"]) == "VUS-high (apart)"]
    cats = Counter(r["reason"] for r in exc)
    return {"read": len(cv["read"]), "included": len(inc), "residues": len(per),
            "multi": sum(1 for v in per.values() if v > 1), "excluded": len(exc),
            "excluded_by_rule": dict(Counter(r["rule"] for r in exc)), "categories": dict(cats),
            "vus_records": len(vus), "vus_residues": len({r["n"] for r in vus}),
            "vus_high": [r["accession_version"] for r in high]}
