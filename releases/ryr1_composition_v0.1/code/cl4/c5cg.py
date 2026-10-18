"""c5cg.py - C5-C and C5-G (the criteria, *C5-C, ClinVar* and *C5-G, gnomAD*): the fresh retrievals of C5's two
plans compared with L4's and L3's rows. Each function takes the build's rows and the fetched bytes (through check
C1's guard, by their retrieval records) and returns each comparison and the failures."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET


def from_vcv(xml: bytes) -> dict:
    """The full record under the criteria's normalisation: the trait sets of its germline classification that
    contribute to the aggregate classification, as a set of (preferred name, Mondo identifiers)."""
    root = ET.fromstring(xml)
    va = root.find(".//VariationArchive")
    if va is None:
        return {}
    gc = va.find("./ClassifiedRecord/Classifications/GermlineClassification")
    conds = set()
    for ts in gc.findall("./ConditionList/TraitSet"):
        if ts.get("ContributesToAggregateClassification") != "true":
            continue
        for tr in ts.findall("./Trait"):
            name = next((ev.text for ev in tr.findall("./Name/ElementValue") if ev.get("Type") == "Preferred"), None)
            conds.add((name, tuple(sorted(x.get("ID") for x in tr.findall("./XRef") if x.get("DB") == "MONDO"))))
    return {"accession": va.get("Accession"), "version": int(va.get("Version")), "title": va.get("VariationName"),
            "description": gc.findtext("./Description"), "review_status": gc.findtext("./ReviewStatus"),
            "last_evaluated": gc.get("DateLastEvaluated"), "conditions": conds}


def c5c(rows: list[dict], conditions: list[dict], fetched: dict[str, bytes]) -> dict:
    """rows: L4's rows at sampled residues; conditions: their condition rows; fetched: uid -> VCV XML bytes."""
    conds = {}
    for c in conditions:
        conds.setdefault(c["accession_version"], set()).add(
            (c["condition_name"], (c["mondo_id"],) if c["mondo_id"] else ()))
    out, fails = [], []
    for r in sorted(rows, key=lambda r: int(r["uid"])):
        v = from_vcv(fetched[str(r["uid"])]) if str(r["uid"]) in fetched else {}
        acc, ver = r["accession_version"].rsplit(".", 1)
        res = {"uid": int(r["uid"]), "held": r["accession_version"]}
        if not v:
            res["outcome"] = "no record returned"
            fails.append(res)
        elif v["accession"] != acc:
            res["outcome"] = f"another accession, {v['accession']}"
            fails.append(res)
        elif v["version"] < int(ver):
            res["outcome"], res["fetched"] = "a lower version", v["version"]
            fails.append(res)
        elif v["version"] > int(ver):
            res["fetched"] = f"{acc}.{v['version']}"
            res["outcome"] = "higher version: title equal" if v["title"] == r["title"] else "higher version: title differs"
            res["update"] = {"description": v["description"], "review_status": v["review_status"],
                             "last_evaluated": v["last_evaluated"],
                             "conditions": sorted([n, list(m)] for n, m in v["conditions"])}
            if v["title"] != r["title"]:
                fails.append(res)
        else:
            held = {"title": r["title"], "description": r["description"], "review_status": r["review_status"],
                    "last_evaluated": r["last_evaluated"].split(" ")[0].replace("/", "-"),
                    "conditions": conds.get(r["accession_version"], set())}
            diff = [k for k in held if held[k] != v[k]]
            res["outcome"] = "same version: equal" if not diff else f"same version: differs in {', '.join(diff)}"
            if diff:
                res["differences"] = {k: [str(held[k]), str(v[k])] for k in diff}
                fails.append(res)
        out.append(res)
    return {"compared": out, "failures": fails,
            "higher_version": sum(1 for x in out if str(x["outcome"]).startswith("higher version"))}


LABEL = re.compile(r"gnomad_r4:\s*['\"]([^'\"]+)['\"]")
RELEASE = re.compile(r"gnomAD v(\d+)\.(\d+)(?:\.(\d+))?")


def release_check(metadata_ts: bytes, news_html: bytes) -> dict:
    m = LABEL.search(metadata_ts.decode("utf-8"))
    label = m.group(1) if m else None
    later = sorted({x.group(0) for x in RELEASE.finditer(news_html.decode("utf-8", errors="replace"))
                    if tuple(int(g or 0) for g in x.groups()) > (4, 1, 2)})
    return {"label": label, "news_releases_after_v4_1_2": later,
            "later_release_recorded": label != "gnomAD v4.1.2" or bool(later)}


def c5g(rows: list[dict], fetched: dict[str, bytes], release: dict) -> dict:
    out, fails = [], []
    for r in sorted(rows, key=lambda r: r["variant_id"]):
        data = json.loads(fetched[r["variant_id"]])
        v = (data.get("data") or {}).get("variant")
        res = {"variant_id": r["variant_id"]}
        if data.get("errors") or v is None:
            res["outcome"] = f"no variant returned: {data.get('errors')}"
            fails.append(res)
            out.append(res)
            continue
        diff = {}
        for t in ("exome", "genome"):
            got = v.get(t)
            if (got is not None) != r[f"{t}_present"]:
                diff[f"{t}_present"] = [r[f"{t}_present"], got is not None]
                continue
            if got is None:
                continue
            for k in ("ac", "an"):
                if got[k] != r[f"{t}_{k}"]:
                    diff[f"{t}_{k}"] = [r[f"{t}_{k}"], got[k]]
            held = set((r[f"{t}_filters"] or "").split(",")) - {""}
            if set(got["filters"] or []) != held:
                diff[f"{t}_filters"] = [sorted(held), sorted(got["filters"] or [])]
        j = v.get("joint")
        for k in ("ac", "an"):
            if (j or {}).get(k) != r[f"joint_{k}"]:
                diff[f"joint_{k}"] = [r[f"joint_{k}"], (j or {}).get(k)]
        res["outcome"] = "equal" if not diff else "differs"
        if diff:
            res["differences"] = diff
            if not release.get("post_says_variant_data_changed"):  # the only excuse; read from a later post, if any
                fails.append(res)
        out.append(res)
    return {"compared": out, "failures": fails, "release": release}
